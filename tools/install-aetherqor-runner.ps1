[CmdletBinding()]
param(
    [string]$RepoUrl = "https://github.com/tkinvestmentseu-debug/vendocerta-download",
    [string]$RunnerRoot = "$env:LOCALAPPDATA\AETHERQOR_GitHubRunner",
    [string]$RegistrationToken = "",
    [switch]$EnableAutoStart,
    [switch]$SkipToolInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Write-Step([string]$Text) {
    Write-Host "`n=== $Text ===" -ForegroundColor Cyan
}

function Get-PlainTextFromSecureString([Security.SecureString]$Secure) {
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Secure)
    try { return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
}

function Download-File([string]$Url, [string]$Destination) {
    $parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $Destination -Headers @{"User-Agent"="AETHERQOR-Runner-Installer"}
}

Write-Step "Preparing local directories"
New-Item -ItemType Directory -Path $RunnerRoot -Force | Out-Null
$toolsRoot = Join-Path $RunnerRoot "tools"
$ytDir = Join-Path $toolsRoot "yt-dlp"
$ffDir = Join-Path $toolsRoot "ffmpeg"
New-Item -ItemType Directory -Path $toolsRoot,$ytDir,$ffDir -Force | Out-Null

if (-not $SkipToolInstall) {
    Write-Step "Installing yt-dlp"
    $ytExe = Join-Path $ytDir "yt-dlp.exe"
    Download-File "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe" $ytExe
    & $ytExe --version
    if ($LASTEXITCODE -ne 0) { throw "yt-dlp verification failed." }

    Write-Step "Installing FFmpeg"
    $ffZip = Join-Path $env:TEMP "aetherqor-ffmpeg.zip"
    $ffExtract = Join-Path $env:TEMP "aetherqor-ffmpeg-extract"
    if (Test-Path $ffExtract) { Remove-Item $ffExtract -Recurse -Force }
    Download-File "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip" $ffZip
    Expand-Archive -Path $ffZip -DestinationPath $ffExtract -Force
    $ffmpegExe = Get-ChildItem -Path $ffExtract -Filter ffmpeg.exe -Recurse -File | Select-Object -First 1
    $ffprobeExe = Get-ChildItem -Path $ffExtract -Filter ffprobe.exe -Recurse -File | Select-Object -First 1
    if (-not $ffmpegExe) { throw "Could not find ffmpeg.exe in downloaded package." }

    $ffBin = Join-Path $ffDir "bin"
    New-Item -ItemType Directory -Path $ffBin -Force | Out-Null
    Copy-Item $ffmpegExe.FullName (Join-Path $ffBin "ffmpeg.exe") -Force
    if ($ffprobeExe) { Copy-Item $ffprobeExe.FullName (Join-Path $ffBin "ffprobe.exe") -Force }
    (Join-Path $ffBin "ffmpeg.exe") | Set-Content -Path (Join-Path $RunnerRoot "ffmpeg-path.txt") -Encoding ASCII
    & (Join-Path $ffBin "ffmpeg.exe") -version | Select-Object -First 1
    if ($LASTEXITCODE -ne 0) { throw "FFmpeg verification failed." }

    Remove-Item $ffZip -Force -ErrorAction SilentlyContinue
    Remove-Item $ffExtract -Recurse -Force -ErrorAction SilentlyContinue
} else {
    $ytExe = Join-Path $ytDir "yt-dlp.exe"
}

Write-Step "Checking browser session for YouTube"
$browserCandidates = New-Object System.Collections.Generic.List[string]
$chromePaths = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)
$edgePaths = @(
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
)
$firefoxPaths = @(
    "$env:ProgramFiles\Mozilla Firefox\firefox.exe",
    "${env:ProgramFiles(x86)}\Mozilla Firefox\firefox.exe"
)
if ($chromePaths | Where-Object { Test-Path $_ }) { $browserCandidates.Add("chrome") }
if ($edgePaths | Where-Object { Test-Path $_ }) { $browserCandidates.Add("edge") }
if ($firefoxPaths | Where-Object { Test-Path $_ }) { $browserCandidates.Add("firefox") }
if ($browserCandidates.Count -eq 0) { $browserCandidates.Add("chrome") }

$browserChosen = $browserCandidates[0]
if (Test-Path $ytExe) {
    foreach ($browser in $browserCandidates) {
        Write-Host "Testing YouTube session from $browser..."
        $probeOut = & $ytExe --no-playlist --skip-download --cookies-from-browser $browser --print title "https://www.youtube.com/watch?v=3bw2SnKQhwA" 2>&1
        if ($LASTEXITCODE -eq 0) {
            $browserChosen = $browser
            Write-Host "YouTube session OK via $browser." -ForegroundColor Green
            break
        }
        Write-Host "Session test via $browser did not pass. The workflow will retry browsers automatically." -ForegroundColor Yellow
    }
}
$browserChosen | Set-Content -Path (Join-Path $RunnerRoot "browser.txt") -Encoding ASCII

Write-Step "Installing GitHub Actions runner"
$configCmd = Join-Path $RunnerRoot "config.cmd"
if (-not (Test-Path $configCmd)) {
    $headers = @{"User-Agent"="AETHERQOR-Runner-Installer"; "Accept"="application/vnd.github+json"}
    $release = Invoke-RestMethod -Uri "https://api.github.com/repos/actions/runner/releases/latest" -Headers $headers
    $asset = $release.assets | Where-Object { $_.name -match '^actions-runner-win-x64-.*\.zip$' } | Select-Object -First 1
    if (-not $asset) { throw "Could not locate the latest Windows x64 GitHub runner package." }
    $runnerZip = Join-Path $env:TEMP $asset.name
    Download-File $asset.browser_download_url $runnerZip
    Expand-Archive -Path $runnerZip -DestinationPath $RunnerRoot -Force
    Remove-Item $runnerZip -Force -ErrorAction SilentlyContinue
}

$runnerAlreadyConfigured = Test-Path (Join-Path $RunnerRoot ".runner")
if (-not $runnerAlreadyConfigured) {
    if ([string]::IsNullOrWhiteSpace($RegistrationToken)) {
        $repoSlug = $RepoUrl -replace '^https://github\.com/','' -replace '/$',''
        $gh = Get-Command gh -ErrorAction SilentlyContinue
        if ($gh) {
            Write-Host "GitHub CLI detected. Trying to obtain the short-lived runner registration token automatically..."
            try {
                $autoToken = (& $gh.Source api -X POST "repos/$repoSlug/actions/runners/registration-token" --jq .token 2>$null | Select-Object -First 1).Trim()
                if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($autoToken)) {
                    $RegistrationToken = $autoToken
                    Write-Host "Runner registration token obtained through GitHub CLI." -ForegroundColor Green
                }
            } catch {
                Write-Host "GitHub CLI could not provide a token. Falling back to the GitHub setup page." -ForegroundColor Yellow
            }
        }
    }
    if ([string]::IsNullOrWhiteSpace($RegistrationToken)) {
        $setupUrl = "$RepoUrl/settings/actions/runners/new?arch=x64&os=win"
        Write-Host "Opening the GitHub runner setup page. Copy the short-lived registration token from the Windows x64 setup command." -ForegroundColor Yellow
        Start-Process $setupUrl
        $secureToken = Read-Host "Paste the GitHub runner registration token" -AsSecureString
        $RegistrationToken = Get-PlainTextFromSecureString $secureToken
    }
    if ([string]::IsNullOrWhiteSpace($RegistrationToken)) { throw "Registration token is required for first-time runner configuration." }

    $runnerName = "AETHERQOR-$env:COMPUTERNAME"
    Push-Location $RunnerRoot
    try {
        & .\config.cmd --url $RepoUrl --token $RegistrationToken --name $runnerName --labels "aetherqor-video" --work "_work" --unattended --replace
        if ($LASTEXITCODE -ne 0) { throw "GitHub runner configuration failed." }
    } finally {
        Pop-Location
    }
} else {
    Write-Host "Runner is already configured. Existing registration was preserved." -ForegroundColor Green
}

Write-Step "Creating user-session launcher"
$ffBin = Join-Path $ffDir "bin"
$launcher = Join-Path $RunnerRoot "start-aetherqor-runner.cmd"
$launcherContent = @"
@echo off
set "AETHERQOR_RUNNER_ROOT=$RunnerRoot"
set "AETHERQOR_TOOLS=$toolsRoot"
set "PATH=$ytDir;$ffBin;%PATH%"
cd /d "$RunnerRoot"
call run.cmd
"@
$launcherContent | Set-Content -Path $launcher -Encoding ASCII

if ($EnableAutoStart) {
    Write-Step "Enabling runner at Windows sign-in"
    $startup = [Environment]::GetFolderPath("Startup")
    $startupLauncher = Join-Path $startup "AETHERQOR-GitHub-Runner.cmd"
    Copy-Item $launcher $startupLauncher -Force
    Write-Host "Auto-start enabled for the current Windows user." -ForegroundColor Green
} else {
    Write-Host "Auto-start was not enabled. You can rerun this installer with -EnableAutoStart later." -ForegroundColor Yellow
}

Write-Step "Starting runner now"
Start-Process -FilePath "cmd.exe" -ArgumentList "/c", ('"' + $launcher + '"') -WindowStyle Minimized

Write-Host "`nREADY" -ForegroundColor Green
Write-Host "Runner root: $RunnerRoot"
Write-Host "Browser preference: $browserChosen"
Write-Host "Repo: $RepoUrl"
Write-Host "Label: aetherqor-video"
Write-Host "Launcher: $launcher"
Write-Host "`nImportant: keep the Windows user session logged in. The workflow reads YouTube cookies only from this local user profile and never commits them to GitHub."
