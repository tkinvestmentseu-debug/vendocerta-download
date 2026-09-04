[CmdletBinding()]
param(
  [string]$OutputDir = "$env:RUNNER_TEMP\aetherqor-blocker-video-discovery",
  [int]$PerQuery = 5
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) { $PSNativeCommandUseErrorActionPreference = $false }

$runnerRoot = if ($env:AETHERQOR_RUNNER_ROOT) { $env:AETHERQOR_RUNNER_ROOT } else { 'C:\AETHERQOR_GitHubRunner' }
if (!(Test-Path $runnerRoot)) { $runnerRoot = "$env:LOCALAPPDATA\AETHERQOR_GitHubRunner" }
$yt = Join-Path $runnerRoot 'tools\yt-dlp\yt-dlp.exe'
if (!(Test-Path $yt)) {
  $cmd = Get-Command yt-dlp -ErrorAction SilentlyContinue
  if (!$cmd) { throw 'yt-dlp not found' }
  $yt = $cmd.Source
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$queries = @(
  [pscustomobject]@{ blocker=1; key='shell_repair_zbrush'; q='game ready armor ZBrush Dynamesh ZRemesher hard surface retopology' },
  [pscustomobject]@{ blocker=1; key='shell_repair_blender'; q='repair non manifold overlapping shells Blender boolean hard surface game asset' },
  [pscustomobject]@{ blocker=2; key='rigid_armor_skinning'; q='rigid armor skin weights weight painting game character shoulder pad bracer' },
  [pscustomobject]@{ blocker=3; key='class_silhouette'; q='game character silhouette readability class design Riot Valve character art' },
  [pscustomobject]@{ blocker=4; key='mobile_character_lod'; q='mobile game character optimization LOD polygon triangle budget character' },
  [pscustomobject]@{ blocker=5; key='gloves_gauntlets'; q='game ready gloves hand retopology gauntlet armor Blender ZBrush' },
  [pscustomobject]@{ blocker=6; key='uv_baking'; q='high poly low poly UV baking hard surface game asset Marmoset Toolbag' },
  [pscustomobject]@{ blocker=7; key='hair_cards_optimization'; q='game ready hair cards optimization low poly Blender hair cards LOD' }
)

$rows = New-Object System.Collections.Generic.List[object]
foreach ($entry in $queries) {
  Write-Host "SEARCH blocker $($entry.blocker): $($entry.q)"
  $search = "ytsearch$PerQuery`:$($entry.q)"
  $raw = & $yt --flat-playlist --dump-json --skip-download --no-warnings $search 2>&1
  if ($LASTEXITCODE -ne 0) {
    Write-Warning "Search failed: $($entry.q)"
    $raw | Set-Content -Encoding UTF8 (Join-Path $OutputDir "$($entry.key)_error.txt")
    continue
  }
  foreach ($line in $raw) {
    if (-not $line.Trim().StartsWith('{')) { continue }
    try { $j = $line | ConvertFrom-Json } catch { continue }
    $id = [string]$j.id
    if (!$id) { continue }
    $duration = $null
    if ($j.PSObject.Properties.Name -contains 'duration') { $duration = $j.duration }
    $rows.Add([pscustomobject]@{
      blocker = $entry.blocker
      query_key = $entry.key
      query = $entry.q
      id = $id
      url = "https://www.youtube.com/watch?v=$id"
      title = [string]$j.title
      channel = if ($j.PSObject.Properties.Name -contains 'channel') { [string]$j.channel } elseif ($j.PSObject.Properties.Name -contains 'uploader') { [string]$j.uploader } else { '' }
      duration_seconds = $duration
      view_count = if ($j.PSObject.Properties.Name -contains 'view_count') { $j.view_count } else { $null }
    })
  }
}

$csv = Join-Path $OutputDir 'candidates.csv'
$rows | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $csv
$rows | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 (Join-Path $OutputDir 'candidates.json')

$md = New-Object System.Collections.Generic.List[string]
$md.Add('# AETHERQOR blocker video candidates')
$md.Add('')
foreach ($b in 1..7) {
  $md.Add("## Blocker $b")
  foreach ($r in ($rows | Where-Object blocker -eq $b)) {
    $dur = if ($r.duration_seconds) { [TimeSpan]::FromSeconds([double]$r.duration_seconds).ToString() } else { '?' }
    $md.Add("- [$($r.title)]($($r.url)) | $($r.channel) | $dur | query=$($r.query_key)")
  }
  $md.Add('')
}
$md | Set-Content -Encoding UTF8 (Join-Path $OutputDir 'CANDIDATES.md')

Write-Host "DISCOVERY_OK candidates=$($rows.Count) output=$OutputDir"