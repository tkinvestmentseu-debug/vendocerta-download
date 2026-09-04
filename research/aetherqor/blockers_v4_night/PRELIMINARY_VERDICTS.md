# AETHERQOR V4 NIGHT ULTRA RESEARCH — PRELIMINARY VERDICTS

Date: 2026-09-04
Context: mobile AAA, Unity 6 URP, Blender 5.2, 14k tri character budget, 90–300 px character height in gameplay.

These are testable technical verdicts before the full video-frame review. They are not permission to skip the measurements requested below.

## P1 — OVERLAPPED_SHELL_SOUP -> one clean watertight solid

### Preliminary verdict

**CGAL Alpha Wrapping is the strongest general candidate found so far and is materially different from the methods already rejected.** Its documented contract directly matches the failure mode: it can accept arbitrary triangle soups and produce an enclosing watertight, orientable/2-manifold, intersection-free output rather than trying to weld or boolean the input surfaces themselves.

This makes it the first candidate that should be tested as a true general replacement for the current slot-specific reconstruction methods.

It is NOT yet declared production-pass for AETHERQOR. The decisive unknown is whether it preserves the specific 3–8 mm recesses, grooves and plate gaps needed by armor at the required triangle budget.

### Parameter interpretation

- `alpha` is the geometric access/detail scale. Larger alpha acts like a larger carving tool: it cannot enter small cavities and will bridge/fill more detail. Smaller alpha follows narrower cavities/gaps but costs more geometry and compute.
- `offset` controls how far the final wrap sits outside the input. If the offset is too large relative to a plate gap, neighboring offset envelopes can effectively erase that gap.
- Therefore there is no defensible universal alpha/offset pair for 10–40 cm armor. Parameters must be calibrated in millimeters against the smallest feature that must survive.

### Required AETHERQOR sweep

Run on at least two real failures: the broken cuirass and the shoulder piece outside body-underlay range.

Test grid, in scene millimeters:

- alpha: `1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0 mm`
- offset: `0.25, 0.5, 0.75, 1.0, 1.5, 2.0 mm`

This grid is an AETHERQOR experiment, not a parameter recommendation from CGAL documentation.

For every combination measure:

- connected components
- boundary edges
- non-manifold edges
- self-intersection percentage
- output triangle count before and after reduction
- donor distance P50 / P95 / P99
- retained/bridged state for known 3 mm, 5 mm and 8 mm gaps
- concavity depth error at selected panel recesses
- silhouette deviation from donor at front/side/3-4 view
- wall thickness / accidental double-sided wraps around large openings

### Integration route

Python bindings do exist through CGAL SWIG bindings and include an Alpha_wrap_3 example for mesh/soup input. For a production build pipeline, compare two routes:

1. SWIG Python binding if it installs reproducibly on the Windows runner.
2. A tiny standalone C++ CLI compiled once and called from Python/PowerShell/Blender. This is likely the more stable route if Python binding packaging becomes brittle.

Do not pull the whole algorithm into Unity runtime. This belongs in the offline asset build pipeline.

Before shipping/distributing any CGAL-based binary, perform a separate license/compliance check for the exact CGAL package/version and use case.

### Alternative ranking

1. **CGAL Alpha_wrap_3** — first test. General enclosing wrap with explicit alpha+offset contract.
2. **Houdini/OpenVDB SDF/VDB from Polygons** — second test. Strong on open/kitbashed soup and automation, but voxel size becomes a hard feature floor; narrow concavities can be rounded/bridged.
3. **ZBrush DynaMesh + ZRemesher with PolyGroups/creases** — artist-guided fallback, useful for preserving authored regions but resolution sensitive and not equivalent to a general geometric guarantee.
4. **Quad Remesher / Instant Meshes** — retopology tools, not first-line solidification tools for an arbitrary open overlapping soup. Do not confuse cleaner topology with obtaining a valid enclosing solid.

Do not retry QRemeshify, Quadriflow, weld+holes_fill, Boolean Union on soup, Laplacian, or budget inflation.

## P2 — panel lines on hard armor at 2600 tri

### Preliminary verdict

A normal map can restore local shading detail but **cannot restore silhouette or actual plate-depth discontinuities**. The correct production split must be made by screen-space importance:

- geometry: silhouette-changing edges, major plate overlaps, recess mouths and breaks that must read at 90–300 px;
- normal/AO bake: stitching, engraved seams, shallow grooves and sub-pixel bevel/support-loop detail;
- optional floating geometry: only for a small number of visually important elements where it survives batching/material constraints and produces a measured benefit.

The exact triangle allocation is asset-specific. Do not invent an industry-standard percentage without evidence.

### Required experiment

Create three cuirass variants at the same total 2600-triangle budget:

A. current smooth low + donor normal/AO bake
B. edge-aware retopo/decimation that reserves triangles for major plate borders + same bake
C. B plus a very small floating-detail budget for only 2–4 critical accents

Render at equivalent 90, 150 and 300 px character height, front/3-4/side, same lighting.

Measure:

- silhouette IoU to donor
- contour/edge distance to donor
- number of major panel boundaries still human-visible
- normal-map seam/artifact count
- draw calls/material passes
- GPU frame delta on target mobile profile if floating parts are separate renderers

Rule: if a line changes the visible contour or creates a plate overlap shadow at 90–150 px, it should not be delegated entirely to the normal map.

## P3 — hair-card cap faceting at 1600–2000 tri

### Preliminary verdict

Transferring/editing normals on hair cards from a smooth scalp/base surface is a normal realtime production technique, not merely an emergency workaround. It can make the card cap shade as one smooth mass while alpha controls strand edges.

Limits:

- it does not fix a visibly polygonal silhouette;
- badly transferred normals can make specular response detach from actual card orientation;
- dramatic anisotropic/custom hair lighting can expose the mismatch;
- it must be tested under rotating key light and animation, not only one beauty angle.

### Required experiment

For each of at least two current styles:

1. current normals
2. scalp-transferred normals
3. scalp-transferred normals + one extra longitudinal/arc segment reallocated from strand density into the crown if faceting remains visible

At 90/150/300 px and three camera angles measure visual crown faceting plus bald-scalp exposure.

### Transparency test

Compare in the actual URP mobile shader/build:

- dithered/alpha-clipped treatment
- alpha blend where sorting is controllable

Measure GPU time, overdraw, sorting artifacts, edge stability under TAA/MSAA/current project AA, and backface behavior.

Do not pick Alpha Blend only because a tutorial shows it. Semi-transparent cards carry sorting/overdraw costs. Prefer the cheapest mode that passes the actual hair look at game distance.

## P4 — male 400x vs female 172x forearm stretch

### Preliminary verdict

Identical fitting code does not imply identical deformation because the algorithm consumes different geometry, bind transforms and weight fields. A 2.3x difference in the measured stretch ratio can arise from differences in:

- armature/rest-pose transforms or non-uniform object/armature scale
- bone lengths and local joint placement
- mesh density and edge flow around wrist/elbow
- nearest-source correspondence used for weight transfer/fitting
- count of influences per vertex
- normalization errors or tiny stray weights
- max weight / weight entropy / gradient across the forearm
- different bind matrices despite matching bone names
- twist-bone presence or absence and how weights are distributed between forearm/hand/twist bones

### Mandatory male-vs-female diagnostic dump

Generate a CSV/JSON comparison, not visual guesses:

- body/gear vertex and triangle counts in forearm ROI
- median/min/max edge length in ROI
- bone names, parent chain, rest length and local/global rest matrices
- object and armature scale/rotation transforms
- per-vertex weight sum before/after normalization
- influences-per-vertex histogram
- max-weight histogram
- weight entropy or equivalent spread metric
- percentage of vertices with stray influence <0.01, <0.02, <0.05
- forearm/hand/twist weight gradient by normalized distance along bone
- nearest body->gear correspondence distance P50/P95/P99 if transfer uses spatial matching
- deformation stretch metric per vertex and correlation with all fields above

The goal is to identify the variable that predicts the 400x outliers, not to tune a gender-specific constant.

## P5 — silhouette anchors readable at 64 px

### Preliminary verdict

Mask IoU is useful but insufficient as the only metric because it largely measures occupied-area overlap and is weakly sensitive to where boundary errors occur. Keep IoU as one gate, but supplement it.

Recommended AETHERQOR metric suite:

1. pairwise IoU on 64 px black masks
2. modified Hausdorff or Chamfer distance on the contour, normalized by character height
3. anchor-region occupancy/extent for the deliberately distinguishing region of each class
4. human forced-choice recognition/confusion test at 64 px, preferably with short exposure and class labels learned beforehand

Do not claim 0.85 is an industry-standard threshold. Treat it as an internal gate and calibrate it against actual human confusion. If pairs pass IoU yet are repeatedly confused by humans, the anchor contract fails regardless of IoU.

### Required calibration

For all 7 classes:

- render same pose and at least 2 additional poses that alter limb overlap
- 64 px and 96 px
- compute pairwise IoU + contour distance
- run a small blinded forced-choice test
- rank class pairs by human confusion
- regress/confusion-check which automated metric best predicts those errors

Final threshold should be chosen from this calibration rather than borrowed from another project.

## Final research output required

The complete research pass must end in `FINAL_TECHNICAL_VERDICTS.md` with one row per point and one of:

- `RESOLVED`
- `TESTABLE_HYPOTHESIS`
- `BLOCKED`

Every row must include evidence, exact measured test, result numbers and the next implementation change in AETHERQOR. No `RESEARCH_DONE` status is accepted.
