# AETHERQOR V6 URGENT RESEARCH QUESTIONS — 2026-09-05

Constant context: mobile AAA, Unity 6 URP, Blender 5.2, 7 classes x 2 sexes, target gameplay character size 90–300 px. Current universal triangle target is 14,000, but this is now under review.

## P1 — CHARACTER TRIANGLE ARCHITECTURE

Measured local state:
- 12 integrated post-Solidify hard-surface objects consume 12,535 / 14,000 triangles.
- 1,465 triangles remain for body, hair, underwear and six cloth layers.
- minimum allocation floor for remaining objects is 2,200 triangles, therefore the current contract is mathematically impossible.
- low variants such as 595-triangle cuirass and 358-triangle helmet visibly facet despite smooth shading; donor normal maps recover surface detail but not silhouette.

Questions to resolve:
1. Is 14k a sensible UNIVERSAL full-character target for a current high-budget mobile RPG, or should quality be context/device/screen-size dependent?
2. What evidence exists for player-character mesh sizes in Genshin Impact, Wuthering Waves, Diablo Immortal and Black Desert Mobile? Distinguish official/first-party evidence from extracted/reuploaded meshes.
3. How should AETHERQOR allocate triangles across body, rigid armor, cloth, hair and weapons when the character is 90/150/220/300 px tall?
4. How many logical equipment slots need geometry simultaneously? Build an assembled-outfit visibility matrix rather than blindly summing all catalog slot budgets.
5. Decide whether 14k should remain a low/gameplay LOD, be raised, or be replaced by a measured quality ladder.

Required experiment on ONE real complete outfit:
- generate total visible assembled variants at 14k, 20k, 28k, 40k;
- render identical animation/key poses at 90, 150, 220, 300 px plus equipment close-up;
- measure silhouette error, contour error, visible faceting, animation clipping, total rendered triangles/vertices, SkinnedMeshRenderer count, draw calls and GPU cost on the best target-like mobile profile available;
- choose the lowest variant that is visually indistinguishable enough in its intended context.

## P2 — RIGID GEAR THICKNESS / SOLIDIFY ARCHITECTURE

Measured local state:
- full Solidify doubles most hard-surface shell triangle counts approximately 2x because every outer plate gets a complete inner surface.
- the current budget crisis is therefore strongly coupled to thickness architecture.

Hypothesis to test:
ONE-SIDED OUTER SHELL + BACKFACE CULLING ON + LOCAL SIDEWALL/RIM GEOMETRY ONLY WHERE THICKNESS IS VISIBLE.

Questions:
1. Do production game-resolution armor pieces use full internal shells everywhere, or selectively model thickness only on exposed edges/openings?
2. How should an edge be constructed so a plate does not read as paper at grazing angles without creating a full duplicate inner shell?
3. When is Render Face Both / Cull Off appropriate, and how does its real GPU cost differ from full double geometry?
4. Which armor regions truly expose the inside surface under gameplay/equipment cameras and animations?

Required A/B/C test on cuirass + helmet + shoulder:
A. current full Solidify;
B. one-sided outer shell, Cull Back/Render Face Front;
C. one-sided outer shell + local boundary sidewalls/rims and only necessary inner patches.

Measure triangles, post-split vertices, renderer count, GPU time, visible holes, rim readability at 90–300 px and equipment close-up, shadow behavior and animation clipping.

## P3 — FREE CONTROLLED REDUCTION + MODULAR SEAM CONTRACT

Measured local state:
- current whole-character common ratio performs a destructive second reduction on parts already built to target;
- shoulder edge loops go 16/16 -> 11/11 and 11/12, losing symmetry;
- trouser/leg geometry develops stair-step artifacts;
- Decimate Planar with Sharp delimit worsened cuirass self-intersection 3.16% -> 5.78%.

Questions:
1. What free Blender/Python tool can emulate importance/vertex-weight-controlled reduction?
2. Can Blender Decimate Collapse + Vertex Group protect selected regions strongly enough for production?
3. Can CGAL Surface_mesh_simplification constrained edges provide a deterministic hard lock on modular seams?
4. How can 19 modular pieces be reduced independently while keeping their mating borders numerically identical?
5. How should the GLOBAL budget be solved without applying a single ratio to all parts?

Required implementation prototype:
- add canonical seam IDs and ordered seam-coordinate hashes;
- protect seam edges plus at least one adjacent ring;
- simplify slot interiors independently;
- verify seam vertex count, coordinates and order after reduction;
- fail the build if a protected seam changes;
- replace global ratio with slot candidate levels and a global allocator minimizing screen-space error subject to total budget.

## P4 — HAIR CARD OCCLUSION REGULARITY AT ~1800 TRI

Measured local state:
- five hair styles fit 1626–1974 tri, scalp exposure 1.11–2.43%.
- crown faceting is caused by regular occlusion boundaries between overlapping flat main/underlay cards.
- rejected by measurement: scalp normal transfer, cap-only SEG increase, solid scalp dome as previously built, duplicated inverted normals.

Questions:
1. How do production hair-card systems break regular row boundaries: staggered roots, variable length/width, curvature, layer hierarchy, breakup cards?
2. At ~1800 tri, how should budget be allocated among hidden/core coverage, primary silhouette/shape, secondary breakup and flyaways?
3. What should be used in URP mobile at ~100 px in MOTION: Alpha Clip, dithered cutout, or Alpha Blend?
4. Can an opaque scalp/inner-hair base be used without repeating our failed protruding solid dome? If so, how must its hairline/shape be trimmed and hidden?

Required controlled variants for one failing style, same ~1800-tri envelope:
A. current regular flat overlap;
B. staggered row phase + varied lengths;
C. curved high-importance primary cards + reduced low-value overlap geometry;
D. trimmed opaque inner coverage + layered alpha-tested cards;
E. best geometry variant under Alpha Clip / Dither / Alpha Blend.

Test stills AND camera motion at 90/100/150/220 px, multiple lights and 1/5/10 characters. Measure scalp exposure, silhouette, temporal flicker, sorting errors, overdraw and GPU time.

## P5 — CLASS IDENTITY FROM TOP-DOWN GAMEPLAY CAMERA

Measured local state:
- existing mask gate passes: 0/21 class pairs above IoU threshold across six views.
- nevertheless at azimuth 35°, elevation 50°, classes without a long diagonal feature (mage coat, hooded seer) can become similar dark blobs.
- existing anchor >=10% of mask does not guarantee that the anchor changes the OUTER CONTOUR.

Questions:
1. How do top-down games combine silhouette, pose, weapon/prop, value, color, material and VFX for recognition?
2. Is there any published universal IoU threshold correlated with human character recognition? If not, how should AETHERQOR calibrate its own threshold?
3. What metric measures whether an anchor actually contributes to the visible contour rather than merely occupying area inside the torso silhouette?
4. What top-view mass distribution should classes without protruding weapons use?

Required test:
- real gameplay camera 35° azimuth / 50° elevation;
- 64, 90, 128, 150, 220 px;
- black silhouette, silhouette+prop, normal material/color, idle pose, optional restrained class VFX;
- metrics: IoU, Dice, robust Hausdorff, contour Chamfer, radial/sector descriptor, outer-contour anchor contribution, negative-space descriptors;
- local timed human 7-choice recognition test and confusion matrix.

## CLOSED TOPICS — DO NOT SPEND RESEARCH BUDGET

- Alpha Wrap is solved locally: pip-installable cgal, no compile; cuirass mean donor distance 0.99 mm vs 6.32, P99 5.72 vs 48.35, watertight, silhouette IoU 0.984/0.961/0.982; 1500 tri beats old 2600 pipeline.
- VDB failed 9/9 parameter combinations with 349–7652 components.
- ZRemesher / Quad Remesher / Quadriflow / QRemeshify are not soup-reconstruction solutions for this problem.
- 3–8 mm armor gaps at 2600 tri are moved to normal/baked detail after 42 failed geometry combinations.
- runtime equipment, hide masks, transmog, MaterialPropertyBlock vs SRP Batcher, mobile VFX Graph decision, retargeting and URP map packing are closed.

Final objective: produce production decisions and runnable changes, not another literature summary.
