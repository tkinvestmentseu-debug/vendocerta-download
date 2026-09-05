# AETHERQOR V7 — PRELIMINARY VERDICTS

These are hypotheses to test, not final truth. Claude must confirm/falsify with video evidence, local project measurements and proof renders/build profiling.

## P1 tiers

Likely production architecture: shared base material families + shared trim/atlas textures + per-slot UV regions + compact mask channels + tier parameters, not unique full PBR texture set per slot per tier.

Proposed first AETHERQOR tier encoding:
- BaseColor/Normal/Mask shared per class/material family where possible.
- Mask RGBA: R metal accent region, G leather/cloth secondary region, B rune/enhancement region, A optional wear/detail/tier selector depending shader needs.
- Tier data table controls palette, metallic/smoothness offsets, emission intensity/color and optional detail-normal scale.
- Unique texture only when silhouette/ornament topology or genuinely unique painted content changes materially.
- Keep hair/eyes/skin separate from opaque gear atlas unless an actual bake/merge test proves acceptable close-up quality.

Required test: current 32 materials / 53 meshes vs three architectures: A current, B shared material families without mesh merge, C gameplay aggregate/atlas after equip. Measure texture memory, draw calls, SRP batches, build size, 1/5/10 characters, 90/150/220/300 px and equipment closeup.

Do not set a universal material-count target from internet anecdotes. Derive target from actual device profiling, but 32 materials on one character is high enough to justify a focused merge experiment immediately.

## P2 rings and micro-props

Likely rule: route by projected screen footprint and silhouette contribution, not by asset category name.

First gate to test:
- if feature changes silhouette by <1 px in gameplay views and occupies <4-9 pixels total, default BAKE_ONLY or REMOVE from gameplay LOD;
- 1-2 px persistent high-contrast feature: test texture/normal first;
- geometry only if it causes a stable silhouette/occlusion cue at target view or must physically deform/swing;
- equipment/inspect model may retain a dedicated close-up version.

The exact thresholds above are AETHERQOR experiment values, not industry standards. Build an automated projected-size report for every micro-prop across 90/150/220/300 px.

## P3 +0..+10 enhancement

Strong candidate: one existing Lit/ShaderGraph material path with a baked enhancement mask and parameterized emission/color/smoothness. Do not create 11 materials or 56 renderers unless measured visual evidence requires it.

Likely visual compression: +0..+10 maps to 3-4 perceptual tiers in gameplay, while UI displays the exact numeric level. Candidate grouping for test only:
- 0-2 neutral
- 3-5 subtle accent
- 6-8 strong accent
- 9-10 premium/max accent

Test 11 raw levels in randomized pairwise/ordered video at 90/150/220/300 px. If adjacent levels are not distinguishable above chance, collapse them. Exact number must come from the AETHERQOR test.

Unity test must compare material instance proliferation vs shared material + parameter path and inspect Frame Debugger/SRP Batcher behavior on the actual URP shader.

## P4 materials and renderers

Do not conflate SRP Batcher with draw-call merging. Shared shader variants reduce CPU setup, but separate renderers/submeshes/material passes still need actual measurement.

Candidate architecture:
- authoring: keep 19 logical slots modular;
- runtime equipment mutation: keep logical slot data separate;
- render representation: rebuild/aggregate opaque equipped parts into one or a few skinned render groups after equipment changes, not every frame;
- preserve separate groups for hair/transparency, eyes/face if required, weapon/offhand if independently animated, and materials requiring distinct shader state;
- hide/remove covered body triangles before aggregation where already supported by project masks.

First experiment: current 53 meshes/32 materials versus grouped target of OPAQUE_GEAR, BODY/SKIN, HAIR, EYES/FACE, WEAPON/OFFHAND, TRANSPARENT_SPECIAL. Target counts are provisional; proof comes from Frame Debugger and mobile profile.

## P5 class recognition

IoU <=0.85 is insufficient by itself. Keep it as one diagnostic, not the acceptance gate.

Add:
- modified Hausdorff or Chamfer contour distance;
- outer-anchor contour contribution: how much final external contour is created by the class anchor;
- radial mass descriptor in 8 or 16 sectors from projected centroid;
- value/color block descriptor for normal gameplay render;
- 7AFC human confusion matrix and response time.

Human protocol:
- 7 classes, randomized;
- 0.75 s default exposure, also 0.5 and 1.0 s pilot;
- 64/90/128/150/220 px;
- stages: black silhouette -> silhouette+anchor -> normal color/material -> idle pose/motion clip;
- at least 5-10 people is enough for a first calibration signal, not for academic publication;
- derive thresholds from confusion, especially Mage<->Seer, rather than inventing a universal Hausdorff/IoU cutoff.

Add metric `outer_anchor_contribution = contour_length_attributed_to_anchor / total_contour_length`; anchor-area >=10% can pass while contributing zero to recognition if fully inside the robe mass.

## Execution priority

1. P1/P4 together: tier/material architecture because it can prevent hundreds of texture sets and dozens of draw calls.
2. P2 micro-prop gate before mass-running rings on 14 characters.
3. P3 enhancement mask architecture before expanding 56 profiles.
4. P5 human-test tooling can be prepared now; actual calibration needs people and should run after seven class anchors exist.

Final allowed labels: PROVEN, LIKELY, FALSIFIED, NEEDS_AETHERQOR_TEST, BLOCKED_EXTERNAL.
