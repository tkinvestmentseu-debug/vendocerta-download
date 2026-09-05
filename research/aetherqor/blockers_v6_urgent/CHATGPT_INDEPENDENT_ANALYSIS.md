# AETHERQOR V6 — CHATGPT INDEPENDENT TECHNICAL ANALYSIS

Status legend:
- PROVEN_EXTERNAL: supported by authoritative external source.
- PROVEN_LOCAL: supported by AETHERQOR measurement supplied in the brief.
- STRONG_HYPOTHESIS: architecture is well supported but still needs local A/B measurement.
- NOT_PROVEN: do not present as fact.

## Executive decision

The dominant architectural mistake is very likely not 'bad decimation'. It is the attempt to force every assembled character context into one fixed 14k envelope while simultaneously paying full internal thickness on hard gear and then applying a second global reduction to already-approved slot meshes.

The recommended architecture is:
1. character quality ladder chosen by screen size/context/device, not one universal count;
2. rigid plates modeled primarily as outer shells with local rim/sidewall thickness rather than full hidden inner copies;
3. per-slot reduction with hard seam/feature constraints plus a global allocator, not a global ratio;
4. hair as a layered depth/geometry problem with an opaque hidden core and irregular curved visible cards, not a normals problem;
5. top-down class identity judged by actual contour contribution + value/color/weapon/pose channels and human recognition, not IoU alone.

These are engineering decisions to test, not permission to skip measurement.

# P1 — CHARACTER TRIANGLE ARCHITECTURE

## What is proven

PROVEN_LOCAL: 12,535 post-Solidify gear triangles leave only 1,465 of the 14k contract, below the stated 2,200 floor for remaining geometry. The current contract cannot be satisfied without violating its own minima.

PROVEN_EXTERNAL: current Simplygon mobile guidance explicitly recommends different optimization variants for low/mid/high devices and notes that character-centric mobile games often use a high-detail focus character and a lower-resolution gameplay version. It also recommends reviewing in actual mobile/camera context.

PROVEN_EXTERNAL: Simplygon recommends OnScreenSize or geometric deviation over one triangle ratio/count because different assets tolerate reduction differently.

PROVEN_EXTERNAL: Valve's top-down production pipeline has separate lower gameplay geometry and higher close/showcase geometry. There is no architectural reason for AETHERQOR to force equipment-closeup quality and 90px gameplay quality into one mesh count.

NOT_PROVEN: exact official LOD0/player-character triangle counts for Diablo Immortal, Genshin, Wuthering Waves and Black Desert Mobile. No trustworthy first-party limits were found. Public mesh reuploads are inconsistent and often lack LOD/export provenance.

## What the weak extracted numbers actually tell us

Some Wuthering Waves reuploads cluster around ~30–36k triangles while others are ~90–103k. This spread is itself more useful than pretending one number is official: it demonstrates that source/version/accessory/LOD provenance matters. AETHERQOR must not pick 14k because 'mobile characters are 14k' unless a first-party source exists.

## Recommended AETHERQOR contract

Do not immediately replace 14k with another arbitrary single value. Reclassify 14k as a CANDIDATE gameplay-low tier and test a quality ladder:

- Q0: 14k total visible character triangles.
- Q1: 20k.
- Q2: 28k.
- Q3: 40k.

This is an experiment envelope, not an industry standard.

Suggested usage hypothesis before measurement:
- 90–120 px / many characters: likely Q0–Q1.
- 150–220 px normal hero gameplay: likely Q1–Q2.
- 220–300 px hero-focused gameplay: likely Q2.
- equipment/portrait close-up: Q3 or separate hero mesh.

If Q1 is visually equivalent to Q2 at 150 px, choose Q1. If Q2 still facets at 300 px, do not force 300px to use Q2. Screen-space error decides.

## Required visibility audit

Logical slot count is not equal to simultaneously visible geometry. Build `assembled_visibility.csv` for a real outfit with columns:
- object / logical slot
- triangles outer
- triangles hidden-inner
- visible gameplay 35/50 camera yes/no
- visible equipment camera yes/no
- hidden by body mask yes/no
- hidden by another gear layer yes/no
- active renderer yes/no
- material count
- skinned/static

Compute three sums:
1. catalog triangles,
2. assembled renderer triangles,
3. actually visible triangles under the target camera/body hiding.

The budget must be based on #2 and validated against #3, not the sum of every conceptual slot maximum.

## Quality-selection metric

For each 14/20/28/40k assembled variant render the same animation frames at 90/150/220/300 px and calculate:
- binary silhouette IoU against 40k reference,
- 95th percentile contour Hausdorff normalized by character height,
- edge-map difference on rigid gear,
- visible polygon faceting score using image gradient discontinuity on known smooth curved surfaces,
- animation clipping count,
- GPU frame time and vertex count.

Add blind A/B human comparison: reference vs candidate for 0.5–1.0 s. If users cannot reliably distinguish the higher mesh in the intended gameplay context, the lower mesh wins.

# P2 — RIGID ARMOR THICKNESS

## Core conclusion

STRONG_HYPOTHESIS: full Solidify on every hard plate is architecturally wasteful. The likely production solution is outer shell + true geometric sidewall only where thickness can enter the camera silhouette/opening, plus selective inner patches only where the inside can really be seen.

PROVEN_EXTERNAL: Unity URP defaults to rendering front faces and culling backs. Render Face Both is an explicit option for thin flat objects. Valve's top-down item guide says backface polygons should be added where necessary rather than implying every surface needs a complete inner copy.

PRODUCTION BREAKDOWN: game-character workflows commonly start from single-sided surfaces and add/extrude side thickness where it actually matters, deleting unseen internal topology.

## Important GPU nuance

Do NOT equate these three architectures:
A. a one-sided shell with backface culling;
B. the same one-sided shell with culling disabled;
C. full Solidify with a complete inner shell.

Cull Off does not magically double vertex count. It prevents winding-based face rejection, so back-facing triangles that would be discarded can rasterize. Full Solidify actually creates additional vertices/triangles and sidewalls and sends them through skinning/vertex processing. On tile-based mobile GPUs, extra backfaces/transparency/overdraw can still be expensive, so Cull Off is not 'free'. Measure both vertex and fragment cost.

For rigid armor, preferred default is A/C hybrid: Front-face culling ON plus local sidewalls. Use Render Face Both only where a genuinely paper-thin two-sided surface is intended, such as some cloth/hair cards.

## Local rim algorithm

For each rigid outer shell:
1. identify exposed boundary loops and explicit openings;
2. classify each boundary segment by camera visibility using sampled gameplay/equipment cameras and animation poses;
3. create an inner duplicate only for boundary vertices at a small physical inset/thickness;
4. bridge outer boundary to inset boundary with quads/triangles, creating the plate sidewall;
5. extend the inset inward only 1–2 rings if needed for grazing views; do NOT cap the whole back surface unless the interior is visible through an opening;
6. mark the outer/sidewall crease for hard/weighted normals as required;
7. bake donor normals/AO onto the final low mesh.

This changes approximate cost from `outer surface + almost full inner surface + border walls` to `outer surface + narrow border walls + occasional inner patches`. Exact savings depend on boundary complexity; do not claim 50% until measured.

## Acceptance test

For cuirass/helmet/shoulder compare:
- full Solidify;
- outer only;
- outer + local rim.

Use 24-angle turntable plus gameplay 35/50 camera and equipment close-up. Include attack/idle animations that expose armpit/neck/waist openings. PASS requires no paper edge/hole at intended cameras while saving enough triangles to materially improve the assembled budget.

# P3 — CONTROLLED FREE REDUCTION / MODULAR SEAMS

## Best free stack

### Level 1: Blender native, zero external dependency

PROVEN_EXTERNAL: Blender 5.2 Decimate Collapse exposes Vertex Group + Factor. Use it first for soft importance weighting and symmetry.

Do not assume weight direction from memory. Build a 100-triangle synthetic strip with one protected high-weight region, run two known settings, inspect which region collapses, then encode the verified semantics in an automated test. This avoids accidentally inverting protection.

### Level 2: CGAL hard constraints

PROVEN_EXTERNAL: CGAL Surface_mesh_simplification supports `edge_is_constrained_map`; constrained edges cannot collapse. `Constrained_placement` prevents constrained-border points from moving.

This is a better semantic match for AETHERQOR's non-negotiable slot seams than a soft vertex group.

First test whether the installed Python `cgal` package exposes Surface_mesh_simplification. Do not assume Alpha_wrap bindings imply all CGAL packages are exposed. If available, use Python. If absent, keep Blender as the no-build path and consider a tiny standalone wrapper only if necessary.

## Deterministic modular seam contract

Simplygon's useful idea is not proprietary magic: it analyzes a shared border once and reuses the same deterministic reduced seam for every compatible part.

Implement this free architecture:

1. Assign each mating border a `seam_id`, e.g. `forearm_hand_L`.
2. Extract the ordered seam polyline from every compatible slot.
3. Normalize orientation and compute a canonical hash of coordinates (within a very small tolerance).
4. If two slot seams differ before reduction, FAIL ASSET CONTRACT rather than trying to hide it later.
5. Choose a canonical seam simplification ONCE, based on both adjoining parts or lock the existing seam if already minimal.
6. Copy/snap that canonical seam result into every compatible slot.
7. Mark all canonical seam edges constrained and optionally protect one adjacent ring.
8. Simplify only the interior of each slot.
9. After reduction assert:
   - same seam vertex count,
   - same ordered coordinates within tolerance,
   - same endpoints/order,
   - no seam gap > tolerance,
   - no self-intersection introduced near seam.

For your shoulder regression, encode `16/16` as a hard test until a deliberately redesigned canonical seam says otherwise. A global reducer is not allowed to silently create 11/11 vs 11/12.

## Replace the global ratio with an allocator

Generate a discrete quality curve per slot instead of one ratio. Example candidate levels for each slot:
- L0 = current approved target,
- L1 = modest reduction with protected seam/silhouette,
- L2 = aggressive reduction if visually acceptable.

For every candidate level store:
- triangles,
- silhouette error at 90/150/220/300 px,
- contour error,
- deformation error,
- seam PASS/FAIL,
- visual score.

Then solve the global budget as a constrained optimization. Practical greedy version:
1. start every visible slot at its best required level;
2. compute each possible next downgrade's `error_increase / triangles_saved`;
3. choose the cheapest-error downgrade;
4. repeat until target total is met;
5. never select a downgrade that violates a hard seam/silhouette/deformation constraint;
6. if no legal downgrade remains before the target is reached, return `BUDGET_ARCHITECTURE_IMPOSSIBLE`, not a broken mesh.

This directly addresses the current failure mode.

# P4 — HAIR OCCLUSION REGULARITY

## Diagnosis

PROVEN_LOCAL: normal transfer did not change the visible defect, raising only cap segmentation exceeded budget, the prior solid dome removed scalp exposure but not faceting, and removing the cap did not remove the defect. The defect is therefore not primarily the cap normal field.

STRONG_HYPOTHESIS: the repeated flat-card depth boundaries form a regular ring/terrace pattern that survives alpha masking and is visible as a faceted crown.

## Production architecture supported by external sources

Apple recommends reducing translucent overlap and using an opaque inner/scalp hair layer so depth rejects hidden fragments. Epic's MetaHuman card system explicitly divides hair into Core, Mid, Top and Flyaway layers, with fewer/wider cards for core coverage and greater triangle allocation for the most visible top layer.

This does NOT mean repeating the failed protruding solid dome. The opaque inner layer should:
- hug the scalp/hair mass;
- terminate beneath the visible hairline and beneath the first card rows;
- never project as a rectangular plate in 3/4 view;
- carry a hair-like opaque texture/value so tiny card gaps do not show bare scalp;
- exist mainly to provide depth/coverage, not the outer hairstyle silhouette.

## Starting 1800-triangle allocation, HYPOTHESIS TO CALIBRATE

- hidden core/inner coverage: 15–20% = ~270–360 tri;
- primary/top silhouette/shape cards: 45–50% = ~810–900 tri;
- secondary/mid breakup: 25–30% = ~450–540 tri;
- flyaways/short transition: 5–10% = ~90–180 tri.

This is NOT an industry-published ratio. Epic publishes the hierarchy, not fixed percentages. Use this as the first controlled allocation and reallocate after image/error measurements.

## Break the regularity geometrically

Test deterministic variation, not random noise for its own sake:
- stagger adjacent root rows by ~0.3–0.5 card spacing;
- length variation ±15–25% within a controlled style band;
- radial/root offset a few millimeters so card endpoints do not lie on one crown ring;
- bend/twist primary cards only where their occlusion boundary is visible;
- avoid having more than ~2–3 neighboring card ends form the same screen-space line;
- rotate card phase so underlying and overlying seams do not coincide;
- use wider/denser-alpha core cards beneath, narrower breakup cards above;
- spend extra segments on cards contributing to the visible crown boundary, not every card equally.

These numeric ranges are starting test values, not external standards.

## Material decision test

Likely gameplay default to test first:
`opaque hidden core + two-sided alpha-clipped visible cards`.

Why:
- Alpha Clip participates like cutout rather than full alpha blend and avoids many depth-sorting problems.
- Apple explicitly warns that overlapping translucent layers drive overdraw.
- URP transparent blending occurs in the transparent path and is vulnerable to ordering/overdraw.

Dither can soften cutout at distance but may shimmer at 100px in motion, especially without stable temporal AA. Alpha Blend can look smoother in a still but is the riskiest for sorting/overdraw.

Required motion test:
- camera orbit and character movement, not stills;
- 90/100/150/220 px;
- 1, 5, 10 characters;
- capture GPU time and an image sequence;
- calculate per-pixel temporal difference after compensating for camera motion or use an optical-flow/warped difference proxy;
- manually count obvious popping/sorting events.

Production decision should be context-specific if needed: gameplay vs equipment close-up can use different hair material/LOD settings.

# P5 — TOP-DOWN CLASS IDENTITY

## What the production guides actually say

PROVEN_EXTERNAL: Valve explicitly designed Dota heroes to be immediately and uniquely identifiable from above. Silhouette matters, but Valve also names pose, weapon read, value gradient, value pattern, color/saturation, animations and speed as identity/readability contributors. It explicitly prioritizes game view over loadout.

PROVEN_EXTERNAL: Riot calls silhouette the single most important champion-recognition channel, centered around a defining PRIMARY feature, while also treating animation, VFX, SFX, model changes and materials/shape language as a combined clarity budget.

Therefore the answer is not 'top-down silhouette does not matter'. It matters enormously. But a black-mask IoU gate by itself is incomplete.

## Why current >=10% anchor test can pass while the class still fails

The anchor may occupy 10% of the mask but remain INSIDE the torso/cape footprint. It adds area without changing the external boundary that the eye uses for recognition.

Add a metric:

`outer_contour_contribution = length of final silhouette boundary whose source triangles belong to the class anchor / total silhouette perimeter`

Also calculate:
- `radial_excursion`: maximum anchor radius beyond a torso/body baseline by angular sector;
- `negative_space_contribution`: new visible holes/concavities introduced by the anchor;
- mass distribution in 8 or 16 polar sectors around the projected torso centroid.

Do not pick a permanent threshold yet. Measure all seven classes and correlate with human recognition.

## Classes without a weapon protrusion

Do NOT impose 'every class must carry a long diagonal weapon'. Riot's primary feature can be any stable defining characteristic. For a mage/seer top-down camera, candidate primary cues include:
- asymmetric shoulder/hood mass;
- a back-mounted focus or compact halo visible from above;
- cape split creating negative space;
- asymmetric sleeve/arm silhouette;
- distinctive headpiece height/width;
- a floating focus/orb whose position is stable in idle/gameplay;
- strong upper-body value/color block visible from above;
- characteristic idle pose that opens one side of the silhouette.

Permanent class VFX can help only if restrained and reliable; do not use VFX to compensate for a completely unreadable base model unless that VFX is guaranteed in every gameplay state.

## Human calibration protocol

No trustworthy universal production IoU threshold was found. Calibrate AETHERQOR itself:

For each of 7 classes render randomized stimuli at real 35°/50° gameplay camera:
- 64, 90, 128, 150, 220 px;
- silhouette only;
- silhouette + prop/anchor;
- normal value/color/material;
- normal + representative idle pose;
- optional stable class VFX.

Show each for 500–1000 ms, then force a 7-choice class selection. Record:
- accuracy,
- confusion matrix,
- median response time,
- confidence if desired.

Then fit/compare automatic metrics against human correctness:
- IoU / Dice,
- robust 95th percentile Hausdorff,
- contour Chamfer,
- radial descriptor distance,
- outer contour contribution,
- negative-space descriptors.

The production threshold is whichever metric combination best predicts real confusion on these seven classes. If IoU passes while mage/seer human confusion stays high, IoU becomes a secondary regression metric, not the primary identity gate.

# FINAL PRIORITY ORDER

1. P1 + P2 together: measure whether full Solidify and one universal 14k contract are the real source of the crisis.
2. P3: replace destructive global second-pass decimation with constrained per-slot reduction + allocator.
3. P4: restructure visible hair-card geometry/layering and test motion materials.
4. P5: replace mask-area anchor gate with actual contour contribution + human-calibrated identity contract.

The key rule for every change: `SOURCE -> LOCAL A/B -> GAME-CAMERA IMAGE -> PERFORMANCE -> DECISION`. Never promote a weak extracted game model count into a production budget fact.
