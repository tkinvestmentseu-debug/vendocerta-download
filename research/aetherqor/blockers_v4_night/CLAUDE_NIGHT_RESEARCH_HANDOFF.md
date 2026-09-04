# AETHERQOR V4 NIGHT ULTRA RESEARCH — CLAUDE HANDOFF

## Local research root

`D:\AetherqorFoundry\research\blockers_v4_night\ULTRA_RESEARCH_2026-09-04_NIGHT`

Existing V3 research is already local at:

`D:\AetherqorFoundry\research\blockers_v3\CLAUDE_VIDEO_REPORT_33904162671`

Reuse it where relevant. Do not redownload it.

## Mission

Resolve five measured production questions. This is not a general modular-character research task.

1. General conversion of arbitrary `OVERLAPPED_SHELL_SOUP` armor donors into one clean enclosing solid, with CGAL Alpha Wrapping as the primary untested candidate.
2. Preserve/read panel construction on a 2600-triangle hard cuirass.
3. Remove faceted hair-cap reading at a 1600–2000 tri hair budget and choose the correct URP mobile transparency strategy.
4. Explain and fix the measured male/female forearm deformation divergence: 400x vs 172x under the same fitting mechanism.
5. Validate class silhouette anchors at 64 px with metrics that predict actual recognition, not IoU alone.

## Read order

Before changing production assets:

1. `PRELIMINARY_VERDICTS.md`
2. `SOURCE_REGISTRY.md`
3. `videos.psv`
4. each video `manifest.json`
5. transcript and indexes for each relevant video
6. sequential 3x3 contact sheets
7. selected raw 1fps frames for the exact relevant time ranges
8. selected 4fps high-detail frames when present
9. relevant existing V3 evidence
10. current AETHERQOR source/assets and the user's measured failure artifacts

Do not inspect thousands of JPGs blindly. Triage with transcript -> indexes -> 3x3 sheets -> selected 1fps -> selected 4fps.

## Evidence record

Every material video conclusion must record:

- point P1–P5
- video slug
- exact timecode
- frame/sheet filename
- what the author actually does/shows
- why it matters to AETHERQOR
- confidence level
- what measurement will prove or reject it locally

For web/document sources record the exact source and the specific technical claim used. Separate documented guarantees from AETHERQOR hypotheses.

## P1 execution contract — highest priority

After evidence review, perform a real Alpha Wrap experiment if the runner/toolchain makes it feasible.

Use at least:

- the real failing cuirass donor
- the real failing shoulder/naramiennik donor

Do not substitute a toy cube or synthetic soup as the final proof.

Try the lowest-friction route first:

1. discover whether usable CGAL Alpha_wrap_3 Python/SWIG bindings already install or can be reproducibly installed;
2. if not, create a minimal standalone C++ command-line wrapper around `Alpha_wrap_3` and compile it once for the offline pipeline;
3. do not integrate it into Unity runtime.

Run the parameter sweep specified in `PRELIMINARY_VERDICTS.md` unless a documented unit/scale reason requires adapting it. Record the adaptation.

For every run write machine-readable metrics including self intersections, boundary/nonmanifold counts, components, triangles, donor-distance percentiles, known 3/5/8 mm gap survival and selected concavity-depth errors.

Produce proof renders from consistent views.

Do NOT retry the already measured dead ends:

- QRemeshify
- Quadriflow
- weld + holes_fill
- Boolean Union on soup
- Laplacian smoothing
- raising the slot budget to 25k

Compare Alpha Wrap to VDB only if Alpha Wrap does not meet the feature-retention gate or if VDB can be tested cheaply in the existing environment.

## P2 execution contract — cuirass at 2600 tri

Normal maps cannot change silhouette. Test three equal-budget variants:

A. current smooth low + donor normal/AO bake
B. edge-aware low reserving triangles for major constructive plate boundaries + same bake
C. B plus only a tiny measured floating-detail allocation

Evaluate at 90, 150 and 300 px character height under identical lighting and views.

Classify each donor detail before spending triangles:

- silhouette / major overlap / recess mouth -> geometry candidate
- shallow seam / stitch / engraving / support-loop bevel -> bake candidate

Record render cost and draw-call/material impact for floating pieces rather than accepting/rejecting them by convention.

## P3 execution contract — hair

Test current vs scalp-transferred normals on real current hair assets under:

- three views
- rotating/changeable key light
- game-distance framing
- at least one animation if available

If silhouette/crown facets remain after normal transfer, reallocate triangles from low-value strand detail into cap curvature and measure the result.

Test the actual project URP shader/build with dither/clip versus alpha blend. Measure overdraw/GPU delta and sorting artifacts. Do not choose a mode solely because a tutorial recommends it.

## P4 execution contract — male vs female 400x / 172x

Do not introduce a `if male then ...` correction unless the root cause has first been measured.

Produce a male-vs-female diagnostic JSON/CSV including:

- body/gear vertex and triangle density in forearm ROI
- edge-length statistics
- object/armature transforms
- bone hierarchy, rest lengths and matrices
- per-vertex weight sums
- influences-per-vertex histogram
- max-weight distribution
- weight entropy/spread
- tiny stray-weight rates
- normalized forearm/hand/twist weight gradient
- spatial transfer correspondence distances if applicable
- per-vertex deformation/stretch outliers

Then correlate the 400x outliers with these fields and identify the smallest root-cause fix.

## P5 execution contract — silhouette at 64 px

For all seven classes compare:

- pairwise mask IoU
- modified Hausdorff or Chamfer contour distance, normalized by character height
- explicit anchor-region occupancy/extent
- blinded human forced-choice confusion at 64 px

Use same pose plus at least two additional poses. Also render 96 px as a control.

The current IoU 0.85 gate remains an internal gate until calibration. Do not call it an industry standard.

## Hard implementation loop

For each point:

`SOURCE READ -> VIDEO FRAME REVIEW -> CURRENT ASSET/CODE DIAGNOSIS -> EXPERIMENT -> REAL AETHERQOR ASSET -> AUTOMATED METRICS -> PROOF RENDER -> VERDICT -> IMPLEMENTATION CHANGE -> RE-TEST -> CHECKPOINT COMMIT`

No point is closed because code compiles or a mesh visually looks better in Blender.

## Final files required

Create under the local root:

- `FINAL_TECHNICAL_VERDICTS.md`
- `EVIDENCE_LEDGER.csv`
- `EXPERIMENT_RESULTS.json`
- `IMPLEMENTATION_PLAN.md`

For each P1–P5 final status use exactly one:

- `RESOLVED`
- `TESTABLE_HYPOTHESIS`
- `BLOCKED`

Include the measured numbers, source/frame evidence and exact next production change. Do not output `RESEARCH_DONE`.
