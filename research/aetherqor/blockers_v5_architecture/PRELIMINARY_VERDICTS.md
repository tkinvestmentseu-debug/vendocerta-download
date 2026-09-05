# AETHERQOR V5 — PRELIMINARY VERDICTS

These are STARTING HYPOTHESES, not final decisions. Claude must verify them against local video evidence and AETHERQOR experiments.

## P1 — 14k architecture

HYPOTHESIS A: 14k is probably too low as a single universal hero/equipment budget for a modern high-end mobile character with body + hair + layered cloth + many hard-surface slots. Public extracted/re-uploaded character models from current high-end mobile titles frequently sit well above 14k, but provenance varies and those counts cannot be treated as official budgets.

HYPOTHESIS B: the more important architectural mistake may be using one geometry budget for every presentation context. Official Simplygon mobile guidance explicitly recommends higher-detail character versions when the character is the focus and lower-resolution versions in gameplay. AETHERQOR should test at least GAMEPLAY_LOD versus EQUIPMENT/HERO_LOD rather than forcing one 14k asset to solve both.

HYPOTHESIS C: global Solidify on every hard slot is likely structurally wasteful. It doubles many plate triangle counts even when inner surfaces are not visible. Do NOT simply switch Cull Off globally: Unity states back-face culling saves GPU work. Test one-sided exterior shells with thickness only on visible rims/openings and compare to full Solidify and two-sided rendering.

HYPOTHESIS D: logical equipment slots should not automatically equal simultaneous geometric layers. Audit which slots truly contribute visible geometry and which can share/merge shells or be represented by textures/hide masks.

## P2 — shell soup

PROVEN_FROM_PRIMARY_DOCS: CGAL Alpha_wrap_3 accepts triangle soups directly and promises a watertight, 2-manifold, intersection-free enclosing output. Alpha controls feature/cavity penetration scale; offset controls tightness/distance.

HYPOTHESIS: Alpha Wrap is the strongest candidate for a generic validity-reconstruction stage, but it may close 3-8 mm panel gaps or erase concavities depending on alpha/offset. It must be tested in world units on the real cuirass and shoulder. Do not call it solved until the parameter sweep demonstrates acceptable gap/concavity retention and post-reduction quality.

HYPOTHESIS: Houdini VDB is the strongest alternative because unsigned distance fields can consume non-watertight/self-intersecting/kit-bashed geometry, but voxel size and topology conversion may blur the exact features Alpha Wrap preserves geometrically.

## P3 — second-pass decimation

HYPOTHESIS: whole-character blind re-decimation is the wrong architecture for already-approved modular slots. Production-oriented tools expose vertex importance, skinning-aware reduction and modular seam preservation specifically because not all regions/parts should be reduced uniformly.

Candidate architecture to prove:
1. each slot has min/target/max and protected features;
2. global budget allocator decides how many triangles each slot may spend based on screen-space importance and current outfit;
3. slot reducer is forbidden from crossing hard minimums/protected boundary loops;
4. global sum is solved by reallocating between parts, not by an uncontrolled second pass over the assembled character.

## P4 — hair

PRODUCTION_BREAKDOWN EVIDENCE: realistic real-time hair workflows often use an opaque/base coverage layer near the scalp, then breakup/transitional/flyaway layers. This is consistent with the AETHERQOR diagnosis that card layering/occlusion structure matters more than transferred normals.

HYPOTHESIS: AETHERQOR's faceting is likely created by coarse planar overlap boundaries in main/underlay layers. The next experiment should vary card curvature, overlap depth ordering and opacity architecture while holding total triangles roughly constant. Do not repeat scalp-normal transfer or cap-only SEG increases.

HYPOTHESIS: Alpha Blend is unlikely to be the default mobile gameplay answer because Unity explicitly warns about alpha blending/overdraw on mobile. Test Alpha Clip/Dither/Blend in the actual crowded gameplay scene, not a single head render.

## P5 — top-down class identity

HYPOTHESIS: a silhouette-only metric that passes front/side/3-4 masks can still fail the actual 35deg azimuth / 50deg elevation gameplay camera. The production contract should include the actual gameplay camera and a recognition/confusion test.

HYPOTHESIS: classes without a weapon/prop protruding into the top-down footprint may need a deliberate top-view anchor OR another strong identity channel such as color/material/VFX/animation. Do not force arbitrary spikes or weapons without proving that silhouette is the identity channel that matters at 90-300 px.

## Required final output

For each problem Claude must label the final statement as PROVEN, LIKELY, or NOT PROVEN, and attach:
- source evidence,
- local AETHERQOR measurement,
- experiment,
- before/after metric,
- production decision.
