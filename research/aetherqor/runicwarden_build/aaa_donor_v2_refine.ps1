param(
  [Parameter(Mandatory=$true)][string]$SourceRoot,
  [Parameter(Mandatory=$true)][string]$OutputRoot
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
if([string]::IsNullOrWhiteSpace($env:MESHY_API_KEY)){ throw 'MESHY_API_KEY missing.' }

$Api='https://api.meshy.ai'
$H=@{Authorization="Bearer $($env:MESHY_API_KEY)";'Content-Type'='application/json'}
function Call([string]$Method,[string]$Path,$Body=$null){
  $u="$Api$Path"
  if($null -eq $Body){ return Invoke-RestMethod -Method $Method -Uri $u -Headers $H -TimeoutSec 180 }
  return Invoke-RestMethod -Method $Method -Uri $u -Headers $H -Body ($Body|ConvertTo-Json -Depth 12 -Compress) -TimeoutSec 180
}
function WaitTask([string]$Path,[string]$Id,[int]$TimeoutSec=5400){
  $deadline=(Get-Date).AddSeconds($TimeoutSec)
  while((Get-Date)-lt $deadline){
    $t=Call 'GET' "$Path/$Id"
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] $Id status=$($t.status) progress=$($t.progress)"
    if($t.status -eq 'SUCCEEDED'){ return $t }
    if($t.status -in @('FAILED','CANCELED')){ throw "Meshy task $Id failed: $($t.task_error.message)" }
    Start-Sleep -Seconds 8
  }
  throw "Meshy timeout $Id"
}
function DownloadFile([string]$Url,[string]$Path){ if($Url){ Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $Path -TimeoutSec 600 } }

$srcReport=Join-Path $SourceRoot 'reports\image_task.json'
if(-not (Test-Path -LiteralPath $srcReport)){ throw "Missing source image report: $srcReport" }
$src=Get-Content -LiteralPath $srcReport -Raw | ConvertFrom-Json
$refs=@($src.image_urls)
if($refs.Count -lt 3){ throw "Need >=3 coherent source views, got $($refs.Count)" }

$balance=(Call 'GET' '/openapi/v1/balance').balance
Write-Host "MESHY_BALANCE_START=$balance"
if([int]$balance -lt 60){ throw "Refusing V2 donor run: balance too low ($balance)." }

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null
$imgDir=Join-Path $OutputRoot 'multiview'; $modelDir=Join-Path $OutputRoot 'model'; $repDir=Join-Path $OutputRoot 'reports'
New-Item -ItemType Directory -Force -Path $imgDir,$modelDir,$repDir | Out-Null

$prompt=@'
REFINE THIS SAME EXISTING RUNIC WARDEN CHARACTER. Do not redesign into another class and do not change body proportions or A-pose. Raise the result to premium hero-character quality for a high-end mobile dark-fantasy RPG.

MANDATORY silhouette and identity corrections:
- stronger recognizable RUNIC WARDEN identity at first glance
- fitted forged dark-iron cuirass with deliberate old-gold/brass rune channels, layered articulated abdomen and clean modular seams
- helmet must become a premium signature piece: compact knight/warden helm with a strong vertical rune crest and readable face/visor construction; no bucket shape, no giant horns, no oversized crown
- pauldrons restrained and anatomical, extending only slightly beyond shoulder width; no wings and no floating plates
- shield medium-sized, sturdy and geometric, with a clear engraved runic ward emblem; reduce organic/ornamental swirl; practical combat thickness and grip
- sword elegant runic longsword, straight readable blade, premium guard, not oversized
- greaves, boots and gauntlets must read as engineered armor, not melted metal
- short controlled back mantle only; legs fully readable from front/side/back
- no exposed torso/waist gaps, no underwear visible, no random skin patches; only face/neck/hands where intentional
- no floating geometry, no fused limbs, no pedestal, no jewelry, no extra props

MATERIAL / ART DIRECTION:
blackened forged iron, gunmetal steel, restrained aged brass/old gold, subtle warm amber-white runes only, ZERO blue. Realistic PBR, believable edge wear, micro-scratches, leather/cloth only at joints. Premium contrast and material separation without noisy decoration.

TURNAROUND REQUIREMENTS:
exact same character in every view, full body head-to-boots, clean symmetrical A-pose, centered, unobstructed silhouette, neutral studio lighting, consistent weapon/shield placement, production concept turnaround suitable for high-fidelity 3D reconstruction.
'@

Write-Host 'STEP 1: refine coherent donor views, preserving same character'
$ic=Call 'POST' '/openapi/v1/image-to-image' @{ ai_model='gpt-image-2'; prompt=$prompt; reference_image_urls=$refs; generate_multi_view=$true; remove_background=$true }
$img=WaitTask '/openapi/v1/image-to-image' $ic.result 1800
$img|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $repDir 'image_task.json') -Encoding UTF8
$i=0
foreach($u in @($img.image_urls)){ DownloadFile $u (Join-Path $imgDir ("view_{0:D2}.png" -f $i)); $i++ }
if($i -lt 3){ throw "Expected >=3 refined views, got $i" }

Write-Host 'STEP 2: Meshy Ultra V2 donor from refined multiview'
$mc=Call 'POST' '/openapi/v1/multi-image-to-3d' @{
  input_task_id=$img.id
  ai_model='latest'
  ultra_mode=$true
  should_texture=$true
  enable_pbr=$true
  should_remesh=$false
  pose_mode='a-pose'
  image_enhancement=$true
  remove_lighting=$true
  target_formats=@('glb','fbx')
  auto_size=$true
  origin_at='bottom'
  alpha_thumbnail=$true
  multi_view_thumbnails=$true
}
$model=WaitTask '/openapi/v1/multi-image-to-3d' $mc.result 5400
$model|ConvertTo-Json -Depth 16|Set-Content -LiteralPath (Join-Path $repDir 'model_task.json') -Encoding UTF8
DownloadFile $model.model_urls.glb (Join-Path $modelDir 'RunicWarden_AAA_Donor_V2.glb')
DownloadFile $model.model_urls.fbx (Join-Path $modelDir 'RunicWarden_AAA_Donor_V2.fbx')
if($model.thumbnail_url){ DownloadFile $model.thumbnail_url (Join-Path $modelDir 'thumb_front.png') }
if($model.alpha_thumbnail_url){ DownloadFile $model.alpha_thumbnail_url (Join-Path $modelDir 'thumb_alpha.png') }
if($model.thumbnail_urls){ foreach($p in $model.thumbnail_urls.PSObject.Properties){ if($p.Value){ DownloadFile ([string]$p.Value) (Join-Path $modelDir ("thumb_{0}.png" -f $p.Name)) } } }

$end=(Call 'GET' '/openapi/v1/balance').balance
[ordered]@{
  status='V2_VISUAL_GATE_REQUIRED_DO_NOT_RIG_YET'
  source=$SourceRoot
  balance_start=$balance
  balance_end=$end
  image_task=$img.id
  model_task=$model.id
  image_credits=$img.consumed_credits
  model_credits=$model.consumed_credits
  next='Visual QA front/right/back/left. Only PASS_STRONG may proceed to rig/modularization.'
}|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $repDir 'SUMMARY.json') -Encoding UTF8
Write-Host "AAA_DONOR_V2_DONE balance_end=$end"
