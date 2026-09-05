[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$Source,
  [Parameter(Mandatory=$true)][double]$Start,
  [Parameter(Mandatory=$true)][double]$End,
  [Parameter(Mandatory=$true)][string]$OutputDir,
  [int]$Fps = 24,
  [int]$MaxHeight = 1080
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if($End -le $Start){ throw 'End must be greater than Start' }
$ffmpeg=(Get-Command ffmpeg -ErrorAction Stop).Source
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
$frames=Join-Path $OutputDir 'frames'
$sheets=Join-Path $OutputDir 'sheets_4x4'
New-Item -ItemType Directory -Path $frames,$sheets -Force | Out-Null
$dur=$End-$Start
$startInv=$Start.ToString([Globalization.CultureInfo]::InvariantCulture)
$durInv=$dur.ToString([Globalization.CultureInfo]::InvariantCulture)
& $ffmpeg -hide_banner -loglevel warning -y -ss $startInv -t $durInv -i $Source -vf "fps=$Fps,scale=-2:$MaxHeight" -q:v 3 (Join-Path $frames 'frame_%07d.jpg')
if($LASTEXITCODE -ne 0){ throw 'Micro frame extraction failed' }
$count=@(Get-ChildItem $frames -Filter 'frame_*.jpg' -File).Count
$csv=New-Object System.Collections.Generic.List[string]
$csv.Add('frame,absolute_second,timecode')
for($i=0;$i -lt $count;$i++){
  $sec=$Start+($i/[double]$Fps)
  $ts=[TimeSpan]::FromSeconds($sec)
  $tc=('{0:00}:{1:00}:{2:00}.{3:000}' -f [int]$ts.TotalHours,$ts.Minutes,$ts.Seconds,$ts.Milliseconds)
  $csv.Add(('"frame_{0:0000000}.jpg",{1},"{2}"' -f ($i+1),$sec.ToString([Globalization.CultureInfo]::InvariantCulture),$tc))
}
$csv | Set-Content (Join-Path $OutputDir 'micro_index.csv') -Encoding UTF8
& $ffmpeg -hide_banner -loglevel warning -y -framerate $Fps -start_number 1 -i (Join-Path $frames 'frame_%07d.jpg') -vf "scale=960:-2,tile=4x4:nb_frames=16:padding=4:margin=4" -fps_mode vfr -q:v 2 (Join-Path $sheets 'sheet_%05d.jpg')
if($LASTEXITCODE -ne 0){ throw 'Micro contact sheet generation failed' }
@(
  "source=$Source",
  "start=$Start",
  "end=$End",
  "fps=$Fps",
  "frames=$count",
  "created_utc=$([DateTime]::UtcNow.ToString('o'))"
) | Set-Content (Join-Path $OutputDir '_MICRO_DONE.txt') -Encoding UTF8
Write-Host "FLYCAT_MICRO_READY start=$Start end=$End fps=$Fps frames=$count out=$OutputDir"
