# AETHERQOR — CLAUDE CODE FULL AUTOMATION DIRECTIVE

Date: 2026-09-05
Scope: all AETHERQOR character, Blender, Unity, Python, PowerShell, QA and research workflows.

## Non-negotiable owner requirement
The owner should not have to click through Blender/Unity setup, type routine MCP registration commands, start helper servers, launch editors, re-run predictable verification steps, install known dependencies, or manually move evidence between tools.

Claude Code is the production orchestrator. If a task can be completed safely through PowerShell, CLI, Python, Blender startup scripts, Unity batch/editor scripts, MCP configuration, Git hooks, scheduled/bootstrap scripts or project-local automation, Claude MUST automate it instead of delegating the step to the owner.

Ask the owner to perform a manual action only when ALL of the following are true:
1. the action genuinely cannot be completed through the available local tools/APIs/CLI;
2. automating it would require bypassing OS/application security or would be materially unsafe;
3. no supported unattended/bootstrap path exists;
4. Claude has already tried the safe automated routes and recorded the exact blocker.

`I cannot type slash commands` is NOT an acceptable blocker if the same action can be executed as a normal `claude` CLI/PowerShell command.
`Blender needs a click` is NOT an acceptable blocker until Blender command-line/startup-Python/add-on APIs have been tested.
`Unity project is red` is NOT an acceptable blocker for toolchain smoke tests if an isolated validation worktree/project can prove the integration without touching leased work-in-progress files.

## 1. Create one-command bootstrap
Create and maintain a project-local launcher, preferably:

`tools/bootstrap-aetherqor-dev.ps1`

It must be idempotent and safe to run repeatedly.

Responsibilities:
- detect repository/project roots;
- detect exact Blender 5.2 executable;
- detect the configured Unity 6 editor executable/project path;
- verify `claude`, `uv`, Python, Git, ffmpeg/ffprobe where relevant;
- verify/create the pinned `tools/pygeom` environment;
- verify required Python packages and lock state;
- verify `astcenc` executable/version;
- verify official Unity Skills are installed and only project-relevant skills are enabled;
- verify Blender MCP registration and add-on installation;
- verify Unity MCP package/configuration;
- launch required applications/services;
- wait for health checks rather than using blind sleeps where possible;
- run P0 smoke tests;
- write a machine-readable health report;
- exit non-zero if a required component is not healthy.

Provide switches such as:
- `-InstallMissing`
- `-StartBlender`
- `-StartUnity`
- `-VerifyOnly`
- `-RepairMcp`
- `-SmokeTest`
- `-StopTools`

Do not require the owner to remember multi-command setup sequences.

## 2. Automate Claude MCP registration
Detect the current Claude CLI MCP configuration before modifying it.

If Blender MCP is missing, execute the supported CLI equivalent automatically, e.g. the current documented `claude mcp add ...` form for the installed version. Do not ask the owner to type it unless the CLI itself is unavailable or requires an interactive credential step that cannot be completed unattended.

After registration:
- list/inspect configured MCP servers;
- verify the expected Blender server entry exists;
- verify command/args/path are correct;
- record configuration proof in the health report.

Do the same for Unity MCP using the package's supported Claude Code setup/configuration path. Do NOT invent package APIs. Inspect the installed package/docs and use the supported transport/configuration for the actual installed version.

## 3. Fully automate Blender startup and MCP server
The current state already has `blender_mcp.py` installed under Blender 5.2 scripts/addons.

Create a Blender bootstrap script, e.g.:

`tools/blender/bootstrap_blender_mcp.py`

It should:
- enable the Blender MCP add-on through `bpy` if disabled;
- save user preferences when safe;
- locate the add-on's supported server-start operator/function by inspecting the installed add-on rather than guessing names;
- start the MCP server automatically;
- emit a local readiness/port marker;
- fail with a clear machine-readable error if the add-on API changed.

Launch normal Blender (not background mode if the MCP server requires a GUI/editor context) with `--python bootstrap_blender_mcp.py` or another supported startup method.

If server startup cannot occur until the UI event loop is active, use `bpy.app.timers.register(...)` from the startup script to start it after Blender initialization.

PowerShell bootstrap must:
- start Blender if not already running;
- avoid launching duplicates;
- wait for MCP readiness;
- connect/query a harmless Blender resource through MCP;
- run a harmless metric on a known fixture;
- save the result to `artifacts/qa/toolchain/blender_mcp_smoke.json`.

Do NOT ask the owner to open Preferences, toggle the add-on, and click Start Server unless automation has been proven impossible in the installed add-on version.

## 4. Fully automate Unity startup and Unity MCP
Create/maintain Unity bootstrap automation, e.g.:

`tools/unity/start_aetherqor_unity.ps1`

Responsibilities:
- locate the exact Unity editor version configured by the project;
- start the AETHERQOR Unity project with supported command-line arguments;
- avoid duplicate editor instances against the same project;
- wait until the editor/project is responsive;
- verify the Unity MCP package/configuration;
- use supported package/editor initialization to make MCP available automatically where possible;
- query editor/project state through MCP;
- save proof to `artifacts/qa/toolchain/unity_mcp_smoke.json`.

If Unity MCP requires a one-time package installation, automate it through UPM/manifest or the package's supported installation route. Do not ask the owner to click Package Manager for a package that can be installed deterministically in project files.

If an MCP server can be started from a Unity Editor initialization hook safely, add a project-local development-only bootstrap using supported APIs. Keep production runtime clean; editor/tooling code belongs in Editor-only assemblies/folders.

## 5. Unrelated red Unity tree must not block toolchain verification
Current known state: `Domain.Combat` may be temporarily red because another combat agent owns in-progress action-phase constants.

Do NOT modify leased/in-progress combat files merely to make toolchain verification green.

Instead, choose the safest valid route:

A. If Unity MCP/editor can connect despite compile errors, perform read-only connection and project-state smoke tests there.

B. For compile/reimport/test verification that requires a green project, create a disposable isolated validation worktree or minimal Unity smoke project using the same Unity version and required MCP/package/shader/importer tooling.

C. If there is a known recent green commit that can be identified without discarding current work, use an isolated git worktree at that commit for P0 toolchain validation.

Never `reset --hard`, clean, overwrite or revert another agent's leased WIP just to obtain a green tree.

Record which validation environment was used.

## 6. Automate pygeom health
The installed pygeom environment currently includes the required geometry/QA stack.

Create:
- a lock/requirements record;
- `tools/pygeom/smoke_test.py`;
- `tools/pygeom/run.ps1` wrapper.

Smoke test must exercise, on a small deterministic fixture:
- NumPy/SciPy;
- trimesh load/metrics;
- manifold3d basic operation;
- Open3D nearest-neighbor or mesh/point operation;
- xatlas parameterization call;
- PyMeshLab filter enumeration/basic safe operation;
- OpenCV/scikit-image contour/IoU path;
- pytest availability.

Use `--system-certs` automatically for `uv` operations on this machine when normal TLS fails with the known Avast `UnknownIssuer` interception. Do not disable antivirus or certificate validation globally.

## 7. Automate ASTC QA
Create an ASTC wrapper, e.g.:

`tools/textures/test_astc.ps1`

Inputs:
- texture path;
- semantic type: base/normal/mask/emission;
- candidate block sizes.

Outputs:
- encoded byte size;
- bits per pixel;
- PSNR/quality metrics when supported;
- decoded comparison image;
- CSV/JSON report.

Use it from the material/texture budget skill. No manual encoder invocation by the owner.

## 8. Skills, agents and hooks must be generated automatically
If the project-local `.claude/skills/`, `.claude/agents/` or hook configuration does not yet contain the AETHERQOR definitions from `CLAUDE_TOOLCHAIN_AND_SKILLS.md`, create them automatically.

Do not stop at writing a plan document.

Required project skills:
- `aetherqor-character-forensics`
- `aetherqor-donor-fidelity`
- `aetherqor-skinning-regression`
- `aetherqor-unity-import-qa`
- `aetherqor-screen-space-lod`
- `aetherqor-material-texture-budget`
- `aetherqor-class-identity`
- `aetherqor-external-code-license-gate`
- `aetherqor-evidence-to-implementation`

Required restricted subagents:
- mesh-forensics-agent
- unity-runtime-profiler-agent
- visual-qa-agent
- dependency-license-agent
- research-evidence-agent

Generate deterministic hooks for protected donors, Python tests, Unity compile/import tests, shader proof tests and session-state persistence.

Preserve existing useful user/project Claude configuration. Merge deliberately; do not replace configuration blindly.

## 9. One command to start a production session
The intended owner experience is:

`./tools/bootstrap-aetherqor-dev.ps1 -InstallMissing -StartBlender -StartUnity -SmokeTest`

or an even simpler project-local command if practical.

After that, Claude should be able to:
- use Blender MCP;
- use Unity MCP;
- run Python geometry QA;
- run ASTC tests;
- run Git/tests/builds;
- continue the active task graph.

If PowerShell execution policy/path quoting makes the command awkward, create a small `.cmd` launcher as well.

## 10. Auto-repair before asking the owner
When a tool is unhealthy:

1. inspect process/config/logs;
2. detect stale process/port;
3. restart only the affected local service;
4. validate executable/path/version;
5. repair project-local config;
6. retry once with captured logs;
7. only then report a true blocker.

Do not repeatedly kill Blender/Unity during normal work. Restart only when health evidence justifies it.

## 11. Machine-readable toolchain state
Maintain:

`artifacts/qa/toolchain/toolchain_health.json`

Recommended fields:
- timestamp;
- git commit/branch;
- blender executable/version/process/server health;
- unity executable/version/project/process/server health;
- Claude MCP registration state;
- pygeom Python/version/lock/package smoke results;
- astcenc version/smoke result;
- skills installed;
- agents installed;
- hooks installed;
- last error/log path;
- overall PASS/FAIL.

Claude should read this first instead of rediscovering all setup each session.

## 12. Acceptance gate
Do not call the automation complete until all safe automated checks pass:

- Blender launches automatically;
- Blender MCP add-on is enabled without owner UI work;
- Blender MCP server starts automatically or a documented API limitation proves why not;
- Claude MCP configuration includes Blender;
- a harmless Blender query/metric succeeds;
- Unity launches automatically;
- Unity MCP connection/project query succeeds in production or isolated validation environment;
- pygeom smoke passes;
- astcenc smoke passes;
- official Unity Skills are visible;
- nine AETHERQOR skills are present;
- five restricted subagents are present;
- hooks smoke test passes;
- no leased WIP file was overwritten;
- a single bootstrap command reproduces the environment from a fresh Claude session.

## 13. Reporting contract
Do not return a list of steps for the owner to perform if Claude can perform them.

Return only:
- what was automated;
- exact files created/changed;
- health checks PASS/FAIL;
- any true external/manual blocker;
- next production action.

The default outcome must be ACTION, not instructions for the owner.

## 14. Start immediately
Before asking the owner to touch Blender or Unity:
1. inspect the installed Blender MCP add-on code and discover the supported programmatic enable/start path;
2. inspect current Claude MCP configuration and register Blender automatically if missing;
3. inspect Unity MCP package/config and create the automated startup/health path;
4. create the one-command bootstrap;
5. create isolated Unity smoke verification if the production tree remains red because of leased combat WIP;
6. run all non-destructive acceptance checks;
7. checkpoint commit the automation.

Do not wait for owner confirmation between these steps.
