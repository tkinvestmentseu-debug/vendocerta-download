[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Url,
    [Parameter(Mandatory=$true)][string]$Slug,
    [Parameter(Mandatory=$true)][string]$Topic,
    [string]$Browser = "chrome",
    [string]$OutputRoot = "$env:RUNNER_TEMP\aetherqor-video",
    [int]$FrameFps = 1,
    [int]$HighDetailFps = 4,
    [int]$MaxHeight = 1080,
    [int]$HighDetailMaxSeconds = 360
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

function Resolve-Executable([string]$Name, [string[]]$Fallbacks) {
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    foreach ($candidate in $Fallbacks) {
        if ($candidate -and (Test-Path $candidate)) { return $candidate }
    }
    throw "Required executable not found: $Name"
}

function Format-Timecode([double]$Seconds) {
    if ($Seconds -lt 0) { $Seconds = 0 }
    $ts = [TimeSpan]::FromSeconds($Seconds)
    return ('{0:00}:{1:00}:{2:00}.{3:000}' -f [int]$ts.TotalHours, $ts.Minutes, $ts.Seconds, $ts.Milliseconds)
}

function Convert-VttToText([string]$InputFile, [string]$OutputFile) {
    $out = New-Object System.Collections.Generic.List[string]
    $prev = ""
    foreach ($raw in Get-Content -Path $InputFile -Encoding UTF8) {
        $line = $raw.Trim()
        if (-not $line) { continue }
        if ($line -eq "WEBVTT") { continue }
        if ($line -match '^(Kind|Language):') { continue }
        if ($line -match '^NOTE') { continue }
        if ($line -match '-->') { continue }
        if ($line -match '^\d+$') { continue }
        $line = $line -replace '<[^>]+>', ''
        $line = [System.Net.WebUtility]::HtmlDecode($line).Trim()
        if (-not $line) { continue }
        if ($line -eq $prev) { continue }
        $out.Add($line)
        $prev = $line
    }
    $out | Set-Content -Path $OutputFile -Encoding UTF8
}

$runnerRoot = if ($env:AETHERQOR_RUNNER_ROOT) { $env:AETHERQOR_RUNNER_ROOT } else { "C:\AETHERQOR_GitHubRunner" }
if(-not (Test-Path $runnerRoot)) { $runnerRoot = "$env:LOCALAPPDATA\AETHERQOR_GitHubRunner" }
$toolsRoot = if ($env:AETHERQOR_TOOLS) { $env:AETHERQOR_TOOLS } else { Join-Path $runnerRoot "tools" }
$yt = Resolve-Executable "yt-dlp" @((Join-Path $toolsRoot "yt-dlp\yt-dlp.exe"))
$ffmpeg = Resolve-Executable "ffmpeg" @((Join-Path $toolsRoot "ffmpeg\bin\ffmpeg.exe"))
$ffprobe = Resolve-Executable "ffprobe" @((Join-Path $toolsRoot "ffmpeg\bin\ffprobe.exe"))

$outDir = Join-Path $OutputRoot $Slug
$framesDir = Join-Path $outDir "frames_1fps"
$sheetsDir = Join-Path $outDir "contact_sheets_3x3"
$highDir = Join-Path $outDir "high_detail_4fps"
$logsDir = Join-Path $outDir "logs"
New-Item -ItemType Directory -Path $outDir,$framesDir,$sheetsDir,$highDir,$logsDir -Force | Out-Null

# Chrome-only browser policy. Edge/Firefox are never used.
$cookieSpec = "chrome"
$cookieSpecFile = Join-Path $runnerRoot "chrome-cookie-spec.txt"
if(Test-Path $cookieSpecFile) {
    $saved = (Get-Content $cookieSpecFile -First 1).Trim()
    if($saved) { $cookieSpec = $saved }
}

# VIDEO is mandatory. Subtitles are deliberately NOT part of this command,
# so a 429 on captions can never abort the MP4 download.
$downloadOk = $false
$downloadMode = ""
$format = "bv*[height<=$MaxHeight]+ba/b[height<=$MaxHeight]"
$attempts = @(
    @{ Name = $cookieSpec; UseCookies = $true },
    @{ Name = "chrome-local-ip-no-cookies"; UseCookies = $false }
)
foreach ($attempt in $attempts) {
    $safeName = ($attempt.Name -replace '[^A-Za-z0-9_-]+','_')
    $attemptLog = Join-Path $logsDir ("yt-dlp-video-{0}.log" -f $safeName)
    $args = @(
        '--no-playlist',
        '--write-info-json',
        '--merge-output-format','mp4',
        '-f',$format,
        '-o',(Join-Path $outDir 'source.%(ext)s')
    )
    if ($attempt.UseCookies) { $args += @('--cookies-from-browser',$cookieSpec) }
    $args += $Url

    "VIDEO_ATTEMPT=$($attempt.Name)" | Set-Content -Path $attemptLog -Encoding UTF8
    & $yt @args *>> $attemptLog
    $code = $LASTEXITCODE
    if ($code -eq 0) {
        $downloadOk = $true
        $downloadMode = $attempt.Name
        break
    }
}
if (-not $downloadOk) {
    throw "yt-dlp could not download VIDEO $Url using Chrome or local-IP no-cookie mode. See $logsDir"
}

$source = Get-ChildItem -Path $outDir -File | Where-Object {
    $_.BaseName -eq 'source' -and $_.Extension -match '^\.(mp4|mkv|webm|mov)$'
} | Sort-Object Length -Descending | Select-Object -First 1
if (-not $source) { throw "Video source file was not produced despite yt-dlp exit code 0." }

# Captions are best-effort and separate from the video. English only to avoid
# YouTube translation-caption rate limiting (the prior PL request returned HTTP 429).
$subLog = Join-Path $logsDir 'yt-dlp-subtitles-best-effort.log'
$subArgs = @(
    '--no-playlist',
    '--skip-download',
    '--write-auto-subs',
    '--write-subs',
    '--sub-langs','en.*,en',
    '--sub-format','vtt',
    '-o',(Join-Path $outDir 'source.%(ext)s')
)
if ($downloadMode -ne 'chrome-local-ip-no-cookies') {
    $subArgs += @('--cookies-from-browser',$cookieSpec)
}
$subArgs += $Url
"SUBTITLE_ATTEMPT_MODE=$downloadMode" | Set-Content -Path $subLog -Encoding UTF8
& $yt @subArgs *>> $subLog
$subtitleExitCode = $LASTEXITCODE
if ($subtitleExitCode -ne 0) {
    "Subtitle download failed with exit code $subtitleExitCode. Video processing continues." | Add-Content -Path $subLog -Encoding UTF8
}

$infoFile = Get-ChildItem -Path $outDir -Filter '*.info.json' -File | Select-Object -First 1
$info = $null
if ($infoFile) { $info = Get-Content $infoFile.FullName -Raw -Encoding UTF8 | ConvertFrom-Json }

$durationText = (& $ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $source.FullName | Select-Object -First 1)
if ($LASTEXITCODE -ne 0 -or -not $durationText) { throw "ffprobe could not read source video." }
$durationText | Set-Content (Join-Path $outDir 'duration_seconds.txt') -Encoding ASCII

# Full-resolution frame every second.
$frameLog = Join-Path $logsDir "ffmpeg-frames.log"
& $ffmpeg -hide_banner -loglevel warning -i $source.FullName -vf "fps=$FrameFps" -q:v 2 (Join-Path $framesDir 'frame_%06d.jpg') *>> $frameLog
if ($LASTEXITCODE -ne 0) { throw "FFmpeg 1fps extraction failed." }

$frameFiles = Get-ChildItem -Path $framesDir -Filter 'frame_*.jpg' -File | Sort-Object Name
if ($frameFiles.Count -eq 0) { throw "FFmpeg created zero 1fps frames." }
$frameCsv = New-Object System.Collections.Generic.List[string]
$frameCsv.Add('frame,second,timecode')
for ($i=0; $i -lt $frameFiles.Count; $i++) {
    $sec = $i / [double]$FrameFps
    $frameCsv.Add(('"{0}",{1},"{2}"' -f $frameFiles[$i].Name, $sec.ToString([Globalization.CultureInfo]::InvariantCulture), (Format-Timecode $sec)))
}
$frameCsv | Set-Content -Path (Join-Path $outDir 'frame_index.csv') -Encoding UTF8

# 3x3 review sheets. Individual 1fps frames stay full resolution; sheets use
# 960px-wide cells so UI remains readable without producing gigantic artifacts.
$sheetLog = Join-Path $logsDir "ffmpeg-sheets.log"
& $ffmpeg -hide_banner -loglevel warning -framerate $FrameFps -start_number 1 -i (Join-Path $framesDir 'frame_%06d.jpg') -vf "scale=960:-2,tile=3x3:nb_frames=9:padding=4:margin=4" -fps_mode vfr -q:v 2 (Join-Path $sheetsDir 'sheet_%05d.jpg') *>> $sheetLog
if ($LASTEXITCODE -ne 0) { throw "FFmpeg contact-sheet generation failed." }

$sheetFiles = Get-ChildItem -Path $sheetsDir -Filter 'sheet_*.jpg' -File | Sort-Object Name
$sheetCsv = New-Object System.Collections.Generic.List[string]
$sheetCsv.Add('sheet,start_second,end_second,start_timecode,end_timecode')
for ($i=0; $i -lt $sheetFiles.Count; $i++) {
    $start = $i * 9 / [double]$FrameFps
    $end = [Math]::Min((($i + 1) * 9 - 1) / [double]$FrameFps, [Math]::Max(0,($frameFiles.Count-1)/[double]$FrameFps))
    $sheetCsv.Add(('"{0}",{1},{2},"{3}","{4}"' -f $sheetFiles[$i].Name,$start,$end,(Format-Timecode $start),(Format-Timecode $end)))
}
$sheetCsv | Set-Content -Path (Join-Path $outDir 'sheet_index.csv') -Encoding UTF8

# Transcript from available English VTT.
$transcriptFiles = Get-ChildItem -Path $outDir -Filter '*.vtt' -File
$selectedTranscript = $null
if ($transcriptFiles.Count -gt 0) {
    $selectedTranscript = $transcriptFiles | Sort-Object @{Expression={ if ($_.Name -match '\.en-orig\.vtt$') {0} elseif ($_.Name -match '\.en\.vtt$') {1} elseif ($_.Name -match '\.en') {2} else {3} }}, Name | Select-Object -First 1
    Convert-VttToText $selectedTranscript.FullName (Join-Path $outDir 'transcript.txt')
    $selectedTranscript.Name | Set-Content -Path (Join-Path $outDir 'transcript_source.txt') -Encoding UTF8
} else {
    "No English YouTube subtitles were available. Video frames remain complete." | Set-Content -Path (Join-Path $outDir 'TRANSCRIPT_MISSING.txt') -Encoding UTF8
}

# Up to six minutes of 4fps detail from chapters whose titles look relevant.
$importantRegex = '(?i)hair|bang|bun|curve|armor|armour|retopo|topolog|eye|skin|cloth|gear|rig|vfx|mesh|geometry|uv|unwrap|bake|normal|material|shader|sculpt|accessor|plate|strap'
$remaining = $HighDetailMaxSeconds
$highCsv = New-Object System.Collections.Generic.List[string]
$highCsv.Add('segment,title,start_second,end_second,fps,frames')
$highFrameCount = 0
if ($info -and $remaining -gt 0 -and ($info.PSObject.Properties.Name -contains 'chapters') -and $info.chapters) {
    $segmentNo = 0
    foreach ($chapter in $info.chapters) {
        if ($remaining -le 0) { break }
        $title = [string]$chapter.title
        if ($title -notmatch $importantRegex) { continue }
        $start = [double]$chapter.start_time
        $end = [double]$chapter.end_time
        if ($end -le $start) { continue }
        $duration = [Math]::Min($end - $start, 90)
        $duration = [Math]::Min($duration, $remaining)
        if ($duration -lt 1) { continue }

        $segmentNo++
        $safe = ($title -replace '[^A-Za-z0-9_-]+','_').Trim('_')
        if ($safe.Length -gt 50) { $safe = $safe.Substring(0,50) }
        if (-not $safe) { $safe = "segment" }
        $segDir = Join-Path $highDir ('{0:00}_{1}' -f $segmentNo,$safe)
        New-Item -ItemType Directory -Path $segDir -Force | Out-Null
        $segLog = Join-Path $logsDir ('ffmpeg-high-{0:00}.log' -f $segmentNo)
        $startInvariant = $start.ToString([Globalization.CultureInfo]::InvariantCulture)
        $durationInvariant = $duration.ToString([Globalization.CultureInfo]::InvariantCulture)
        & $ffmpeg -hide_banner -loglevel warning -ss $startInvariant -t $durationInvariant -i $source.FullName -vf "fps=$HighDetailFps" -q:v 2 (Join-Path $segDir 'frame_%06d.jpg') *>> $segLog
        if ($LASTEXITCODE -eq 0) {
            $count = (Get-ChildItem -Path $segDir -Filter 'frame_*.jpg' -File).Count
            $highFrameCount += $count
            $highCsv.Add(('"{0}","{1}",{2},{3},{4},{5}' -f $segDir.Split([IO.Path]::DirectorySeparatorChar)[-1],($title -replace '"','""'),$start,($start+$duration),$HighDetailFps,$count))
            $remaining -= $duration
        }
    }
}
$highCsv | Set-Content -Path (Join-Path $outDir 'high_detail_index.csv') -Encoding UTF8

$titleValue = ""
$durationValue = 0
$uploaderValue = ""
if ($info) {
    if ($info.PSObject.Properties.Name -contains 'title') { $titleValue = [string]$info.title }
    if ($info.PSObject.Properties.Name -contains 'duration' -and $info.duration) { $durationValue = [double]$info.duration }
    if ($info.PSObject.Properties.Name -contains 'uploader') { $uploaderValue = [string]$info.uploader }
}
$manifest = [ordered]@{
    slug = $Slug
    url = $Url
    topic = $Topic
    title = $titleValue
    uploader = $uploaderValue
    duration_seconds = $durationValue
    download_mode = $downloadMode
    frame_fps = $FrameFps
    frame_count = $frameFiles.Count
    contact_sheet_count = $sheetFiles.Count
    high_detail_fps = $HighDetailFps
    high_detail_frame_count = $highFrameCount
    transcript = if ($selectedTranscript) { 'transcript.txt' } else { $null }
    subtitle_exit_code = $subtitleExitCode
    created_utc = [DateTime]::UtcNow.ToString('o')
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content -Path (Join-Path $outDir 'manifest.json') -Encoding UTF8

# Keep frames/transcript/metadata in the artifact, not the full downloaded movie.
if ($env:AETHERQOR_KEEP_SOURCE -ne '1') {
    Remove-Item $source.FullName -Force
}

Write-Host "AETHERQOR VIDEO COMPLETE: $Slug"
Write-Host "Frames: $($frameFiles.Count) | Sheets: $($sheetFiles.Count) | High-detail frames: $highFrameCount | Mode: $downloadMode"
