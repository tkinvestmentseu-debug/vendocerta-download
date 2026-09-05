# AETHERQOR V8 — OPEN PROBLEMS ULTRA RESEARCH + IMPLEMENTATION HANDOFF

Local root after workflow success:
`D:\AetherqorFoundry\research\blockers_v8_open_problems\ULTRA_RESEARCH_2026-09-05_OPEN_PROBLEMS`

## Mission
Resolve ALL A1-A5, B1-B6 and C1-C3 from `QUESTIONS.md`. V8 is not another generic report. Every technically resolvable item must end in an AETHERQOR experiment, code/asset change where justified, metrics and regression proof.

Required loop:
`SOURCE READ -> FORUM/GITHUB REVIEW -> VIDEO FRAME REVIEW -> CURRENT AETHERQOR FORENSICS -> HYPOTHESIS -> CONTROLLED EXPERIMENT -> REAL ASSET -> UNITY/BLENDER METRICS -> PROOF RENDER/VIDEO -> VERDICT -> IMPLEMENTATION -> REGRESSION QA -> CHECKPOINT COMMIT`

## Mandatory read order
1. `LOCAL_READY.md`
2. `QUESTIONS.md`
3. `CHATGPT_INDEPENDENT_ANALYSIS.md`
4. `PRELIMINARY_VERDICTS.md`
5. `SOURCE_REGISTRY.md`
6. `GITHUB_CANDIDATES.md`
7. `FINAL_STATUS.md`
8. `videos.psv`
9. all V8 video evidence using protocol below
10. relevant V3-V7 local packages
11. current AETHERQOR source/assets/contracts/forensics

## Video protocol — every V8 slug
1. `manifest.json`
2. `transcript.txt` or `TRANSCRIPT_MISSING.txt`
3. `frame_index.csv`
4. `sheet_index.csv`
5. `high_detail_index.csv`
6. ALL `contact_sheets_3x3` sequentially
7. selected raw `frames_1fps` around relevant moments
8. `high_detail_4fps` where visual technique, shading, animation or engine state matters

Never infer a visual fact only from transcript. Record every used fact in `EVIDENCE_LEDGER.csv`:
`problem,slug,source_url,timecode,sheet,frame,fact_shown,application,confidence,local_test`.

## External code protocol
For every GitHub candidate write a row to `EXTERNAL_CODE_EVALUATION.csv`:
`repo,commit_or_tag,license,problem,feature_used,adopt_port_reference_reject,reason,test_result`.

License gate is mandatory. No-license repositories are REFERENCE_ONLY. Do not silently vendor them.

## A1 — torso terraces
Implement a causal experiment, not another blind smoothing pass:
- raw donor Alpha Wrap control;
- semantically torso-cropped donor Alpha Wrap;
- calculate neighbor-Z terrace step P50/P95/P99/max and silhouette jitter;
- compare donor distance P95/P99 and intended feature-edge retention;
- if needed, local feature-preserving fairing ONLY on detected terrace regions after cause is proven.
Deliver: `A1_TORSO_TERRACE_DECISION.md`, metric CSV and 90/150/300px proofs.

## A2 — UV mosaic
Replace current 2D Gaussian cavity experiment with geometry-derived curvature controls. Compare Blender Pointiness, Marmoset curvature/concavity and one independent equivalent if available. Pack result into the actual runtime `MODS.B` path and render Unity debug controls: B=0/B=1/current/new/amplified. Do not rebuild UV until this test says it is needed. If needed, run xatlas/UV alternative on duplicate and measure chart count, distortion, density, seam score and bake error.
Deliver: `A2_CURVATURE_RUNTIME_DECISION.md`.

## A3 — slippers
Build causal four-stage footwear audit:
`DONOR -> PRE_DECIMATION -> POST_DECIMATION -> GAMEPLAY_LOD`.
Measure sole thickness, toe projection, heel height/projection, ankle break, boundary condition, triangles and screen-space silhouette at 90/150/300. Fix only the stage that destroys the feature. Add automated semantic footwear guard.
Deliver: `A3_FOOTWEAR_READABILITY_DECISION.md`.

## A4 — hair
Do NOT edit hair geometry before correcting measurement. Downscale existing proof first. Then same hair mesh in Unity 6 URP:
A current material;
B minimal port of CC0 Fulcrum anisotropic model;
C optional MIT anisotropic Shader Graph reference.
Test 90/150/300px character, camera orbit, moving light and animation. Measure temporal shimmer/crown contrast/GPU cost/overdraw. Only reopen card geometry if defect persists.
Deliver: `A4_HAIR_TARGET_SCALE_DECISION.md`.

## A5 — Ember_M pauldron
Trace source provenance and build slot-source outlier preflight. Compare 15,208 source to slot/class median; components, spatial spread, anatomical overlap, path/hash/generator. Fix routing/isolation if wrong; if genuine complexity, rebuild intentionally rather than 76x blind collapse.
Deliver: `A5_SOURCE_PROVENANCE_DECISION.md`.

## B1/C2 — M/F
Prepare two comparable production proofs:
- SAME_IDENTITY_REFIT
- SEX_SPECIFIC_FORM
Preserve class primary characteristic and evaluate top-down recognition, donor/class similarity, animation/deformation, collision and production cost. Do not decide art policy for owner. Avoid body-hugging rigid 'boob plate' shrinkwrap; preserve armor macro planes and use clearance fitting.
Deliver: `B1_C2_GENDER_ARCHITECTURE_OPTIONS.md` with owner-decision matrix.

## B2 — FBX materials
Make actual Unity import deterministic. Prototype semantic material naming + checked-in manifest + AssetPostprocessor/ModelImporter remap using supported Unity APIs. Test known failures: underlayer, eyes, skin, AQ_CATCH L/R, bracer material slots. Validate all 14. Remove reliance on QA rescue flags as proof of importer correctness.
Deliver: `B2_MATERIAL_IMPORT_CONTRACT.md` and automated import validator.

## B3 — SkinnedMeshRenderer aggregation
Use MIT UMA and other license-safe sources as references. Pilot one promoted character. Canonical skeleton mapping, source->destination bone remap, bindposes, weights, blendshapes, UV/normals/tangents/submeshes/material families. Hard-fail `.001` ambiguity. Regression across current 21 animation clips in non-bind poses. Measure source vs merged visual/deformation error and Unity performance on 1/5/10 chars. Combine/cache on equip state changes, never every frame.
Deliver: `B3_SKINNED_AGGREGATION_DECISION.md`.

## B4 — class anchor
Do not implement universal 68% anchor height. Test real gameplay camera. For each class compute outer contour contribution, radial excursion, occupied pixels at 90/150/300, animation motion signature and collision/clipping across clips. Ensure anchor bone ownership matches intended movement. Decide per class primary identity cue.
Deliver: `B4_CLASS_ANCHOR_CONTRACT.md`.

## B5 — weapon slot
Implement a technical prototype of first-class `weapon` and `offhand` equipment/render slots with budget, attachment semantics, LOD, material family and QA. Reuse a working existing weapon as pilot before generating seven assets. Owner chooses production scope after proof.
Deliver: `B5_WEAPON_SLOT_DECISION.md`.

## B6 — Frost shield
Open the actual file. Audit hierarchy, parent bone, transforms, bounds, nearest body/gear distance, intended attachment markers and trajectory through idle/run/combat. Compare to a correct backpiece. Fix transform/attachment if accidental; if intentionally floating, require explicit floating visual-language specification rather than silent 0% contact.
Deliver: `B6_FROST_SHIELD_ATTACHMENT.md`.

## C1 — recognition humans
Build complete 7AFC app/trial generator now: 500/750/1000ms; 64/90/128/150/220px; silhouette, +anchor, normal color/material, motion. Output trials/results/confusion/latency. Until people participate, only final threshold calibration may be `BLOCKED_EXTERNAL`.
Deliver: `C1_7AFC_PROTOCOL.md` and runnable harness.

## C3 — visual rank bands
Keep seven gameplay ranks exact. Build configurable visual band mapping and compare 2 vs 3 vs 4 bands under daylight/night/neutral and Bloom on/off. Do not make global Bloom the only carrier. Owner chooses final visual progression after comparison matrix.
Deliver: `C3_VISUAL_BAND_OWNER_DECISION.md`.

## Closed topics
Do not re-research whether Alpha Wrap works as soup solver; it works and may be USED. Do not repeat VDB/QRemeshify/Quadriflow/general remesher soup tests, generic MPB-vs-SRP, VFX Graph, retarget or URP channel packing.

## Required final package
- `FINAL_TECHNICAL_VERDICTS.md`
- `EVIDENCE_LEDGER.csv`
- `EXTERNAL_CODE_EVALUATION.csv`
- `EXPERIMENT_RESULTS.json`
- `IMPLEMENTATION_PLAN.md`
- all A1-A5/B1-B6/C1/C3 decision docs above
- `C2` owner decision included with B1

Status only: `IMPLEMENTED_PASS`, `IMPLEMENTED_FAIL`, `RESEARCH_CONFIRMED_NEEDS_ENGINEERING`, `BLOCKED_EXTERNAL`.

Checkpoint commit after each validated problem or tightly coupled pair. Do not bundle V8 into one commit. Preserve raw donors and known-good assets; experiments go under existing research/proof/QA artifact structure.
