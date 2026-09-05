param(
  [Parameter(Mandatory=$true)][string]$OutputRoot
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
if([string]::IsNullOrWhiteSpace($env:MESHY_API_KEY)){ throw 'MESHY_API_KEY missing.' }

$Api='https://api.meshy.ai'
$H=@{Authorization="Bearer $($env:MESHY_API_KEY)";'Content-Type'='application/json'}
New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null
$imgDir=Join-Path $OutputRoot 'multiview'; $modelDir=Join-Path $OutputRoot 'model'; $repDir=Join-Path $OutputRoot 'reports'
New-Item -ItemType Directory -Force -Path $imgDir,$modelDir,$repDir | Out-Null

function Call([string]$Method,[string]$Path,$Body=$null){
  $u="$Api$Path"
  if($null -eq $Body){ return Invoke-RestMethod -Method $Method -Uri $u -Headers $H -TimeoutSec 180 }
  return Invoke-RestMethod -Method $Method -Uri $u -Headers $H -Body ($Body|ConvertTo-Json -Depth 12 -Compress) -TimeoutSec 180
}
function WaitTask([string]$Path,[string]$Id,[int]$TimeoutSec=3600){
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

$balance=(Call 'GET' '/openapi/v1/balance').balance
Write-Host "MESHY_BALANCE_START=$balance"
if([int]$balance -lt 70){ throw "Refusing AAA donor run: Meshy balance too low ($balance). Need >=70." }

$bodyRef='https://d2ol7oe51mr4n9.cloudfront.net/user_3GIsPqjyHCX7dwJRn8e5M98bAE1/2d61f29f-b06b-4698-8f30-0207f4ec80f2.png'
$prompt=@'
KEEP the exact adult male body proportions, head size, limb lengths and clean symmetrical A-pose from the reference. Transform him into an ORIGINAL premium AAA dark-fantasy RUNIC WARDEN hero suitable for a high-end mobile RPG at Black Desert Mobile visual quality, but do not copy any copyrighted costume. Full body, head to boots, unobstructed silhouette, same character in all views. Practical modular knight armor with clearly readable separate equipment seams: fitted dark forged iron cuirass, articulated abdomen, restrained medium pauldrons (NO giant shoulder wings), fitted gauntlets, segmented belt/faulds, armored trousers and greaves, solid armored boots, short controlled back mantle/cape that does not hide the legs, one runic longsword and one medium aegis shield. Dark iron + gunmetal + restrained aged brass/old gold, subtle warm amber-white runes only, ZERO blue. Realistic PBR materials, believable metal thickness, leather undersuit at joints, no exposed random skin gaps except face/neck/hands where appropriate, no floating pieces, no spikes through body, no pedestal, no giant skirt, no oversized cloak, no extra limbs, no jewelry, no text, no logo. Neutral studio lighting, production character turnaround, consistent design from every angle, game-ready proportions.
'@

Write-Host 'STEP 1: Meshy image-to-image multi-view AAA design from body reference'
$ic=Call 'POST' '/openapi/v1/image-to-image' @{ ai_model='gpt-image-2'; prompt=$prompt; reference_image_urls=@($bodyRef); generate_multi_view=$true; remove_background=$true }
$img=WaitTask '/openapi/v1/image-to-image' $ic.result 1800
$img|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $repDir 'image_task.json') -Encoding UTF8
$i=0
foreach($u in @($img.image_urls)){ DownloadFile $u (Join-Path $imgDir ("view_{0:D2}.png" -f $i)); $i++ }
if($i -lt 3){ throw "Expected 3 multi-view images, got $i" }

Write-Host 'STEP 2: Meshy 7 Ultra multi-image-to-3D, no remesh for maximum source fidelity'
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
DownloadFile $model.model_urls.glb (Join-Path $modelDir 'RunicWarden_AAA_Donor_Source.glb')
DownloadFile $model.model_urls.fbx (Join-Path $modelDir 'RunicWarden_AAA_Donor_Source.fbx')
if($model.thumbnail_url){ DownloadFile $model.thumbnail_url (Join-Path $modelDir 'thumb_front.png') }
if($model.alpha_thumbnail_url){ DownloadFile $model.alpha_thumbnail_url (Join-Path $modelDir 'thumb_alpha.png') }
if($model.thumbnail_urls){
  foreach($p in $model.thumbnail_urls.PSObject.Properties){ if($p.Value){ DownloadFile ([string]$p.Value) (Join-Path $modelDir ("thumb_{0}.png" -f $p.Name)) } }
}

$end=(Call 'GET' '/openapi/v1/balance').balance
$summary=[ordered]@{
  status='AAA_DONOR_GENERATED_VISUAL_GATE_REQUIRED'
  balance_start=$balance
  balance_end=$end
  image_task=$img.id
  model_task=$model.id
  image_credits=$img.consumed_credits
  model_credits=$model.consumed_credits
  files=@('model/RunicWarden_AAA_Donor_Source.glb','model/RunicWarden_AAA_Donor_Source.fbx')
  next='DO NOT RIG OR MODULARIZE until visual QA passes front/right/back/left thumbnails.'
}
$summary|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $repDir 'SUMMARY.json') -Encoding UTF8
Write-Host "AAA_DONOR_DONE balance_end=$end"
