[CmdletBinding()]
param(
    [string]$Repo = 'tkinvestmentseu-debug/vendocerta-download',
    [string]$RunnerRoot = 'C:\AETHERQOR_GitHubRunner',
    [switch]$NoAutoStart
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

function Step([string]$s){ Write-Host "`n=== $s ===" -ForegroundColor Cyan }
function Ok([string]$s){ Write-Host "[OK] $s" -ForegroundColor Green }
function Warn([string]$s){ Write-Host "[WARN] $s" -ForegroundColor Yellow }
function Download([string]$url,[string]$dst){
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
  Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $dst -Headers @{'User-Agent'='AETHERQOR-Setup'}
}
function Add-Path([string]$p){ if($env:PATH -notlike "*$p*"){ $env:PATH = "$p;$env:PATH" } }

$RepoUrl = "https://github.com/$Repo"
$YouTubeProbe = 'https://www.youtube.com/watch?v=3bw2SnKQhwA'

Step '0/9  Preparing folders'
try { New-Item -ItemType Directory -Force -Path $RunnerRoot | Out-Null }
catch { $RunnerRoot = Join-Path $env:LOCALAPPDATA 'AETHERQOR_GitHubRunner'; New-Item -ItemType Directory -Force -Path $RunnerRoot | Out-Null }
$Tools = Join-Path $RunnerRoot 'tools'
$GhDir = Join-Path $Tools 'gh'
$YtDir = Join-Path $Tools 'yt-dlp'
$FfDir = Join-Path $Tools 'ffmpeg\bin'
New-Item -ItemType Directory -Force -Path $Tools,$GhDir,$YtDir,$FfDir | Out-Null

Step '1/9  Installing GitHub CLI locally'
$gh = Get-Command gh -ErrorAction SilentlyContinue
if(-not $gh){
  $rel = Invoke-RestMethod -Headers @{'User-Agent'='AETHERQOR-Setup'} -Uri 'https://api.github.com/repos/cli/cli/releases/latest'
  $asset = $rel.assets | Where-Object { $_.name -match '^gh_.*_windows_amd64\.zip$' } | Select-Object -First 1
  if(-not $asset){ throw 'Could not find GitHub CLI Windows amd64 ZIP.' }
  $zip = Join-Path $env:TEMP $asset.name
  $tmp = Join-Path $env:TEMP 'aetherqor-gh'
  Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
  Download $asset.browser_download_url $zip
  Expand-Archive $zip $tmp -Force
  $ghExe = Get-ChildItem $tmp -Recurse -Filter gh.exe -File | Select-Object -First 1
  if(-not $ghExe){ throw 'gh.exe not found after extraction.' }
  Copy-Item $ghExe.FullName (Join-Path $GhDir 'gh.exe') -Force
  Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
  Remove-Item $zip -Force -ErrorAction SilentlyContinue
  $GhExe = Join-Path $GhDir 'gh.exe'
}else{ $GhExe = $gh.Source }
& $GhExe --version | Select-Object -First 1
Ok 'GitHub CLI ready'

Step '2/9  Authenticating GitHub through Chrome'
$authOk = $false
& $GhExe auth status -h github.com *> $null
if($LASTEXITCODE -eq 0){ $authOk = $true }
if(-not $authOk){
  Write-Host 'GitHub will open a browser login/device page. Use CHROME and approve the login.' -ForegroundColor Yellow
  & $GhExe auth login -h github.com -p https -w
  if($LASTEXITCODE -ne 0){ throw 'GitHub CLI login failed.' }
}
$login = (& $GhExe api user --jq .login).Trim()
Ok "GitHub logged in as $login"
& $GhExe repo view $Repo --json nameWithOwner *> $null
if($LASTEXITCODE -ne 0){ throw "Authenticated GitHub account cannot access $Repo" }

Step '3/9  Installing yt-dlp'
$YtExe = Join-Path $YtDir 'yt-dlp.exe'
Download 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe' $YtExe
& $YtExe --version
if($LASTEXITCODE -ne 0){ throw 'yt-dlp verification failed.' }
Ok 'yt-dlp ready'

Step '4/9  Installing FFmpeg'
$ffZip = Join-Path $env:TEMP 'aetherqor-ffmpeg.zip'
$ffTmp = Join-Path $env:TEMP 'aetherqor-ffmpeg'
Remove-Item $ffTmp -Recurse -Force -ErrorAction SilentlyContinue
Download 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' $ffZip
Expand-Archive $ffZip $ffTmp -Force
$ffmpegSrc = Get-ChildItem $ffTmp -Recurse -Filter ffmpeg.exe -File | Select-Object -First 1
$ffprobeSrc = Get-ChildItem $ffTmp -Recurse -Filter ffprobe.exe -File | Select-Object -First 1
if(-not $ffmpegSrc -or -not $ffprobeSrc){ throw 'FFmpeg package incomplete.' }
Copy-Item $ffmpegSrc.FullName (Join-Path $FfDir 'ffmpeg.exe') -Force
Copy-Item $ffprobeSrc.FullName (Join-Path $FfDir 'ffprobe.exe') -Force
Remove-Item $ffTmp -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item $ffZip -Force -ErrorAction SilentlyContinue
& (Join-Path $FfDir 'ffmpeg.exe') -version | Select-Object -First 1
Ok 'FFmpeg ready'

Step '5/9  Detecting Chrome profile for YouTube'
$ChromeExe = @(
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
  "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if(-not $ChromeExe){ throw 'Google Chrome was not found. Install Chrome first.' }
$ChromeUserData = Join-Path $env:LOCALAPPDATA 'Google\Chrome\User Data'
$profiles = @('Default')
if(Test-Path $ChromeUserData){
  $profiles += Get-ChildItem $ChromeUserData -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^Profile \d+$' } | Select-Object -ExpandProperty Name
}
$profiles = $profiles | Select-Object -Unique
$ChromeCookieSpec = 'chrome'
$chromePassed = $false
foreach($profile in $profiles){
  Write-Host "Testing Chrome profile: $profile"
  & $YtExe --no-playlist --skip-download --cookies-from-browser "chrome:$profile" --print title $YouTubeProbe *> $null
  if($LASTEXITCODE -eq 0){
    $ChromeCookieSpec = "chrome:$profile"
    $chromePassed = $true
    Ok "YouTube session works from $ChromeCookieSpec"
    break
  }
}
if(-not $chromePassed){
  Warn 'Chrome cookie test did not pass. This may be Chrome App-Bound cookie encryption or no YouTube login. The workflow will still try local-IP download without browser cookies after the Chrome attempt.'
}
Set-Content -Path (Join-Path $RunnerRoot 'chrome-cookie-spec.txt') -Value $ChromeCookieSpec -Encoding ASCII
Set-Content -Path (Join-Path $RunnerRoot 'browser.txt') -Value 'chrome' -Encoding ASCII

Step '6/9  Installing GitHub Actions runner'
$config = Join-Path $RunnerRoot 'config.cmd'
if(-not (Test-Path $config)){
  $rel = Invoke-RestMethod -Headers @{'User-Agent'='AETHERQOR-Setup'} -Uri 'https://api.github.com/repos/actions/runner/releases/latest'
  $asset = $rel.assets | Where-Object { $_.name -match '^actions-runner-win-x64-.*\.zip$' } | Select-Object -First 1
  if(-not $asset){ throw 'Could not find GitHub Actions runner Windows x64 ZIP.' }
  $zip = Join-Path $env:TEMP $asset.name
  Download $asset.browser_download_url $zip
  Expand-Archive $zip $RunnerRoot -Force
  Remove-Item $zip -Force -ErrorAction SilentlyContinue
}
if(-not (Test-Path $config)){ throw 'config.cmd is missing after runner extraction.' }

$runnerJson = Join-Path $RunnerRoot '.runner'
$needsConfig = -not (Test-Path $runnerJson)
if(-not $needsConfig){
  try {
    $r = Get-Content $runnerJson -Raw | ConvertFrom-Json
    if([string]$r.gitHubUrl -notlike "$RepoUrl*"){ $needsConfig = $true }
  } catch { $needsConfig = $true }
}
if($needsConfig -and (Test-Path $runnerJson)){
  Warn 'Existing runner configuration points elsewhere or is invalid. Removing it.'
  $removeToken = (& $GhExe api -X POST "repos/$Repo/actions/runners/remove-token" --jq .token).Trim()
  Push-Location $RunnerRoot
  try { & .\config.cmd remove --unattended --token $removeToken } finally { Pop-Location }
}
if(-not (Test-Path $runnerJson)){
  $regToken = (& $GhExe api -X POST "repos/$Repo/actions/runners/registration-token" --jq .token).Trim()
  if([string]::IsNullOrWhiteSpace($regToken)){ throw 'Could not obtain GitHub runner registration token automatically.' }
  $runnerName = "AETHERQOR-$env:COMPUTERNAME"
  Push-Location $RunnerRoot
  try {
    & .\config.cmd --url $RepoUrl --token $regToken --name $runnerName --labels 'aetherqor-video' --work '_work' --unattended --replace
    if($LASTEXITCODE -ne 0){ throw 'GitHub runner config.cmd failed.' }
  } finally { Pop-Location }
}
Ok 'GitHub Actions runner configured'

Step '7/9  Creating startup launcher'
$launcher = Join-Path $RunnerRoot 'START_AETHERQOR_RUNNER.cmd'
@"
@echo off
set "AETHERQOR_RUNNER_ROOT=$RunnerRoot"
set "AETHERQOR_TOOLS=$Tools"
set "PATH=$GhDir;$YtDir;$FfDir;%PATH%"
cd /d "$RunnerRoot"
call run.cmd
"@ | Set-Content $launcher -Encoding ASCII
if(-not $NoAutoStart){
  $startup = [Environment]::GetFolderPath('Startup')
  Copy-Item $launcher (Join-Path $startup 'AETHERQOR-GitHub-Runner.cmd') -Force
  Ok 'Auto-start enabled for Windows sign-in'
}

Step '8/9  Starting local runner'
Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*$RunnerRoot*Runner.Listener*" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Process -FilePath 'cmd.exe' -ArgumentList '/c',('"'+$launcher+'"') -WindowStyle Minimized
Start-Sleep -Seconds 5
Ok 'Runner start requested'

Step '9/9  Ensuring AETHERQOR video workflow is queued'
$active = $false
try {
  $json = & $GhExe run list --repo $Repo --workflow 'aetherqor-video-research-selfhosted.yml' --limit 10 --json status,conclusion,databaseId 2>$null
  if($LASTEXITCODE -eq 0 -and $json){
    $runs = $json | ConvertFrom-Json
    $active = @($runs | Where-Object { $_.status -in @('queued','in_progress','waiting','pending') }).Count -gt 0
  }
} catch { $active = $false }
if(-not $active){
  & $GhExe workflow run 'aetherqor-video-research-selfhosted.yml' --repo $Repo -f video_filter=all -f browser=chrome -f max_height=1080
  if($LASTEXITCODE -ne 0){ Warn 'Could not dispatch workflow automatically. Runner itself is configured; workflow can be started from GitHub Actions.' }
  else { Ok 'Research workflow dispatched for all tutorials' }
}else{ Ok 'A queued/in-progress AETHERQOR research run already exists' }

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host 'AETHERQOR SETUP COMPLETE' -ForegroundColor Green
Write-Host "Repo: $Repo"
Write-Host "Runner root: $RunnerRoot"
Write-Host 'Runner label: aetherqor-video'
Write-Host 'Browser policy: CHROME ONLY'
Write-Host "Chrome cookie source: $ChromeCookieSpec"
Write-Host 'The runner window may be minimized. Keep Windows signed in while research runs.'
Write-Host '============================================================' -ForegroundColor Green
