[CmdletBinding()]
param(
  [string]$OutputDir = "$env:RUNNER_TEMP\aetherqor-blockers-v3-forensics"
)

Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$roots=@(
  'D:\AetherqorFoundry',
  'E:\AETHERQOR_ODCHUDZONE\ZBROJA_PELNA'
)

$report=[ordered]@{
  created_utc=[DateTime]::UtcNow.ToString('o')
  machine=$env:COMPUTERNAME
  roots=@()
  blender=@()
  files=@()
  scripts=@()
  problem_docs=@()
}

foreach($root in $roots){
  $exists=Test-Path $root
  $report.roots += [ordered]@{path=$root;exists=$exists}
  if(!$exists){continue}
  $items=Get-ChildItem -Path $root -Recurse -File -ErrorAction SilentlyContinue
  foreach($f in $items){
    $name=$f.Name
    $full=$f.FullName
    $isRelevant = $name -match '(?i)RunicWarden|boot_L|glove_R|hair|wlos|włos|retopo|bake|uv|weight|skin|armor|armour|lod|character_bible|pytania_do_researchu|rejected|gear'
    if($isRelevant -and $f.Extension -match '(?i)^\.(fbx|blend|obj|glb|gltf|py|ps1|md|txt|json|csv)$'){
      $report.files += [ordered]@{
        path=$full
        ext=$f.Extension
        bytes=$f.Length
        modified_utc=$f.LastWriteTimeUtc.ToString('o')
      }
    }
    if($f.Extension -eq '.py' -and $name -match '(?i)retopo|bake|uv|weight|skin|armor|gear|hair|wlos|lod|mesh'){
      $report.scripts += $full
    }
    if($name -match '(?i)PYTANIA_DO_RESEARCHU|CHARACTER_BIBLE|REJECTED_APPROACHES'){
      $report.problem_docs += $full
    }
  }
}

$blenderCandidates=@(
 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe',
 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe',
 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe'
)
$cmd=Get-Command blender -ErrorAction SilentlyContinue
if($cmd){$blenderCandidates=@($cmd.Source)+$blenderCandidates}
foreach($b in ($blenderCandidates|Select-Object -Unique)){
 if(Test-Path $b){
   $ver=& $b --version 2>&1 | Select-Object -First 1
   $report.blender += [ordered]@{path=$b;version=[string]$ver}
 }
}

$report.files = @($report.files | Sort-Object bytes -Descending | Select-Object -First 500)
$report.scripts = @($report.scripts | Select-Object -Unique | Sort-Object)
$report.problem_docs = @($report.problem_docs | Select-Object -Unique | Sort-Object)
$report | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 (Join-Path $OutputDir 'forensic_inventory.json')

$report.files | ForEach-Object { [pscustomobject]$_ } | Export-Csv -NoTypeInformation -Encoding UTF8 (Join-Path $OutputDir 'relevant_files.csv')
$report.scripts | Set-Content -Encoding UTF8 (Join-Path $OutputDir 'relevant_scripts.txt')
$report.problem_docs | Set-Content -Encoding UTF8 (Join-Path $OutputDir 'problem_docs.txt')

# Extract selected source snippets without modifying project files.
$snipDir=Join-Path $OutputDir 'source_snippets'
New-Item -ItemType Directory -Force -Path $snipDir | Out-Null
$i=0
foreach($p in ($report.scripts | Select-Object -First 80)){
  try{
    $i++
    $safe=('{0:000}_{1}' -f $i,([IO.Path]::GetFileName($p) -replace '[^A-Za-z0-9_.-]','_'))
    @("SOURCE=$p",'') + (Get-Content -Path $p -Encoding UTF8 -TotalCount 800) | Set-Content -Encoding UTF8 (Join-Path $snipDir "$safe.txt")
  } catch {}
}
foreach($p in ($report.problem_docs | Select-Object -First 20)){
  try{
    $i++
    $safe=('{0:000}_{1}' -f $i,([IO.Path]::GetFileName($p) -replace '[^A-Za-z0-9_.-]','_'))
    @("SOURCE=$p",'') + (Get-Content -Path $p -Encoding UTF8 -TotalCount 2000) | Set-Content -Encoding UTF8 (Join-Path $snipDir "$safe.txt")
  } catch {}
}

Write-Host "FORENSIC_SCAN_OK files=$($report.files.Count) scripts=$($report.scripts.Count) docs=$($report.problem_docs.Count)"