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

function Write-Step([string]$Text) { Write-Host "`n=== $Text ===" -ForegroundColor Cyan }
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
function Find-Chrome {
    $candidates = @(
        "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
        "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
    )
    foreach ($p in $candidates) { if (Test-Path $p) { return $p } }
    return $null
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
    & (Join-Path $ffBin "ffmpeg.exe") -version | Select-Object -First 1
    Remove-Item $ffZip -Force -ErrorAction SilentlyContinue
    Remove-Item $ffExtract -Recurse -Force -ErrorAction SilentlyContinue
} else {
    $ytExe = Join-Path $ytDir "yt-dlp.exe"
}

Write-Step "Chrome preference"
$chromeExe = Find-Chrome
if (-not $chromeExe) { throw "Google Chrome was not found. Install Chrome before continuing." }
"chrome" | Set-Content -Path (Join-Path $RunnerRoot "browser.txt") -Encoding ASCII
Write-Host "Chrome selected for all AETHERQOR browser steps." -ForegroundColor Green

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
            try {
                $autoToken = (& $gh.Source api -X POST "repos/$repoSlug/actions/runners/registration-token" --jq .token 2>$null | Select-Object -First 1).Trim()
                if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($autoToken)) { $RegistrationToken = $autoToken }
            } catch {}
        }
    }
    if ([string]::IsNullOrWhiteSpace($RegistrationToken)) {
        $setupUrl = "$RepoUrl/settings/actions/runners/new?arch=x64&os=win"
        Start-Process -FilePath $chromeExe -ArgumentList $setupUrl
        $secureToken = Read-Host "Paste the GitHub runner registration token" -AsSecureString
        $RegistrationToken = Get-PlainTextFromSecureString $secureToken
    }
    if ([string]::IsNullOrWhiteSpace($RegistrationToken)) { throw "Registration token is required for first-time runner configuration." }

    $runnerName = "AETHERQOR-$env:COMPUTERNAME"
    Push-Location $RunnerRoot
    try {
        & .\config.cmd --url $RepoUrl --token $RegistrationToken --name $runnerName --labels "aetherqor-video" --work "_work" --unattended --replace
        if ($LASTEXITCODE -ne 0) { throw "GitHub runner configuration failed." }
    } finally { Pop-Location }
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
    $startup = [Environment]::GetFolderPath("Startup")
    Copy-Item $launcher (Join-Path $startup "AETHERQOR-GitHub-Runner.cmd") -Force
}

Write-Step "Starting runner now"
Start-Process -FilePath "cmd.exe" -ArgumentList "/c", ('"' + $launcher + '"') -WindowStyle Minimized
Write-Host "`nREADY" -ForegroundColor Green
Write-Host "Runner root: $RunnerRoot"
Write-Host "Browser preference: Chrome"
Write-Host "Repo: $RepoUrl"
Write-Host "Label: aetherqor-video"
