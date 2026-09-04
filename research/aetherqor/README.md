# AETHERQOR YouTube research runner

This setup uses a Windows self-hosted GitHub Actions runner so YouTube requests originate from the developer's normal Windows session instead of a datacenter IP.

## What one workflow run produces per tutorial

- YouTube metadata and chapter data.
- Available YouTube subtitles plus a cleaned `transcript.txt`.
- One JPEG frame for every second of the tutorial at up to the selected source resolution.
- 3x3 contact sheets built from consecutive 1-second frames.
- `frame_index.csv` and `sheet_index.csv` with exact second/timecode mappings.
- Up to 360 seconds of automatic 4 fps high-detail extraction from chapters whose titles contain character-production keywords such as hair, armor, retopo, eyes, skin, cloth, UV, rig, VFX, mesh, geometry, material or shader.
- Logs and `manifest.json`.
- The downloaded source video is deleted before artifact upload by default. Browser cookies remain local and are never included in the repository or artifact.

## Local installation

Run PowerShell as the normal Windows user who is signed in to YouTube in Chrome/Edge/Firefox:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\tools\install-aetherqor-runner.ps1 -EnableAutoStart
```

On first configuration the installer opens the repository runner setup page. Copy the short-lived Windows x64 registration token from GitHub and paste it into the hidden PowerShell prompt.

The runner label is `aetherqor-video`.

## Starting research

Open GitHub Actions and run **AETHERQOR Video Research Self-Hosted**.

- `video_filter=all` runs the entire list sequentially.
- Set `video_filter` to one slug to process only one tutorial.
- `browser=auto` uses the browser detected by the installer and falls back through Chrome, Edge, Firefox, then a no-cookie attempt.
- `max_height=1080` is the default.

The workflow uses `max-parallel: 1` because one local workstation is expected.

## Security model

This runner executes repository workflow code on the Windows workstation. Keep repository write access tightly controlled. The workflow is manual (`workflow_dispatch`) and requires the dedicated `aetherqor-video` label. If the repository becomes shared with untrusted collaborators, stop the local runner before accepting workflow changes.
