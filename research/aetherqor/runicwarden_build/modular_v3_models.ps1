param(
  [Parameter(Mandatory=$true)][string]$MasterRoot
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
function DownloadFile([string]$Url,[string]$Path){ if($Url){ Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $Path -TimeoutSec 900 } }

$slots=@('Helmet','Chest','Shoulders','Gloves','Belt','Legs','Boots','Cloak','Sword','Shield','ClassRelic')
$modelRoot=Join-Path $MasterRoot 'models'; $reportRoot=Join-Path $MasterRoot 'reports'; $thumbRoot=Join-Path $MasterRoot 'model_thumbs'
New-Item -ItemType Directory -Force -Path $modelRoot,$reportRoot,$thumbRoot | Out-Null
$start=[int](Call 'GET' '/openapi/v1/balance').balance
Write-Host "MESHY_BALANCE_START=$start"
if($start -lt 600){ throw "Refusing V3 3D generation: balance too low ($start)." }
$summary=[ordered]@{status='MODEL_GATE_PENDING';balance_start=$start;generated=@();reused=@();failed=@()}
foreach($slot in $slots){
  $conceptRep=Join-Path $reportRoot ("{0}_image_task.json" -f $slot)
  if(-not (Test-Path -LiteralPath $conceptRep)){ throw "Missing concept report for $slot" }
  $concept=Get-Content -LiteralPath $conceptRep -Raw | ConvertFrom-Json
  if(-not $concept.id){ throw "Missing concept task id for $slot" }
  $dir=Join-Path $modelRoot $slot; $tdir=Join-Path $thumbRoot $slot; $rep=Join-Path $reportRoot ("{0}_model_task.json" -f $slot)
  New-Item -ItemType Directory -Force -Path $dir,$tdir | Out-Null
  $glb=Join-Path $dir ("{0}_source.glb" -f $slot); $fbx=Join-Path $dir ("{0}_source.fbx" -f $slot)
  if((Test-Path -LiteralPath $rep) -and (Test-Path -LiteralPath $glb) -and (Test-Path -LiteralPath $fbx)){
    Write-Host "REUSE 3D $slot"
    $summary.reused += $slot
    continue
  }
  Write-Host "GENERATE 3D $slot from concept task $($concept.id)"
  try{
    $c=Call 'POST' '/openapi/v1/multi-image-to-3d' @{
      input_task_id=$concept.id
      ai_model='latest'
      ultra_mode=$true
      should_texture=$true
      enable_pbr=$true
      should_remesh=$false
      image_enhancement=$true
      remove_lighting=$true
      target_formats=@('glb','fbx')
      auto_size=$true
      origin_at='bottom'
      alpha_thumbnail=$true
      multi_view_thumbnails=$true
    }
    $task=WaitTask '/openapi/v1/multi-image-to-3d' $c.result 5400
    $task|ConvertTo-Json -Depth 18|Set-Content -LiteralPath $rep -Encoding UTF8
    DownloadFile $task.model_urls.glb $glb
    DownloadFile $task.model_urls.fbx $fbx
    if(-not (Test-Path -LiteralPath $glb) -or (Get-Item -LiteralPath $glb).Length -lt 10000){ throw "Invalid GLB for $slot" }
    if($task.thumbnail_url){ DownloadFile ([string]$task.thumbnail_url) (Join-Path $tdir 'front.png') }
    if($task.alpha_thumbnail_url){ DownloadFile ([string]$task.alpha_thumbnail_url) (Join-Path $tdir 'alpha.png') }
    if($task.thumbnail_urls){ foreach($p in $task.thumbnail_urls.PSObject.Properties){ if($p.Value){ DownloadFile ([string]$p.Value) (Join-Path $tdir ("{0}.png" -f $p.Name)) } } }
    $summary.generated += $slot
    Write-Host "MODEL_DONE $slot credits=$($task.consumed_credits)"
  }catch{
    $summary.failed += [ordered]@{slot=$slot;error=$_.Exception.Message}
    $summary|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $reportRoot 'MODEL_SUMMARY.json') -Encoding UTF8
    throw
  }
}
$end=[int](Call 'GET' '/openapi/v1/balance').balance
$summary.balance_end=$end; $summary.credits_used=$start-$end
$summary.next='Inspect per-slot 3D thumbnails. Only clean isolated assets proceed to deterministic body fitting and rigging.'
$summary|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $reportRoot 'MODEL_SUMMARY.json') -Encoding UTF8
Write-Host "MODULAR_V3_MODELS_DONE credits_used=$($start-$end) balance_end=$end"
