# AETHERQOR V5 — CLAUDE RESEARCH HANDOFF

## Mission

Close five architecture blockers with evidence and experiments. Do not produce another generic research essay.

Root after workflow completion:
`D:\AetherqorFoundry\research\blockers_v5_architecture\ULTRA_RESEARCH_2026-09-05`

Reuse existing local evidence instead of redownloading it:
- V3: `D:\AetherqorFoundry\research\blockers_v3\CLAUDE_VIDEO_REPORT_33904162671`
- V4: `D:\AetherqorFoundry\research\blockers_v4_night\ULTRA_RESEARCH_2026-09-04_NIGHT`

## Mandatory reading order

1. `LOCAL_READY.md`
2. `QUESTIONS.md`
3. `SOURCE_REGISTRY.md`
4. `PRELIMINARY_VERDICTS.md`
5. `CHATGPT_INDEPENDENT_ANALYSIS.md`
6. `FINAL_STATUS.md`
7. each new video `manifest.json`, `transcript.txt`, `frame_index.csv`, `sheet_index.csv`, `high_detail_index.csv`
8. 3x3 contact sheets sequentially
9. selected raw 1fps frames only for relevant time ranges
10. selected 4fps high-detail frames for critical visual steps

`CHATGPT_INDEPENDENT_ANALYSIS.md` is an independent technical hypothesis set, not authority. Validate or falsify it with V5 video evidence and real AETHERQOR experiments.

Transcripts are navigation aids, not visual proof.

## Evidence record format

For every external/video conclusion record:
- problem id P1-P5
- source authority class
- video slug/source URL
- timecode
- sheet/frame filename if video
- exact observed technique/fact
- relevance to AETHERQOR
- confidence: PROVEN_PRIMARY / PRODUCTION_BREAKDOWN / EXTRACTED_MODEL_WEAK_EVIDENCE / COMMUNITY_SECONDARY / HYPOTHESIS

## P1 execution contract — triangle architecture

Do not merely find a triangle-count number.

Audit current AETHERQOR assembled character and produce a machine-readable table for every visible runtime object:
- logical slot
- renderer/mesh
- triangles before/after modifiers
- whether Solidify is present
- outer-facing triangles
- inner/back-facing triangles
- material count
- skinned/static
- screen-space contribution at 90/150/220/300 px
- whether hidden by another layer
- whether visible from gameplay camera

Then build at least three architecture variants on the same real outfit:
A. current full Solidify architecture
B. one-sided outer shells + local rim thickness only where visible
C. revised gameplay budget with per-context LOD allocation

For A/B/C measure:
- full rendered triangles
- vertices after splits
- SkinnedMeshRenderer count
- draw calls/batches
- GPU frame cost on target-like mobile profile or best available device profile
- silhouette deviation
- visible holes from gameplay and equipment cameras
- animation clipping

Required decision:
- keep 14k universal, OR
- 14k gameplay-only + higher hero/equipment LOD, OR
- new measured gameplay budget
with explicit slot allocation and justification.

Do not accept public extracted model counts as official studio limits. Use them only as range/context evidence.

## P2 execution contract — Alpha Wrap

Primary docs already establish that triangle soup is valid input. The unknown is whether it preserves the features AETHERQOR needs.

Use real donor cuirass and shoulder.
Run alpha x offset sweeps in real units.
Measure:
- connected components
- boundary edges
- non-manifold edges
- self-intersections
- watertight/orientation validity
- triangles
- donor mean/P95/max distance
- panel-gap survival for 3-8 mm gaps
- concavity retention
- body penetration
- silhouette difference

Compare Alpha Wrap against current best per-slot reconstruction and one VDB/SDF alternative if tooling is available.

Do not retry rejected QRemeshify/Quadriflow/Boolean soup workflows.

## P3 execution contract — budget allocator / protected reduction

Inspect `retopo_postaci.py` and all calls that apply a second reduction to meshes already in slot target.

Build a report showing exactly where the second collapse occurs and how many triangles each approved slot loses.

Prototype a budget allocator with:
- slot min / target / max
- protected boundary/silhouette weights
- deformation importance
- screen-space importance
- global outfit sum constraint

Test either existing reducer vertex groups/weights or a production reducer capable of feature importance. If Simplygon is installable/licensable locally, a small proof is useful; if not, reproduce the architecture using available Blender tooling and mark the Simplygon-specific path as external.

Success requires preserving known edge loops such as shoulder 16/16 while meeting the measured global target. If the global target is impossible, P1 must change it rather than silently destroying P3 assets.

## P4 execution contract — hair occlusion boundaries

Do not repeat scalp normal transfer, cap-only SEG increase, or solid scalp dome.

Use one failing hairstyle and keep total budget approximately 1600-2000 tri.
Create controlled variants that alter only the real suspected mechanism:
- current flat overlap
- more curved main/underlay cards with same-ish triangle budget
- opaque/base coverage layer + breakup cards
- adjusted overlap/depth ordering
- Alpha Clip vs Dithered vs Alpha Blend where supported

Render at real gameplay camera and equipment camera under static and rotating light.
Measure:
- visible faceting/occlusion boundary metric if possible
- scalp exposure
- triangles
- overdraw
- sorting artifacts
- temporal stability
- frame cost with multiple characters

Use existing V4 `p3_urp_hair_shader` and `p3_ffvii_hair_normals` evidence instead of downloading them again.

## P5 execution contract — actual gameplay recognition

Existing pairwise mask gate is necessary but not sufficient.

Generate actual class renders at:
- azimuth 35 degrees
- elevation 50 degrees
- real gameplay FOV/distance
- 90, 150, 220, 300 px character height

Compare identity channels:
A. black silhouette only
B. silhouette + weapon/prop anchor
C. normal material/color
D. material/color + class VFX cue if representative
E. representative idle/motion pose if possible

Metrics:
- IoU
- contour Hausdorff or robust percentile Hausdorff
- Chamfer contour distance
- top-view radial/shape descriptor
- anchor contribution
- timed human recognition/confusion matrix using a simple local test harness

Required decision: whether every class needs a top-down protruding silhouette anchor, or whether the contract should combine silhouette + controlled non-silhouette identity channels.

## Hard workflow contract

For every blocker:
`READ SOURCES -> REVIEW VIDEO FRAMES -> AUDIT CURRENT CODE/ASSET -> HYPOTHESIS -> MINIMAL EXPERIMENT -> METRICS -> PROOF RENDER -> PRODUCTION DECISION -> IMPLEMENTATION/QA -> CHECKPOINT COMMIT`

Allowed final statuses:
- `IMPLEMENTED_PASS`
- `IMPLEMENTED_FAIL` with exact reason
- `RESEARCH_CONFIRMED_NEEDS_ENGINEERING` only for a proven solution that needs a large separate component
- `BLOCKED_EXTERNAL` only for a true external dependency

Forbidden final status: `RESEARCH_DONE`.

## Final deliverable

Create `AETHERQOR_V5_FINAL_TECHNICAL_DECISIONS.md` containing a table:

| Problem | Current measured state | Method/architecture tested | Result | Production decision | Status | Commit |
|---|---|---|---|---|---|---|
| P1 budget architecture | | | | | | |
| P2 shell soup | | | | | | |
| P3 second decimation | | | | | | |
| P4 hair occlusion | | | | | | |
| P5 gameplay identity | | | | | | |

Separate PROVEN / LIKELY / NOT PROVEN. Every PROVEN statement must point to source evidence and local test evidence.
