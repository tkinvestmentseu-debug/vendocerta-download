param(
  [Parameter(Mandatory=$true)][string]$OutputRoot,
  [Parameter(Mandatory=$true)][string]$BodyImageUrl
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

if ([string]::IsNullOrWhiteSpace($env:MESHY_API_KEY)) { throw 'MESHY_API_KEY is missing from runner environment.' }

$Api = 'https://api.meshy.ai'
$Headers = @{ Authorization = "Bearer $($env:MESHY_API_KEY)"; 'Content-Type' = 'application/json' }
New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null
$ModelsDir = Join-Path $OutputRoot 'models'
$ReportsDir = Join-Path $OutputRoot 'reports'
New-Item -ItemType Directory -Force -Path $ModelsDir,$ReportsDir | Out-Null

$Tasks = New-Object System.Collections.Generic.List[object]
$Start = Get-Date

function Write-Log([string]$m) {
  $line = "[$((Get-Date).ToString('HH:mm:ss'))] $m"
  Write-Host $line
  Add-Content -LiteralPath (Join-Path $ReportsDir 'build.log') -Value $line -Encoding UTF8
}

function Invoke-Meshy([string]$Method,[string]$Path,$Body=$null) {
  $uri = "$Api$Path"
  if ($null -eq $Body) { return Invoke-RestMethod -Method $Method -Uri $uri -Headers $Headers -TimeoutSec 120 }
  $json = $Body | ConvertTo-Json -Depth 10 -Compress
  return Invoke-RestMethod -Method $Method -Uri $uri -Headers $Headers -Body $json -TimeoutSec 120
}

function Wait-Task([string]$Path,[string]$Id,[int]$TimeoutSec=2400) {
  $deadline = (Get-Date).AddSeconds($TimeoutSec)
  while ((Get-Date) -lt $deadline) {
    $task = Invoke-Meshy 'GET' "$Path/$Id"
    Write-Host "  $Id status=$($task.status) progress=$($task.progress)"
    if ($task.status -eq 'SUCCEEDED') { return $task }
    if ($task.status -eq 'FAILED') { throw "Meshy task failed: $Id :: $($task.task_error.message)" }
    Start-Sleep -Seconds 6
  }
  throw "Meshy task timeout: $Id"
}

function Download-ModelUrls($Task,[string]$BaseName) {
  foreach ($ext in @('glb','fbx')) {
    $u = $Task.model_urls.$ext
    if ($u) {
      $dst = Join-Path $ModelsDir "$BaseName.$ext"
      Write-Log "Downloading $BaseName.$ext"
      Invoke-WebRequest -UseBasicParsing -Uri $u -OutFile $dst -TimeoutSec 300
    }
  }
}

function Add-TaskRecord([string]$Name,[string]$Phase,$Task) {
  $Tasks.Add([pscustomobject]@{
    name=$Name; phase=$Phase; id=$Task.id; status=$Task.status; consumed_credits=$Task.consumed_credits; finished_at=$Task.finished_at
  })
}

function Get-Balance {
  try { return [int](Invoke-Meshy 'GET' '/openapi/v1/balance').balance } catch { return -1 }
}

function New-ImageBody {
  Write-Log 'Creating BODY image-to-3D task.'
  $payload = @{
    image_url = $BodyImageUrl
    model_type = 'standard'
    ai_model = 'latest'
    should_texture = $true
    enable_pbr = $true
    texture_resolution = '4k'
    remove_lighting = $true
    image_enhancement = $false
    should_remesh = $true
    topology = 'quad'
    target_polycount = 60000
    pose_mode = 'a-pose'
    target_formats = @('glb','fbx')
  }
  $created = Invoke-Meshy 'POST' '/openapi/v1/image-to-3d' $payload
  $task = Wait-Task '/openapi/v1/image-to-3d' $created.result 3000
  Add-TaskRecord 'Body' 'image-to-3d' $task
  Download-ModelUrls $task 'Body_Base'

  # RIG = skeleton/armature for animation. This is mandatory.
  Write-Log 'Creating BODY RIGGING task.'
  $rigCreated = Invoke-Meshy 'POST' '/openapi/v1/rigging' @{ input_task_id=$task.id; height_meters=1.78 }
  $rig = Wait-Task '/openapi/v1/rigging' $rigCreated.result 1800
  Add-TaskRecord 'Body' 'rigging' $rig
  if ($rig.result.rigged_character_glb_url) {
    Invoke-WebRequest -UseBasicParsing -Uri $rig.result.rigged_character_glb_url -OutFile (Join-Path $ModelsDir 'Body_Rigged.glb') -TimeoutSec 300
  }
  if ($rig.result.rigged_character_fbx_url) {
    Invoke-WebRequest -UseBasicParsing -Uri $rig.result.rigged_character_fbx_url -OutFile (Join-Path $ModelsDir 'Body_Rigged.fbx') -TimeoutSec 300
  }
  foreach ($a in @('walking_glb_url','running_glb_url')) {
    $u = $rig.result.basic_animations.$a
    if ($u) { Invoke-WebRequest -UseBasicParsing -Uri $u -OutFile (Join-Path $ModelsDir ("Body_" + ($a -replace '_glb_url','') + '.glb')) -TimeoutSec 300 }
  }
}

function New-Gear([string]$Name,[int]$Poly,[string]$Prompt,[bool]$Refine=$true) {
  # REUSE BEFORE GENERATE: if the exact slot already exists in this production cache, do not spend credits again.
  $existingGlb = Join-Path $ModelsDir "$Name.glb"
  $existingFbx = Join-Path $ModelsDir "$Name.fbx"
  if ((Test-Path -LiteralPath $existingGlb) -or (Test-Path -LiteralPath $existingFbx)) {
    Write-Log "REUSE $Name: local generated model already exists."
    return
  }

  Write-Log "Creating $Name preview."
  $previewPayload = @{
    mode='preview'; model_type='standard'; ai_model='latest'; prompt=$Prompt; should_remesh=$true; topology='quad';
    target_polycount=$Poly; target_formats=@('glb','fbx'); auto_size=$false
  }
  $created = Invoke-Meshy 'POST' '/openapi/v2/text-to-3d' $previewPayload
  $preview = Wait-Task '/openapi/v2/text-to-3d' $created.result 2400
  Add-TaskRecord $Name 'preview' $preview
  if (-not $Refine) { Download-ModelUrls $preview $Name; return }

  Write-Log "Creating $Name refine/PBR."
  $refinePayload = @{
    mode='refine'; preview_task_id=$preview.id; enable_pbr=$true; texture_resolution='4k'; remove_lighting=$true;
    target_formats=@('glb','fbx')
  }
  $rcreated = Invoke-Meshy 'POST' '/openapi/v2/text-to-3d' $refinePayload
  $refined = Wait-Task '/openapi/v2/text-to-3d' $rcreated.result 2400
  Add-TaskRecord $Name 'refine' $refined
  Download-ModelUrls $refined $Name
}

$balanceStart = Get-Balance
Write-Log "Meshy balance at start: $balanceStart"

# Runic Warden art direction. No jewelry generation. RIGGING means armature/skeleton, not rings.
$common = 'Standalone wearable game asset for an athletic adult male 1.78m dark-fantasy Runic Warden. Realistic PBR, forged blackened iron, dark steel, restrained oxidized old-gold/brass trim, engraved geometric runes with subtle warm amber-white glow, premium battle-worn detail, clean silhouette, no blue, no text, no logo, no watermark, no body, no mannequin, centered at origin, front facing, production game asset.'

New-ImageBody

# COMPLETE GAMEPLAY GEAR ONLY. No Ring_L/R, necklace or bracelet.
$gear = @(
  @{N='Helmet'; P=2200; Q="$common Closed/open-face knight helmet, fitted human head proportions, strong brow, modest rune crest, neck clearance, no giant horns."},
  @{N='ChestArmor'; P=4200; Q="$common Rigid torso breastplate shell with front and back plates, open neck and armholes, fitted waist, layered abdominal plates, no body inside."},
  @{N='Shoulders'; P=2200; Q="$common Matching pair of moderate left and right shoulder pauldrons as two disconnected pieces, not oversized, articulated lower lames."},
  @{N='Gloves'; P=1800; Q="$common Matching pair of armored gauntlets as two disconnected pieces, open wrist cuffs, articulated fingers, practical proportions."},
  @{N='Belt'; P=1200; Q="$common Armored waist belt, oval human waist opening, segmented dark leather and metal, central runic clasp, no hanging body."},
  @{N='Legs'; P=3200; Q="$common Leg armor garment: fitted armored trousers/tassets covering pelvis and thighs to below knees, open waist and leg openings, symmetrical."},
  @{N='Boots'; P=1800; Q="$common Matching pair armored boots as two disconnected pieces, solid sole, clear heel and toe volume, shin guards, not slippers."},
  @{N='Cloak'; P=2200; Q="$common Heavy dark charcoal back cloak for a warrior, shoulder attachment points, split lower hem, subtle old-gold rune border, hanging vertically, no body."},
  @{N='Sword'; P=2400; Q="$common One-handed/hand-and-a-half runic longsword, straight forged blade, practical hilt and grip, warm amber rune engraving, isolated weapon."},
  @{N='Shield'; P=2600; Q="$common Medium runic knight shield, convex dark iron, reinforced old-gold rim, central geometric ward sigil, rear grip implied, isolated shield."},
  @{N='ClassRelic'; P=1200; Q="$common Compact Runic Warden class relic: palm-sized ward stone in forged dark metal cage, geometric rune, subtle warm amber-white energy, attachable to chest or belt."}
)

foreach ($g in $gear) {
  $bal = Get-Balance
  if ($bal -ge 0 -and $bal -lt 25) { throw "Meshy balance too low before $($g.N): $bal" }
  $refine = $true
  if ($bal -ge 0 -and $bal -lt 100 -and $g.N -eq 'ClassRelic') { $refine = $false }
  New-Gear $g.N $g.P $g.Q $refine
}

$balanceEnd = Get-Balance
$tasksPath = Join-Path $ReportsDir 'meshy_tasks.json'
$Tasks | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $tasksPath -Encoding UTF8
$summary = [ordered]@{
  started_at=$Start.ToUniversalTime().ToString('o'); finished_at=(Get-Date).ToUniversalTime().ToString('o');
  balance_start=$balanceStart; balance_end=$balanceEnd; total_recorded_credits=($Tasks | Measure-Object consumed_credits -Sum).Sum;
  model_count=(Get-ChildItem $ModelsDir -File -Filter '*.glb').Count; output_root=$OutputRoot;
  requirement='RIGGED_CHARACTER_WITH_MODULAR_GAMEPLAY_GEAR'; jewelry_generation=$false
}
$summary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $ReportsDir 'meshy_summary.json') -Encoding UTF8
Write-Log "DONE. Balance end=$balanceEnd; recorded credits=$($summary.total_recorded_credits); GLB count=$($summary.model_count)"
