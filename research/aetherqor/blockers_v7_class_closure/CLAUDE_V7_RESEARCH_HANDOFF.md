# AETHERQOR V7 — CLAUDE RESEARCH + IMPLEMENTATION HANDOFF

Local root after workflow success:
`D:\AetherqorFoundry\research\blockers_v7_class_closure\ULTRA_RESEARCH_2026-09-05_CLASS_CLOSURE`

## Mission
This is not a generic research report. Resolve P1-P5 into production architecture and immediately validate on the actual AETHERQOR project.

Required loop:
`SOURCE READ -> VIDEO FRAME REVIEW -> CURRENT AETHERQOR MEASUREMENT -> HYPOTHESIS -> IMPLEMENTATION EXPERIMENT -> REAL CHARACTER/ASSET -> UNITY/BLENDER METRICS -> PROOF RENDER/VIDEO -> VERDICT -> CODE CHANGE -> QA -> CHECKPOINT COMMIT`

Do not use `RESEARCH_DONE` as a final status.

## Read order
1. `LOCAL_READY.md`
2. `QUESTIONS.md`
3. `CHATGPT_INDEPENDENT_ANALYSIS.md`
4. `PRELIMINARY_VERDICTS.md`
5. `SOURCE_REGISTRY.md`
6. `FINAL_STATUS.md`
7. `videos.psv`
8. V7 videos as described below
9. relevant V3/V4/V5/V6 evidence
10. actual AETHERQOR code/assets/bibles/QA contracts

## Video review protocol
For every V7 slug:
1. `manifest.json`
2. `transcript.txt`
3. `frame_index.csv`
4. `sheet_index.csv`
5. `high_detail_index.csv` if present
6. ALL 3x3 contact sheets sequentially
7. selected raw 1fps frames around important moments
8. 4fps high-detail around moments where visual technique or UI/engine state matters

Evidence ledger row:
`P#, slug, source_url, timecode, sheet, frame, fact_shown, AETHERQOR_application, confidence, local_test`.

Never infer a visual fact only from transcript.

## P1 implementation task — tier architecture
Do NOT create 931 texture sets.

1. Audit one promoted complete character:
   - logical slots
   - visible slots by gameplay camera and equipment camera
   - mesh count
   - renderer count
   - submesh count
   - material count
   - texture count
   - texture dimensions/formats/resident bytes
   - shader variants
2. Build `tier_material_audit.csv`.
3. Prototype three representations on the SAME character:
   A current architecture
   B shared material families + shared trim/atlas + RGBA masks, slots still separate
   C B + compatible opaque mesh aggregation after equip
4. Define `tier_visual_table.json` and `material_family_manifest.json`.
5. Build Tier 0, Tier 3, Tier 6 and Tier 7 visual variants without unique full PBR sets unless absolutely required.
6. Render 90/150/220/300 px + equipment closeup.
7. Measure texture resident memory, draw calls, setpass/state changes, SRP batches, CPU render thread, GPU frame time for 1/5/10 characters.
8. Decide exactly which channels can be shared and which need unique content.

Deliverable: `P1_TIER_ARCHITECTURE_DECISION.md` with before/after counts and memory.

## P2 implementation task — micro-prop gate
Before integrating rings on 14 characters, create a projected-size analyzer.

For every micro-prop at 90/150/220/300 px and key views output:
`prop, view, bbox_w_px, bbox_h_px, occupied_pixels, silhouette_delta_pixels, moving, gameplay_decision, closeup_decision`.

Test at least:
- ring
- buckle
- amulet
- rivet/plate stud
- small chain/pendant if present

Create four variants for one representative accessory:
A geometry gameplay
B baked normal/albedo/roughness only
C removed gameplay, closeup geometry retained
D geometry simplified to minimum silhouette-supporting form

Render in motion, not only stills.

Do not adopt ChatGPT's proposed 1px / 4-9 pixel gate blindly. Calibrate it from actual AETHERQOR images and aliasing/mipmap behavior.

Deliverable: `P2_MICROPROP_SCREENSPACE_CONTRACT.md` and an automated QA script.

## P3 implementation task — enhancement +0..+10
Use the existing compatible gear shader/material architecture. Prototype one enhancement mask and parameter path.

Required shader properties or equivalent:
- EnhanceLevel01
- EnhanceColor
- EnhanceEmission
- EnhanceSmoothnessBoost
- EnhanceMaskStrength

Render levels 0..10 in exactly the same scene/camera/light at 90/150/220/300 px, plus rotating equipment closeup.

Create a local perception test for adjacent levels. If N and N+1 cannot be distinguished reliably, they must share one visual band while UI still shows exact numeric level.

Compare:
A duplicated material per level
B shared material + per-renderer parameter method that fits current project
C optional lookup-table/texture method if B harms batching

Use Frame Debugger + Profiler. The generic MPB-vs-SRP topic is closed; this test is specifically about the actual AETHERQOR enhancement shader and renderer layout.

Deliverable: `P3_ENHANCEMENT_VISUAL_BANDS.md` and final data table mapping +0..+10 to visual bands.

## P4 implementation task — 32 materials / 53 meshes
Build a complete render-cost audit of one promoted character.

Prototype:
A current 53 meshes / 32 materials
B shared materials only
C mesh merge by compatible material family
D compatible opaque equipped aggregation; keep hair/eyes/weapon/offhand/transparent groups separate only where technically necessary

Equipment remains logically modular. Render aggregation may be cached/rebuilt only on equipment state changes.

For A-D measure:
- renderers
- submeshes
- materials
- passes
- draw calls
- SRP batches
- SetPass/state changes
- texture resident bytes
- CPU render/main thread
- GPU ms
- 1/5/10 characters

Do not set a hard target such as '4 materials' without measurements. Choose the smallest architecture that preserves visual quality and equip behavior.

Deliverable: `P4_CHARACTER_RENDER_ARCHITECTURE.md` and automated guardrail metrics.

## P5 implementation task — human calibration
Prepare tooling now; actual final calibration needs humans after seven class anchors exist.

1. Render every class at 64/90/128/150/220 px in actual gameplay camera.
2. Conditions:
   - black silhouette
   - silhouette + anchor
   - normal color/material
   - idle/motion clip
3. Add metric outputs:
   - IoU
   - Dice
   - modified Hausdorff or Chamfer contour distance
   - radial mass descriptor 16 sectors
   - outer_anchor_contribution
   - class anchor radial excursion
4. Build 7AFC test with randomized exposure 750 ms and controls 500/1000 ms.
5. Log correctness and response latency.
6. Generate confusion matrix and pairwise errors.
7. Calibrate automatic thresholds against actual human error; do not call IoU 0.85 an industry standard.

Deliverables: `P5_7AFC_TEST_PROTOCOL.md`, runnable test, `class_recognition_metrics.csv` and after participants respond `confusion_matrix.csv`.

## Closed topics
Do not research/redo Alpha Wrap, VDB, shell-soup remesh classes, runtime equip/hide/transmog, generic MPB vs SRP Batcher, VFX Graph, retarget, URP map packing, male/female forearm stretch, or panel-gap geometry.

## Required final files
- `FINAL_TECHNICAL_VERDICTS.md`
- `EVIDENCE_LEDGER.csv`
- `EXPERIMENT_RESULTS.json`
- `IMPLEMENTATION_PLAN.md`
- P1-P5 decision docs above

Status per problem must be one of:
`IMPLEMENTED_PASS`, `IMPLEMENTED_FAIL`, `RESEARCH_CONFIRMED_NEEDS_ENGINEERING`, `BLOCKED_EXTERNAL`.

## Commit discipline
Checkpoint after each validated problem. Never bundle all five into one unreviewable commit. Each checkpoint must include code + metrics + proof artifacts + written verdict.
