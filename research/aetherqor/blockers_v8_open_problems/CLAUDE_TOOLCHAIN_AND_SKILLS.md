# AETHERQOR — CLAUDE CODE TOOLCHAIN + SKILLS PLAN

Date: 2026-09-05
Target: Windows, Blender 5.2 LTS, Unity 6 URP, AETHERQOR character/gear pipeline.

## Principle
Do not install tools because they are popular. Every dependency must solve a measured AETHERQOR problem, have a known license, be pinned to a version/commit where practical, and pass a sandbox smoke test before becoming part of the production pipeline.

## P0 — install/use now

### 1. Blender MCP
Use `ahujasid/blender-mcp` so Claude Code can inspect Blender scenes, execute Blender Python, manipulate objects/materials and capture state without relying only on exported FBX files.
Windows setup:
- install `uv` from the official Astral installer;
- `claude mcp add blender uvx blender-mcp`
- `uvx blender-mcp install-addon`
- enable Interface: Blender MCP in Blender.
Security: local-only; do not expose the Blender server to untrusted networks. Treat arbitrary Blender Python execution as full local code execution.

### 2. MCP for Unity
Use `CoplayDev/unity-mcp` as the Unity 6 bridge for Claude Code. It exposes editor/scene/asset/script/material/test tools and read-only project/editor resources. Install through UPM/OpenUPM and use the package's Claude Code auto-configuration. Prefer its maintained HTTP transport unless a specific local setup requires stdio.
Required uses in AETHERQOR:
- compile/error inspection;
- asset/import inspection;
- material and shader checks;
- scene/gameobject inspection;
- EditMode/PlayMode tests;
- proof scene automation;
- profiler/test orchestration where supported.

### 3. Official Unity agent skills
Install the official public `Unity-Technologies/skills` pack with:
`npx skills add Unity-Technologies/skills`
Immediately useful skills:
- `unity-cli`
- `unity-package-management`
- `shader-graph-create-custom-node`
- `validate-urp-render-graph-renderer-feature`
Do not install/use unrelated monetization/multiplayer skills for the character pipeline unless a task actually needs them. Repository license metadata must be checked before copying any skill code into shipped game source; treat the pack primarily as agent instructions/tooling.

### 4. Python geometry/QA environment
Create a dedicated pinned environment, e.g. `D:\AetherqorFoundry\tools\pygeom` using `uv` rather than contaminating Blender's embedded Python.
Recommended packages:
- `numpy`
- `scipy`
- `trimesh`
- `manifold3d`
- `open3d`
- `xatlas`
- `pymeshlab` (offline/tooling only; GPL)
- `shapely`
- `networkx`
- `scikit-image`
- `opencv-python`
- `Pillow`
- `pandas`
- `pytest`
- `ruff`

Roles:
- trimesh: watertightness, components, nearest/signed distance, ray tests, bounds, topology/mesh QA;
- manifold3d: robust manifold/boolean reference and repair experiments;
- Open3D: nearest-neighbor, point-cloud/mesh comparison, registration/visual diagnostics;
- xatlas: controlled UV rebuild experiment and chart generation;
- PyMeshLab: broad MeshLab filter reference for offline experiments, never silently vendor GPL code into runtime;
- OpenCV/scikit-image: silhouette, IoU, contour, temporal/frame metrics;
- scipy/shapely/networkx: spatial/graph/statistical QA;
- pytest: deterministic regression suite;
- ruff: Python lint/static checks.

Pin versions after smoke testing; record `uv.lock`/requirements lock plus platform/Python version.

### 5. ASTC quality tools
Install Arm `astcenc` (Apache-2.0) as a command-line QA tool for Android/mobile character textures. Use it to test actual normal/base/mask/emission maps at candidate block sizes and record bitrate, PSNR/quality and visual proof. Do not use only source PNG size as a memory proxy.
Optional second opinion: AMD Compressonator CLI. Use for independent compression/quality comparison, not as another production dependency unless it materially improves the pipeline.

## P1 — install only if the current measured task needs it

### RetopoFlow
`CGCookie/retopoflow`, GPL, current manifest supports Blender 4.2+ and up to 6.1. Useful for artist-assisted manual retopology and local topology reconstruction. It is NOT a replacement for Alpha Wrap and should not become a blind automated step. Use only for slots where controlled manual topology is cheaper than procedural reconstruction.

### TexTools Blender
Free UV/texture/bake toolset. Useful for texel-density, UV inspection, IDs and bake comparisons. Compatibility must be smoke-tested in Blender 5.2 before production use. It is optional because most required operations can already be scripted in Blender.

### Rigify
Bundled GPL Blender add-on. It generates control rigs but does NOT skin meshes. AETHERQOR already has a working animation/retarget skeleton, so do NOT replace the production skeleton with Rigify. Use only for isolated rig prototypes/debugging if needed.

### Material Maker
Free/open procedural texture authoring. Optional for repeatable masks/pattern/detail experiments. Do not introduce it if Blender/our existing texture scripts already produce the required tier/material masks.

## GitHub code candidates: reference/adoption policy

Preferred license-safe references already identified:
- `umasteeringgroup/UMA` — MIT; serious SkinnedMeshCombiner/reference implementation.
- `Whinarn/UnityMeshSimplifier` — MIT; mesh combine/simplification reference.
- `jpcy/xatlas` — MIT; UV parameterization.
- `itsFulcrum/Unity-URP-Hair-Shader` — CC0; hair-card shading reference.
- `cathyhlshih/UnityURPAnisoHighlightHairShader` — MIT; anisotropic URP hair reference.
- `elalish/manifold` — Apache-2.0; manifold mesh algorithms.
- `mikedh/trimesh` — MIT; mesh processing/analysis.
- `isl-org/Open3D` — MIT; 3D processing.

No-license or unclear-license repositories are REFERENCE_ONLY. Never copy code from them into AETHERQOR.

## What NOT to buy/install now
- Quad Remesher / Exoside: not needed; the relevant soup problem is already solved by Alpha Wrap and the previous remesher class was disproven for that use.
- Auto-Rig Pro: do not buy while the existing AETHERQOR rig/retarget system passes its measured tests.
- another generic LOD/mesh optimizer purely because it is popular: first exhaust screen-space allocator + our measured reduction pipeline.
- paid hair-card generator: only consider if corrected target-scale + URP anisotropic shader tests prove geometry authoring remains the bottleneck.

## Claude Code project skills — create locally in `.claude/skills/`
Anthropic recommends focused skills rather than one giant instruction file. Each skill should contain `SKILL.md` plus scripts/references as needed.

### `aetherqor-character-forensics`
Trigger: diagnosing an asset before changing it.
Procedure: source provenance -> mesh/material/UV/bones/weights metrics -> stage-by-stage snapshots -> cause hypothesis -> controlled A/B -> no fix before cause.

### `aetherqor-donor-fidelity`
Trigger: reconstruction, Alpha Wrap, decimation, LOD or gear replacement.
Mandatory gates: front/3-4/side/game-camera silhouette/contour metrics, donor distance P50/P95/P99, macrofeature survival, no geometry-valid PASS when donor similarity fails.

### `aetherqor-skinning-regression`
Trigger: weights, skeleton, merge, bindpose, gear fitting, FBX changes.
Procedure: inspect bone-name map and bindposes, normalize/limit/clean weights, test non-bind poses and all relevant animation clips, compare source-vs-result vertex/deformation error, hard-fail `.001` bone ambiguity.

### `aetherqor-unity-import-qa`
Trigger: FBX/material/importer changes.
Procedure: semantic material IDs + manifest + ModelImporter/AssetPostprocessor remap, compile, reimport, verify material/renderer/bone assignments on all affected characters, no Blender-only proof.

### `aetherqor-screen-space-lod`
Trigger: triangle/LOD/microprop/hair decisions.
Procedure: always render/measure 90/150/220/300px plus equipment closeup; compute projected contribution and temporal stability; never optimize only by global triangle count.

### `aetherqor-material-texture-budget`
Trigger: tier/material/texture changes.
Procedure: material families, real GPU resident texture bytes, mip/compression audit, shader/pass/submesh count, 1/5/10-character Unity measurements, ASTC candidate comparison.

### `aetherqor-class-identity`
Trigger: class anchors, weapons, silhouettes, M/F identity.
Procedure: real gameplay camera first; outer-contour contribution, radial descriptor, color/value/material cues, motion, 7AFC preparation; never claim IoU 0.85 is an industry standard.

### `aetherqor-external-code-license-gate`
Trigger: any GitHub package/snippet/add-on/repo candidate.
Procedure: repository URL + exact commit/tag + license + transitive/asset license + adoption mode (ADOPT/PORT/REFERENCE/REJECT) + sandbox result. `NOASSERTION`/missing license => REFERENCE_ONLY.

### `aetherqor-evidence-to-implementation`
Trigger: V3-V8 research/video use.
Procedure: transcript/index -> ALL sequential 3x3 sheets -> selected 1fps -> selected 4fps -> evidence ledger -> current source/asset -> real experiment -> metric -> proof -> implementation -> regression -> checkpoint commit. Never stop at `RESEARCH_DONE`.

## Claude Code subagents — isolate noisy work
Create in `.claude/agents/`:
- `mesh-forensics-agent`: read-heavy Blender/Python diagnostics; returns concise cause + metric table.
- `unity-runtime-profiler-agent`: Unity MCP, tests/profiler/read-only where possible; returns runtime evidence.
- `visual-qa-agent`: reviews proof frames/contact sheets and screen-space comparisons; no source edits.
- `dependency-license-agent`: read-only GitHub/license/dependency audit.
- `research-evidence-agent`: source/video/forum cross-checking, no code edits.

Keep implementation in the main agent or a dedicated write-enabled integrator. Do not give every subagent unrestricted write/shell access.

## Deterministic hooks — more valuable than more prompting
Configure Claude Code hooks after the skills are present:

### PreToolUse guards
Block or require explicit special procedure for:
- deletion/overwrite of raw donors and known-good PASS assets;
- `git reset --hard`, destructive clean, recursive deletion of project roots;
- writes into immutable research evidence folders;
- vendoring external code without a recorded license row.

### PostToolUse checks
After relevant edits:
- Python -> `ruff` + targeted `pytest`;
- character pipeline code -> fast mesh QA smoke test;
- Unity C# -> compile/import check through Unity MCP, targeted EditMode tests;
- material/shader -> shader compile + proof-scene smoke test;
- FBX/export/import code -> one known character round-trip test.

### SessionStart
Inject concise dynamic context only: git branch/status, active blocker, latest QA failures, V8 package path, current production character IDs. Do not stuff the whole research corpus into CLAUDE.md.

### PreCompact
Persist current experiment state: hypothesis, changed files, commands, outputs, metrics, next action and rollback point.

## CLAUDE.md should stay small
Keep always-on facts only:
- project roots;
- Unity/Blender versions;
- build/test commands;
- immutable asset rules;
- checkpoint commit policy;
- exact screen-space targets;
- where research packages live.
Long procedures belong in skills, not CLAUDE.md.

## Recommended rollout order
1. Install `uv`.
2. Connect Blender MCP.
3. Connect Unity MCP.
4. Install official Unity agent skills, but enable/use only relevant ones.
5. Build/pin `pygeom` environment.
6. Install `astcenc`.
7. Add the nine AETHERQOR project skills.
8. Add five restricted subagents.
9. Add destructive-action and QA hooks.
10. Only then evaluate RetopoFlow/TexTools/Material Maker in sandbox if a measured blocker needs them.

## Acceptance test before declaring toolchain ready
- Claude can query Blender scene/object/mesh state and run a harmless scripted metric.
- Claude can query Unity editor/project state, reimport one test asset and run a targeted test.
- Python environment reproduces mesh metrics on a known fixture.
- ASTC tool compresses one base color and one normal map and writes quality metrics.
- license skill rejects a fixture repository with no license.
- donor-fidelity skill fails a deliberately distorted mesh.
- skinning-regression skill catches a deliberately corrupted weight/bone mapping.
- screen-space skill produces measurements at 90/150/220/300px.
- hooks block a destructive command against a protected donor test directory.

Only after these pass should the toolchain be considered production-ready.