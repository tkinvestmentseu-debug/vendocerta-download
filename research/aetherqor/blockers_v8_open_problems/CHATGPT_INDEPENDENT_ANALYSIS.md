# AETHERQOR V8 — CHATGPT INDEPENDENT TECHNICAL ANALYSIS

This is an independent engineering position created before complete V8 video review. Claude must challenge it with video evidence, authoritative docs and local experiments. Any numeric threshold not already measured in AETHERQOR is an experiment, not an industry standard.

## A1 — replace the causal role of Z-slice loft, not just its shading

The measured terrace signature is consistent with a reconstruction rule that lets remote shoulder/arm donor geometry influence torso cross-sections. The most informative next test is not another decimator. It is an input-domain experiment:

1. take the same donor and existing successful Alpha Wrap settings;
2. create `RAW_DONOR` and `TORSO_CROPPED_DONOR` where shoulder wings/arm contamination outside the intended chest semantic region cannot influence torso volume;
3. Alpha Wrap both;
4. compute terrace-step metrics along Z and compare silhouette/donor error;
5. if raw is bad and cropped is good, fix semantic donor extraction before reconstruction;
6. if both contain the same torn terrace, the defect is in donor geometry/form itself;
7. only then test localized fairing/mean-curvature/tangential relaxation on terrace-selected regions, with hard feature constraints and max donor displacement.

Do not globally smooth a hard-surface cuirass. A valid fairing result must reduce high-frequency step noise while preserving designed plate breaks, concavity and top-down silhouette.

Suggested detector: sample silhouette/radial envelope over Z, compute adjacent-width jump and second derivative; flag narrow horizontal bands whose jump exceeds local robust median/MAD. Use detector only to select candidate region, not to decide final quality.

## A2 — the cavity algorithm is conceptually wrong for 461 disjoint UV charts

The local 1:1 island-to-mosaic proof is stronger than more padding experiments. A blur in texture coordinates cannot distinguish a real geometric valley from an island boundary because disconnected texels are unrelated despite being neighbors in atlas space.

Correct architecture candidate:

`HIGH/LOW GEOMETRY -> CURVATURE/CONCAVITY IN OBJECT/TANGENT GEOMETRY -> BAKE TO UV -> DILATE -> PACK INTO MODS.B`

not:

`BAKED/FLAT TEXTURE -> 2D GAUSSIAN -> call result cavity`.

Blender Pointiness is useful as one geometry-derived control, but because it is Cycles-specific it should not become runtime logic. Marmoset/Substance-style curvature baker is a second independent control. Compare outputs in object-space truth regions that cross UV seams.

Then inspect Unity `MODS.B` with forced debug shader views: B=0, B=1, current map, amplified map. This isolates whether the Cycles portrait artifact is even materially important in game.

UV rebuild is optional second stage. xatlas is attractive because it is MIT and mature, but fewer charts alone is not the objective. The target is fewer false seams at acceptable distortion/texel density/bake error.

## A3 — footwear needs semantic feature measurements

A boot can be topologically valid and still look like a sock. General geometry metrics will miss this. Add semantic landmark QA:

- sole plane and thickness,
- toe projection relative to foot bone/body envelope,
- heel projection/height,
- ankle opening/break,
- lateral outsole width,
- screen-space silhouette delta versus naked foot/body proxy.

Run the same measurements at donor, reconstructed shell, target-budget shell and LOD. This gives the first causal answer rather than another subjective rebuild.

If the donor itself lacks sole/toe/heel, regenerate/re-author donor. If donor and pre-decim contain them but target budget loses them, protect those features during allocation. If geometry retains them but 300px read is still soft, inspect material/value separation before adding triangles.

## A4 — first establish whether hair debt exists in the actual game

A highlight artifact on 200px head cards under isotropic Cycles is not evidence of a 13-44px head problem in URP. The zero-cost first test is downsampling current proofs with correct reconstruction filter to the target head sizes. The decisive test is Unity 6:

- same mesh, same cards, same camera path;
- material A = current AETHERQOR hair;
- material B = minimal anisotropic URP implementation;
- optional material C = second open-source anisotropic implementation;
- 90/150/300 px character heights;
- static, orbiting camera, moving directional light;
- measure temporal shimmer and crown contrast variance.

The CC0 Fulcrum shader is a code/idea donor, not production drop-in; it was authored for an older URP and its README itself calls it experimental. The MIT Shader Graph anisotropic repository is a second reference. Port the minimum model and profile it on target mobile.

If anisotropic material removes facets at target size, close geometry debt. If not, only then reopen card overlap/curvature/row regularity.

## A5 — prevent garbage-in allocation

A 14x source-count outlier should never silently enter a uniform target allocator. Add provenance gate before optimization:

`slot_source_audit.csv` fields: class, sex, slot, source_path, source_hash, generator_run, triangles, vertices, components, bbox, anatomical_overlap, median_slot_tri, ratio_to_median, decision.

Hard-review any ratio above a robust project-derived threshold. For Ember_M pauldron, inspect components and spatial spread. If the mesh contains multiple accidentally joined pieces, isolate the anatomical component. If it is the wrong donor, fix routing. If truly intended high-frequency class geometry, Alpha Wrap/retopo it deliberately and preserve identity features rather than 76x blind collapse.

## B1/C2 — solve engineering before owner art policy

The data shows current female assets often collapse class identity because shared female source forms override class source forms. Two proof branches can be built now:

### SAME_IDENTITY_REFIT
Start from the class-defining armor form and refit to female body using clearance/fit field, not body-hugging shrinkwrap. Preserve macro planes, shoulder mass, collar, anchor and plate architecture. Adapt only fit zones and deformation clearances.

### SEX_SPECIFIC_FORM
Use a separately authored female form, but enforce shared class grammar: primary anchor, material motifs, dominant shape rhythm, weapon family and class palette.

For both, evaluate top-down/gameplay recognition and animation. The owner can then choose policy from evidence instead of abstract discussion.

## B2 — do not trust FBX material round-trip as material source of truth

The project already proves QA can look correct while imported material ownership is wrong. Make Unity project materials authoritative.

Proposed architecture:

- Blender/FBX exports stable semantic material slot names, e.g. `AQ_BODY_SKIN`, `AQ_UNDERLAYER`, `AQ_EYE`, `AQ_METAL_GEAR`, plus optional slot/class ID;
- checked-in `material_manifest.json` maps semantic identifiers to Unity Material GUID/path;
- AssetPostprocessor/ModelImporter remaps on import using Unity's supported remap APIs;
- import fails if required semantic slot is unresolved or duplicates ambiguously;
- post-import validator checks every renderer/material slot and known failure cases;
- QA render uses actual imported materials, not a rescue flag that hides loss.

`SearchAndRemapMaterials` may be sufficient if naming is unique and deterministic. `AddRemap` gives explicit control where project naming requires it. Choose after a pilot.

## B3 — one skinned aggregate is feasible, but the regression harness matters more than the combiner

Open-source code confirms this is a solved class of engineering problem, not magic. UMA is the strongest reference candidate because it is MIT and built around modular avatars. A small UnitySkinnedMeshCombiner repo also demonstrates the concept but lacks license metadata and must remain read-only reference.

Implementation outline:

1. create canonical destination skeleton dictionary keyed by stable transform path/semantic bone ID;
2. collect each source renderer's bones;
3. remap source bone indices to destination canonical indices;
4. append vertices/normals/tangents/UV/colors;
5. offset triangles/submesh indices;
6. remap all BoneWeight indices;
7. verify weight normalization/influence policy;
8. produce destination bones/bindposes consistently from canonical skeleton;
9. copy/remap blendshape vertex deltas by final vertex offsets where needed;
10. merge only material-compatible submeshes or preserve submeshes intentionally;
11. build SkinnedMeshRenderer;
12. test in motion.

Critical QA: sample several frames from all 21 clips and compare source aggregate versus merged output. Use max/percentile deformed vertex distance if vertex correspondence is preserved, plus silhouette/render diff. A bind-pose screenshot is insufficient.

Runtime strategy: combine/cached rebuild on equip state changes, never every frame. Measure cost and cache policy on actual target.

## B4/B5 — identity should be designed as a cue budget, not a single anchor percentage

Riot/Valve production guidance supports stable primary identity cues and real gameplay-view evaluation, not a universal 68% extent. A weapon can be ideal because it naturally leaves the torso contour and moves with animation, but huge shoulder geometry is not equivalent.

For each class define:

- `primary_identity_type`: weapon / offhand / shoulder / backpiece / hood / etc;
- outer contour contribution in gameplay view;
- radial excursion by 16 sectors;
- occupied screen pixels at 90/150/300;
- movement signature during idle/run/combat;
- collision/clipping over animation;
- donor/class similarity.

If adding a first-class weapon slot gives classes a cleaner identity cue than giant shoulder/back anchors, the architecture should permit it. Existing 1400/1200 weapon/offhand budget makes the current absence of the slot especially suspicious.

## B6 — Frost shield is first a transform/attachment forensic problem

Before remodeling, print:

- renderer/object hierarchy path,
- parent bone,
- local position/rotation/scale,
- world bounds,
- nearest distance to intended torso/back surface,
- attachment marker distance,
- trajectory over idle/run/combat.

Compare to any correctly attached backpiece/shield. If transform basis or parent is wrong, fix it. If the design intentionally floats, then it needs an explicit magical-floating visual language; otherwise 0% proximity reads accidental.

## C1 — tooling can be complete now

Build the 7AFC application/trial generator and metric pipeline regardless of participant availability. Human calibration is the only external dependency. Do not promote IoU 0.85 or any new number as universal standard.

## C3 — exact rank and visible band are different data dimensions

Seven gameplay ranks can map to N visual bands. Create a data table independent of shader assets, and render candidate 2/3/4-band mappings in:

- daylight,
- night,
- neutral controlled lighting,
- Bloom on/off.

A band is valid only if its cue survives the intended gameplay lighting without depending entirely on Bloom. Let owner select desired art progression after the matrix is available.

## Required V8 output philosophy

For every problem output: `CURRENT_FACTS -> EXTERNAL_EVIDENCE -> VIDEO_EVIDENCE -> GITHUB_CODE_EVIDENCE -> LOCAL_EXPERIMENT -> METRICS -> VERDICT -> IMPLEMENTATION -> REGRESSION QA`.

Never hide an unresolved art decision inside a technical default. Never hide a technical import/geometry bug with a prettier QA render.
