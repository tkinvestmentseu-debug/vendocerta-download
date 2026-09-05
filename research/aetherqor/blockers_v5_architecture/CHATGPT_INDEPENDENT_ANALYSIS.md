# AETHERQOR V5 — CHATGPT INDEPENDENT ANALYSIS

Status: preliminary technical verdicts produced independently from the V5 video pipeline. Claude must validate them against the local V5 videos and real AETHERQOR assets before marking anything PROVEN.

## P1 — 14k triangle architecture

### Preliminary verdict
`14k` should not be treated as a universal authoring budget for every presentation of the player character.

The stronger production pattern is context-dependent character quality:
- equipment / hero close-up
- gameplay player LOD
- gameplay secondary / other-player LOD
- crowd / distant LOD

Simplygon's official mobile guidance explicitly recommends multiple character versions for mobile and judging the result on the target device at the real viewing distance. Their low-poly character example also recommends OnScreenSize / maximum deviation instead of a fixed triangle count because different assets tolerate different reduction levels.

Publicly extracted/ripped character meshes from current games show that full source/runtime-near assets can be far above 14k, but these numbers are WEAK EVIDENCE because they do not prove the exact mobile gameplay LOD selected at runtime. Therefore do not use them as a new budget directly.

### Important architecture correction
Do not pay full Solidify cost on every hard armor shell by default.

For armor, the preferred experiment is:
1. single-sided outward shell
2. backface culling ON
3. add physical thickness only on silhouette-visible / exposed rims, holes and openings
4. use normal/AO for shallow interior detail

Do NOT solve the Solidify problem by globally switching armor to double-sided rendering. That spends pixel cost instead of geometry cost and still does not create a real visible rim.

### Required AETHERQOR experiment
Build exactly the same outfit in four measured presentation tiers:
- 14k
- 20k
- 28k
- 40k

Optional 55k only for equipment/hero close-up if 40k still shows visible silhouette loss.

At each tier measure at 90 / 150 / 220 / 300 px:
- silhouette pixel error against reference
- panel / helm read
- animation deformation
- visible shell holes
- total triangles
- post-split vertex count
- SkinnedMeshRenderer count
- batches / draw calls
- GPU time on target-like mobile profile

Use screen-space quality to choose the production target. Do not choose the number first and then destroy the asset to hit it.

### Budget allocator recommendation
After the presentation-tier decision, allocate triangles by perceptual importance rather than flat per-slot percentages.

High priority:
- head / face / hair silhouette
- shoulders and major class anchors
- torso outer contour
- weapon / prop identity
- large deformation zones

Lower priority:
- body fully hidden under gear
- interior surfaces never visible
- shallow panel detail already represented in maps
- undersides outside gameplay camera

Any hidden body geometry under equipped armor should be removed/hide-masked before judging the total runtime budget.

## P2 — Overlapped shell soup / CGAL Alpha Wrap

### Preliminary verdict
CGAL `Alpha_wrap_3` is technically the strongest general candidate found so far because its official API explicitly accepts a triangle soup and promises an output that is:
- watertight
- 2-manifold
- intersection-free
- enclosing the input

This directly matches the topology failure mode of Meshy donors better than ordinary remesh/decimate tools.

### Critical limitation
Alpha Wrap is an enclosing reconstruction. Its key risk for AETHERQOR is intentional defeaturing:
- small gaps can close
- narrow concavities can disappear
- thin spikes can fatten or vanish

`alpha` controls the cavity/detail scale the wrapper can enter.
`offset` controls tightness / distance from the input.
Large alpha and large offset both move toward simpler, less faithful output.

### First real-unit sweep
Do not start with one magic pair.

For a real armor part scaled in meters, run a coarse sweep approximately around:
- alpha: 1.5, 2, 3, 4, 6, 8 mm
- offset: 0.25, 0.5, 0.75, 1.0, 1.5 mm

Then refine around the Pareto front.

For the smallest protected 3 mm panel gap, treat `offset >= ~1.5 mm` as immediately suspicious and prefer testing well below half-gap first. This is a test heuristic, not a mathematical guarantee.

Pass criteria must include explicit survival of known 3 / 5 / 8 mm gaps and known concavities, not just manifold validity.

### Integration recommendation
Official CGAL Alpha_wrap_3 is C++ and CGAL's package is GPL licensed. For an internal pipeline prototype, prefer a minimal standalone CLI wrapper rather than embedding CGAL into Blender or Unity:

`alpha_wrap.exe input.obj output.obj --alpha-mm X --offset-mm Y`

The wrapper should emit JSON metrics and never overwrite the donor.

Do not block the prototype waiting for a perfect Python binding. If a maintained binding exposing Alpha_wrap_3 is not already available, a tiny C++ executable is the lower-risk route.

### Comparison baseline
Compare against exactly one SDF/VDB reconstruction and current per-slot best method. Do not reopen QRemeshify, Quadriflow, Boolean Union or weld+fill.

## P3 — second decimation destroys already-budgeted shells

### Preliminary verdict
Global blind second-pass decimation is the wrong architecture for modular parts that already have approved topology.

Production pattern should be:
1. each slot has MIN / TARGET / MAX
2. each slot has protected regions / importance
3. global allocator enforces the outfit sum
4. only flexible / over-budget geometry is reduced further
5. if SUM(MIN) exceeds the global budget, fail the budget architecture instead of silently breaking approved slots

### Evidence-backed reducer controls
Simplygon supports:
- vertex weights for important regions
- geometry / shading / skinning importance
- skinning-aware reduction
- modular seams for deterministic shared-border reduction

This is a much closer match to the problem than Blender's generic whole-object Decimate modifier.

### Implementation instruction
Change `retopo_postaci.py` from:
`assemble -> global ratio -> decimate everything`

toward:
`audit -> reserve protected minima -> allocate flexible budget -> weighted reduction only where necessary -> verify sum`.

Each hard reconstructed slot must carry metadata:
- approved triangle count
- min triangle count
- max extra reduction allowed
- protected boundary vertices/edges
- silhouette importance
- deformation importance
- whether slot may be re-reduced at all

For the shoulder regression, encode the known 16/16 border loop as a hard QA assertion. A result with 11/11 and 11/12 must fail even if the global triangle number passes.

### Global allocator sketch
1. Reserve all slot MIN values.
2. Reserve base body/hair minimums.
3. Compute remaining budget.
4. Rank candidate triangle removals by projected screen-space error / cost saved.
5. Spend the remaining budget on the highest-value geometry until TARGET or global cap.
6. Never collapse protected seams merely because the global percentage says so.

If the 14k budget cannot satisfy all MIN values, return `BUDGET_ARCHITECTURE_FAIL` and route back to P1.

## P4 — hair card crown faceting is occlusion geometry, not normals

### Preliminary verdict
The new diagnosis is consistent with production hair workflows: if the visible defect is the boundary between overlapping flat cards, custom normals cannot remove it because the contour/occlusion boundary is geometric.

Do not spend the next iteration on another normal-transfer variant.

### Production structure to test
Use layered hair hierarchy:
1. BASE / SCALP COVERAGE layer
2. PRIMARY large clumps that establish volume
3. SECONDARY cards that break visible planar boundaries
4. BREAKUP / flyaway cards only where they survive at gameplay size

Industry breakdowns commonly use either a low-poly cap plus cards or a first card layer that covers the scalp, followed by large-form and breakup layers.

### Geometry instruction under ~1800 tri
Do not increase SEG uniformly.

Move triangles from invisible/low-value overlap into curvature where the crown silhouette and inter-card occlusion boundary is visible.

Test:
- fewer, wider base cards
- curved primary cards (extra segments only on crown-critical arcs)
- staggered overlap depth so multiple straight edges do not line up
- narrower secondary cards crossing the most visible planar boundaries

The pass criterion is the real 3/4 gameplay view, not isolated wireframe smoothness.

### URP material verdict to test first
For mobile gameplay, Alpha Blend should NOT be the default assumption. URP renders transparent materials in a separate transparent pass, which introduces sorting and overdraw concerns.

First production candidate:
- Alpha Clip / cutout for gameplay
- Render Face Both only where the same card genuinely needs both sides
- test MSAA / alpha-to-coverage style solution if the custom hair shader supports it

Keep Dithered only if temporal stability is proven in the actual game camera. A dither that shimmers at 90-150 px fails even if a still frame looks good.

Use Alpha Blend only as a close-up/equipment candidate if it materially improves the hairline and measured cost/sorting remain acceptable.

### Mandatory comparison
Same hairstyle, same camera, same budget:
A current DITHERED
B Alpha Clip
C Alpha Blend

Measure 1, 5 and 10 visible characters:
- GPU frame time
- overdraw
- sorting artifacts
- temporal shimmer
- scalp exposure
- crown faceting score / edge visibility

## P5 — silhouette identity in the actual top-down gameplay camera

### Preliminary verdict
The existing 21-pair IoU gate is useful but insufficient because it was passed while two classes still collapse into similar dark masses in the real gameplay camera.

This proves that the contract must be camera-conditioned.

Valve's Dota character art guide explicitly requires first-glance silhouette identification, but also states that familiar colors or other silhouette elements can balance a changed item silhouette, and weapons need a unique read. This supports a multi-channel identity contract rather than requiring every class body alone to be unique from every camera.

### New identity contract
Every class must own at least one CAMERA-STABLE primary identity cue in the real gameplay view:
- protruding weapon / staff / shield / prop
- asymmetrical shoulder / back anchor
- strong negative space
- unmistakable top-view mass ratio
- large controlled color/material block
- restrained persistent class VFX cue

A weapon is one valid solution, not a mandatory universal solution.

For mage / oracle-like classes with no long weapon, add a gameplay-readable anchor that survives 35° azimuth / 50° elevation. Examples to test are an asymmetric back/shoulder construct, floating focus, rigid halo/rune frame, or strong cloak cutout/negative space. Do not add random decorative spikes merely to beat the metric.

### Replace pure IoU gate with composite validation
Keep IoU as one signal, but add:
- robust contour Hausdorff percentile
- Chamfer contour distance
- anchor mask contribution in the actual gameplay view
- color/material confusion test
- timed human recognition / confusion matrix

Do not invent a universal Hausdorff or IoU threshold from literature. Calibrate thresholds on the seven actual classes.

### Human test
Generate randomized cards at 64 / 96 / 128 px for:
A silhouette only
B silhouette + weapon/anchor
C final material/color

Record class choice and response time.

The production contract should be based on the weakest pair, especially mage vs oracle, rather than the average of all 21 pairs.

## Immediate priority order for Claude

1. P1 budget architecture audit before any more destructive simplification.
2. P3 remove blind second-pass decimation once P1 determines the real budget model.
3. P2 Alpha Wrap proof on cuirass + shoulder in parallel because it can remove several slot-specific reconstruction branches.
4. P4 geometry/material hair experiment, explicitly no further normal-transfer work.
5. P5 real-camera recognition harness and composite identity contract.

## External sources used for these preliminary verdicts

- Simplygon, Low-poly character optimization: https://www.simplygon.com/blog/0179d2c5-a440-49d7-850a-0a9a94152d1b
- Microsoft/Simplygon, Automated Asset Optimization for Mobile Games: https://developer.microsoft.com/en-us/games/articles/2025/10/automated-asset-optimization-for-mobile-games-with-simplygon/
- Microsoft/Simplygon, Fundamental character optimization tools: https://developer.microsoft.com/en-us/games/articles/2025/09/four-fundamental-simplygon-tools-for-automated-character-optimization/
- Simplygon Modular Seams documentation: https://documentation.simplygon.com/SimplygonSDK_10.1.400.0/api/tools/modularseams.html
- Simplygon Reduction documentation: https://documentation.simplygon.com/SimplygonSDK_10.1.400.0/concepts/reduction.html
- CGAL Alpha Wrap manual: https://doc.cgal.org/latest/Alpha_wrap_3/group__PkgAlphaWrap3Ref.html
- CGAL Alpha Wrap user manual: https://cgal.geometryfactory.com/CGAL/doc/main/Alpha_wrap_3/index.html
- Unity URP Lit / Simple Lit material documentation: https://docs.unity.cn/Manual/urp/lit-shader.html
- Airship Images hair production breakdown: https://80.lv/articles/airship-images-making-haircuts-for-game-characters
- Character hair-card layer breakdown: https://80.lv/articles/001agt-002mrs-004adk-character-production-in-ue4-the-warrior-of-light
- Valve Dota 2 Character Art Guide: https://help.steampowered.com/en/faqs/view/0688-7692-4D5A-1935

## Evidence caution

Extracted/ripped model triangle counts from Genshin / Wuthering Waves are useful only to falsify the assumption that every modern mobile character source is necessarily ~14k. They are NOT proof of the exact runtime mobile LOD. Treat them as `EXTRACTED_MODEL_WEAK_EVIDENCE` until runtime LOD selection is independently demonstrated.