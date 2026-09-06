param(
  [Parameter(Mandatory=$true)][string]$SourceV2Root,
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
  return Invoke-RestMethod -Method $Method -Uri $u -Headers $H -Body ($Body|ConvertTo-Json -Depth 16 -Compress) -TimeoutSec 180
}
function WaitTask([string]$Path,[string]$Id,[int]$TimeoutSec=2400){
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
function DownloadFile([string]$Url,[string]$Path){
  if([string]::IsNullOrWhiteSpace($Url)){ return }
  Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $Path -TimeoutSec 600
}

$srcReport=Join-Path $SourceV2Root 'reports\image_task.json'
if(-not (Test-Path -LiteralPath $srcReport)){ throw "Missing V2 image task report: $srcReport" }
$src=Get-Content -LiteralPath $srcReport -Raw | ConvertFrom-Json
$refs=@($src.image_urls)
if($refs.Count -lt 3){ throw "Need >=3 coherent V2 references, got $($refs.Count)" }

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null
$conceptRoot=Join-Path $OutputRoot 'concepts'; $reportRoot=Join-Path $OutputRoot 'reports'
New-Item -ItemType Directory -Force -Path $conceptRoot,$reportRoot | Out-Null

$balanceStart=[int](Call 'GET' '/openapi/v1/balance').balance
Write-Host "MESHY_BALANCE_START=$balanceStart"
if($balanceStart -lt 300){ throw "Refusing V3 concept generation: balance too low ($balanceStart)." }

$global=@'
Use the supplied Runic Warden V2 turnaround only as the exact ART-DIRECTION and design-language reference. We are rebuilding this hero as a genuinely modular AAA game character. Generate ONLY the requested removable equipment item, isolated as a clean production asset turnaround.

ABSOLUTE RULES:
- exact same Runic Warden visual language across every slot
- blackened forged iron / gunmetal steel, restrained aged brass / old gold rune channels, subtle warm amber-white rune glow only
- ZERO blue, ZERO cyan, no bright fantasy neon
- realistic premium PBR-ready surfaces, believable thickness, engineered seams, edge wear, leather only where mechanically required
- no body, no mannequin, no skin, no hands, no feet, no head, no unrelated armor pieces, no pedestal, no floor, no extra props
- no melted forms, no floating fragments, no asymmetrical corruption
- neutral studio lighting, transparent/clean background, full object visible with generous margins
- same object in every generated view, consistent proportions and construction
- intended for high-end mobile dark-fantasy RPG comparable in finish/readability to Black Desert Mobile hero gear
- clean modular boundaries so the piece can be equipped/unequipped independently
'@

$slotPrompts=[ordered]@{
  Helmet='ONLY the signature Runic Warden helmet. Compact close-fitting knight/warden helm, strong vertical rune crest, articulated cheek/visor construction, complete back of helmet, neck clearance, no horns, no giant crown, no hair, no head. Premium readable silhouette.'
  Chest='ONLY the torso armor shell. Fitted forged cuirass covering upper torso and abdomen, segmented articulated abdomen, protected collar line, deliberate old-gold rune channels, clean arm/neck/waist openings, no pauldrons, no arms, no belt, no cape. It must read as one wearable chest slot.'
  Shoulders='ONLY a matched LEFT+RIGHT pair of restrained anatomical pauldrons as one asset set. Slightly beyond shoulder width only, layered practical plates, clear underside/attachment geometry, no wings, no giant spikes, no chest armor, no arms.'
  Gloves='ONLY a matched LEFT+RIGHT pair of armored gauntlets as one asset set. Full wrist-to-fingertip engineered gauntlets, articulated finger plates, practical cuff, no human hands/skin, no forearms beyond the glove cuff.'
  Belt='ONLY the removable belt + faulds/tassets slot. Structured armored waist belt with central Runic Warden clasp/relic mount and controlled front/side tassets. No torso, no legs, no underwear, no giant skirt, no cape. Must leave hip articulation readable.'
  Legs='ONLY a matched LEFT+RIGHT leg armor set from upper thigh to lower shin, including cuisses/poleyn/knee articulation but EXCLUDING boots. No pelvis/body, no feet. Practical mobile-combat proportions, clean top and ankle openings.'
  Boots='ONLY a matched LEFT+RIGHT pair of armored boots/sabatons as one asset set. Complete foot/ankle construction with practical sole and ankle articulation, no bare feet/skin, no greaves extending to knee.'
  Cloak='ONLY the short controlled Runic Warden back mantle/cape. Shoulder attachment edge plus cloth falling to around knee/calf, narrow enough to preserve leg readability, dark charcoal cloth with restrained reinforced trim, no body, no armor, no gigantic skirt, no floor.'
  Sword='ONLY the Runic Warden Oathblade longsword. Straight readable blade, premium practical guard, wrapped grip, pommel, subtle engraved old-gold rune channel, combat-realistic proportions, no hand, no scabbard, no shield.'
  Shield='ONLY the Runic Warden Aegis shield. Medium-sized sturdy geometric shield, practical thickness, rear grip/strap construction included, engraved central runic ward emblem, blackened steel with restrained old-gold accents, no organic swirl, no arm/hand.'
  ClassRelic='ONLY the removable Runic Warden class relic as a compact armor-mounted ward plate / rune focus, designed to mount at the belt or chest socket. It is NOT jewelry, NOT a necklace, NOT a ring. Palm-sized forged-metal emblem with a strong rune identity and clear mounting back.'
}

$summary=[ordered]@{status='CONCEPT_GATE_PENDING'; source_v2=$SourceV2Root; balance_start=$balanceStart; generated=@(); reused=@(); failed=@()}
foreach($slot in $slotPrompts.Keys){
  $dir=Join-Path $conceptRoot $slot; $rep=Join-Path $reportRoot ("{0}_image_task.json" -f $slot)
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  $existing=@(Get-ChildItem -LiteralPath $dir -File -Filter 'view_*.png' -ErrorAction SilentlyContinue)
  if((Test-Path -LiteralPath $rep) -and $existing.Count -ge 3){
    Write-Host "REUSE concept $slot ($($existing.Count) views)"
    $summary.reused += $slot
    continue
  }
  $prompt=$global+"`n`nREQUESTED SLOT:`n"+$slotPrompts[$slot]+"`n`nGenerate a coherent multi-view product turnaround of this single slot now."
  Write-Host "GENERATE concept $slot"
  try{
    $c=Call 'POST' '/openapi/v1/image-to-image' @{ai_model='gpt-image-2';prompt=$prompt;reference_image_urls=$refs;generate_multi_view=$true;remove_background=$true}
    $task=WaitTask '/openapi/v1/image-to-image' $c.result 2400
    $task|ConvertTo-Json -Depth 16|Set-Content -LiteralPath $rep -Encoding UTF8
    $i=0
    foreach($u in @($task.image_urls)){
      if($u){ DownloadFile ([string]$u) (Join-Path $dir ("view_{0:D2}.png" -f $i)); $i++ }
    }
    if($i -lt 3){ throw "Concept $slot returned only $i views" }
    $summary.generated += $slot
    Write-Host "CONCEPT_DONE $slot views=$i credits=$($task.consumed_credits)"
  }catch{
    $summary.failed += [ordered]@{slot=$slot;error=$_.Exception.Message}
    $summary|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $reportRoot 'CONCEPT_SUMMARY.json') -Encoding UTF8
    throw
  }
}
$balanceEnd=[int](Call 'GET' '/openapi/v1/balance').balance
$summary.balance_end=$balanceEnd
$summary.credits_used=$balanceStart-$balanceEnd
$summary.next='VISUAL QA ONLY. Do not generate 3D until all 11 slot turnarounds pass coherence, isolation, premium quality and exact Runic Warden style.'
$summary|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $reportRoot 'CONCEPT_SUMMARY.json') -Encoding UTF8
Write-Host "MODULAR_V3_CONCEPTS_DONE credits_used=$($balanceStart-$balanceEnd) balance_end=$balanceEnd"
