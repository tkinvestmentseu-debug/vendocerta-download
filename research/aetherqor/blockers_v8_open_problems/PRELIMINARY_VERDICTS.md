# AETHERQOR V8 — PRELIMINARY VERDICTS BEFORE VIDEO REVIEW

These are hypotheses/initial architecture decisions. Claude and ChatGPT must validate them against V8 frames, authoritative sources and real AETHERQOR experiments. `PROVEN` means supported by existing local measurement; `TESTABLE_HYPOTHESIS` means do the experiment; `OWNER_DECISION` means engineering should prepare comparable evidence but not choose art direction.

## A1 torso terraces

**PROVEN:** old Z-slice convex-envelope loft creates a structural mechanism capable of horizontal width jumps; five alternative explanations were already falsified locally.

**TESTABLE_HYPOTHESIS:** compare raw donor Alpha Wrap against torso-cropped donor Alpha Wrap. If crop removes terrace amplitude without unacceptable donor-distance/silhouette loss, donor contamination from shoulder/arm geometry is primary cause. If both preserve terraces, inspect actual donor edge noise. Only then test localized feature-aware fairing after wrap.

Required metrics: neighbor-Z step height P50/P95/P99/max; silhouette radial jitter; donor distance P95/P99; intended hard-edge displacement; SI/manifold; 90/150/300 px proof.

## A2 UV mosaic

**PROVEN:** the current 2D Gaussian cavity method turns UV seams into false edges; dilation did not fix it and random island visualization matched the artifact.

**FIRST CANDIDATE:** eliminate UV-space cavity generation. Bake geometry-space curvature/concavity. Test Blender Pointiness/Cycles, Marmoset curvature/concavity and one independent baker where available. Validate actual `MODS.B` contribution in Unity before reauthoring UVs.

**DO NOT** start by merging 461 UV islands. UV reauthoring is second-line if the correct geometry-space signal still fails.

## A3 slippers

No cause is established. Use causal chain:
`DONOR -> PRE-DECIMATION -> POST-DECIMATION -> GAMEPLAY LOD -> UNITY FRAME`.

Measure semantic features (sole, toe, heel, ankle break) and screen-space silhouette. Branch result into DONOR_AUTHORING / RECONSTRUCTION / ALLOCATION_DECIMATION / LOD_MATERIAL. Fix only identified stage.

## A4 hair faceting

**PROVEN:** previous evaluation scale/material were confounded and never validated in Unity.

**RULE:** no sixth geometry change before correct measurement.

Experiment: existing mesh, same camera/lighting, Unity 6 URP, current material vs anisotropic hair material, char 90/150/300 px, moving camera and directional light. Also downscale old proofs first as zero-cost sanity check. If defect disappears at target scale/material, close geometry debt. If it survives, use V4/V5 card-layer evidence to localize geometric cause.

## A5 Ember_M pauldron anomaly

15,208 source tri vs ~1,052 class/slot norm must be treated as provenance anomaly before any allocator discussion. Add preflight outlier gate. Inspect connected components, bbox, source path/hash, generator metadata and anatomical overlap. Do not simply crush 76x again.

## B1 / C2 gender architecture

Engineering can prepare two production proofs without selecting art policy:

- `SAME_IDENTITY_REFIT`: preserve class armor macroform while fitting female clearance/deformation.
- `SEX_SPECIFIC_FORM`: intentionally distinct female form but preserve class primary characteristic, material language and gameplay recognition.

Compare class recognition, donor/class similarity, collisions, animation and production cost. Owner chooses policy.

Avoid naive shrink-wrap of rigid armor onto breast surface; fit clearance shell while preserving armor planes/macro silhouette.

## B2 FBX materials

Strong candidate architecture: FBX is geometry/skeleton carrier plus stable semantic material slot names; Unity Material assets are authoritative. Use deterministic importer remap (`SearchAndRemapMaterials` / `AddRemap` / AssetPostprocessor) against a checked-in material manifest.

Pilot on the known failing underlayer/eyes/skin/AQ_CATCH/bracer cases, then all 14. Fail import if a required semantic material cannot be resolved. QA render flags must no longer hide importer loss.

## B3 skinned merge

Strong candidate: build or adapt an audited combine path, using MIT UMA as primary reference. Merge only compatible skinned groups sharing the same skeleton/material family. Cache on equipment changes, never every frame.

Validation cannot be bind-pose-only. For 21 clips compare deformed output before/after, including extreme joints. Record bone mapping, weights and bindposes. If any `.001` ambiguity or missing bone occurs, hard fail.

## B4 anchor size

Reject universal 68% rule. Garen measurements are a reference example, not a standard. Optimize `primary identity cue` for actual game camera using outer contour contribution, radial excursion, recognition, collision and animation stability. Correct bone ownership is part of anchor design.

## B5 weapon slot

Technical direction: add `weapon` and likely `offhand` as first-class equipment/render identity slots because current budget already reserves them and production guidance treats weapons as strong readability cues. Art scope of seven unique weapons remains owner/production decision.

## B6 Frost shield

First diagnose transform/parenting semantics. A worn shield with 0 body/gear proximity over intended poses is likely attachment/positioning failure, but confirm intent. Measure local transform, parent bone, closest surface distance and animation trajectory before redesign.

## C1 human calibration

Build complete 7AFC tooling now. Human responses remain external dependency only for threshold calibration. Do not let absence of participants block A1-B6 engineering.

## C3 visual bands

Separate exact gameplay rank count (7) from visible material bands. Shader/data must support configurable 2/3/4+ bands. Compare day, night, no-bloom and controlled exposure. Global Bloom cannot be the only visual signal. Owner chooses final count after side-by-side evidence.

## Cross-cutting QA additions

Create or extend:
- `TERRACE_STEP_HEIGHT`
- `GEOMETRY_CURVATURE_SEAM_SCORE`
- `FOOTWEAR_SEMANTIC_READ`
- `HAIR_TARGET_SCALE_TEMPORAL_READ`
- `SOURCE_PROVENANCE_OUTLIER`
- `MATERIAL_REMAP_COMPLETENESS`
- `SKINNED_MERGE_ANIM_REGRESSION`
- `ANCHOR_OUTER_CONTOUR_CONTRIBUTION`
- `ANCHOR_ANIMATION_COLLISION`
- `WEAPON_SLOT_CONTRACT`
- `ATTACHMENT_DISTANCE_OVER_ANIMATION`

No final PASS without a real AETHERQOR asset and proof at target gameplay scale.
