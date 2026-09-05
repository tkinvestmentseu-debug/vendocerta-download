# FLYCAT_PHASES

Status: PASS 1 COMPLETE — whole-video overview only

Source: public FlyCat video `3D Game Character - Armor modeling - Blender 4.4` (`hQhTGMk47qI`).
Duration from manifest: 3353 s = 55:53.
Evidence reviewed for this pass: all 19 sequential `phase_overview_5s` sheets, 671 sampled frames total, 5 s spacing.

Important limitation: this file is a coarse whole-video phase map. It does NOT claim exact mouse clicks, operators, modifier order or numeric values. Those belong to the cluster/triplet/micro-review pass. Classify exact operations only after before/peak/after review.

The time overlay embedded in overview sheets becomes visually offset by +1 hour after approximately 30:00 (for example the next sequential sheet shows `01:30:00`). Use manifest duration, frame/cluster CSV timecodes and sequential sheet order as the canonical time source, not that visible overlay anomaly.

## P00 — Final-character showcase / target reference
Approx. 00:00–00:55

Visible content:
- finished armored character in several poses and camera distances
- gameplay/render-scale views
- closeups of final silhouette, leg armor, torso and helmet
- FlyCat title/logo transition

Purpose for AETHERQOR:
- final-quality target only
- do not infer construction steps from this intro

## P01 — Existing base + early armor blockout / macro silhouette
Approx. 00:55–03:20

Visible content:
- male base body with already-started armor pieces
- broad torso, shoulder and skirt/leg armor forms
- repeated front/side inspections
- early helmet and torso form changes

Current interpretation:
- macro armor silhouette and plate relationships are established before heavy ornament/detail
- exact source method for each shell remains unresolved until cluster review

## P02 — Helmet, neck, forearm and small armor-component construction/refinement
Approx. 03:20–06:00

Visible content:
- helmet side/back and neck-area edits
- forearm/bracer pieces
- small circular/ornamental objects
- layered skirt/hip components and chainmail-adjacent pieces
- full-character checks between local edits

## P03 — Torso / chest / helmet / arm plate topology refinement
Approx. 06:00–09:00

Visible content:
- chest and side-torso plate boundaries
- repeated edge-loop/topology inspection
- helmet crown/front refinement
- wrist/forearm armor and round accent construction
- local component isolation followed by full-character checks

Important hypothesis to test in cluster review:
- feature intent appears to be encoded through explicit plate boundaries/topology before final surface finishing

## P04 — Gauntlets, hand armor, hip ornament, thigh/shin armor
Approx. 09:00–12:00

Visible content:
- hand/gauntlet finger armor
- wrist cuff and small accent plates
- large hip/waist ornament
- thigh/upper-leg plate shaping
- shin/greave topology and edge refinement

## P05 — Shoulder/chest/leg plate refinement and layered overlaps
Approx. 12:00–15:00

Visible content:
- isolated shoulder/chest plate pieces
- shoulder-to-torso integration checks
- thigh/hip plates with layered surface forms
- repeated wire/topology inspection
- lower-body silhouette checks

## P06 — Loin/skirt/cloth-adjacent armor, decorative forms and cleanup
Approx. 15:00–18:00

Visible content:
- front skirt/loin armor and cloth-adjacent pieces
- chest/hip decorative motifs
- small attachment details
- helmet/arm/garment topology checks
- full-character material/shape inspection

## P07 — Full-set refinement / ornamental-detail pass
Approx. 18:00–24:30

Visible content:
- helmet profile and circular temple/ear detail
- chest ornament and shoulder detail
- forearm/gauntlet surface details
- skirt/waist/lower-body plates
- boot/greave refinements
- embossed/engraved-looking ornamental regions
- many local closeups followed by full-character checks

Interpretation:
- this is predominantly a refinement/details phase rather than first-pass macro blockout
- exact mechanism for engraving/raised detail still requires cluster/triplet review

## P08 — Boots / attachments + UV preparation and packing
Approx. 24:30–27:00

Visible content:
- boot and lower-leg finishing
- long narrow attachment/cloth/strap-like pieces
- full-character mesh selection
- UV islands and packed UV layouts across multiple subsets
- separated armor groups for UV work

Strong visual transition:
- around 25:45–26:00 the workflow visibly shifts from geometry closeups toward UV/layout work

## P09 — Asset/file handoff and Blender material/shader setup
Approx. 27:00–30:00

Visible content:
- asset/file dialogs
- separated object/material groups
- shader-node editing
- whole-character material lookdev
- metallic/leather/cloth appearance adjustments

Interpretation:
- geometry production is largely complete by this point
- exact external-tool roundtrip must be confirmed from cluster evidence; do not assume a particular app solely from a file dialog

## P10 — Material lookdev / shader masks / metal-leather differentiation
Approx. 30:00–39:30

Visible content:
- repeated full-character material previews
- node graphs
- closeups of metal, leather/cloth and chainmail regions
- color/value/roughness-looking adjustments
- surface-detail checks on helmet, chest, boots, waist and skirt

Important note:
- source package contains no usable transcript, so exact node semantics must be read from UI/evidence rather than narration

## P11 — UV / normal / mask / texture-map verification across armor subsets
Approx. 39:30–43:30

Visible content:
- normal-map-looking purple textures
- black/white masks
- packed UV atlases
- subset-specific texture checks for torso, limbs, armor pieces and accessories
- material-node previews on corresponding geometry

Interpretation:
- this phase is clearly texture/UV verification and material assembly
- exact channel packing and map semantics still need close cluster review

## P12 — Rigging / skinning / weight-paint / deformation and pose checks
Approx. 43:30–48:20

Visible content:
- armature/bone views
- weight-paint heat maps on shoulder/chest and torso
- character in T/posed states
- repeated comparison between armored and underlying body/skeleton
- hand/weapon-grip relation checks toward the end

AETHERQOR relevance:
- this phase is critical for our gear-on/off requirement and animation regression contract
- operation-level pass must extract actual skinning/attachment behavior without replacing our canonical production skeleton

## P13 — Polearm/halberd weapon modeling
Approx. 48:20–54:30

Visible content:
- weapon starts from simple low-poly shaft/head forms
- head silhouette developed symmetrically
- inner diamond/opening and hooked/flared side forms
- shaft, blade and decorative transitions refined
- grip/wrap geometry added
- ornamental relief/detail appears on weapon blade/shaft
- UV-like striped/packed views for weapon subparts near the end

Interpretation:
- weapon is treated as a first-class modeled asset, not a late placeholder
- useful reference for AETHERQOR `weapon` slot pipeline

## P14 — Weapon material/UV finalization + final render/pose showcase
Approx. 54:30–55:53

Visible content:
- file/material asset selection
- weapon material lookdev
- final polearm with finished armor character
- final standing/kneeling poses and outro

---

## First-pass structural conclusions

1. The visible workflow is strongly staged: macro armor form -> local component/topology refinement -> detail cleanup -> UV -> material/shader work -> rig/skin/deformation -> weapon -> final presentation.
2. The character is repeatedly checked at full-body scale between local edits. This matters for AETHERQOR because a locally beautiful plate that fails the class silhouette/gameplay scale should not pass.
3. Armor pieces are frequently isolated for editing, then reintegrated visually with adjacent plates/body. This supports a modular-slot production approach rather than one monolithic shell.
4. Feature boundaries and layered plate overlaps are visible throughout the modeling half. Exact operators and modifier order are NOT yet established by this overview pass.
5. UV/material work begins only after the bulk of armor geometry/detail appears mature. That ordering should be preserved in the AETHERQOR pilot unless operation-level evidence contradicts it.
6. Rigging/skinning is a distinct late validation stage, not proof that geometry is finished by itself. AETHERQOR must retain non-bind-pose animation/clipping gates.
7. Weapon production is a substantial dedicated phase and should be represented as a real `weapon` slot in our pipeline.

## Next required pass

Use all 18 `cluster_peaks_6x6` sheets to classify the 647 change clusters into:
- NAVIGATION
- SELECTION
- TRANSFORM
- TOPOLOGY
- MODIFIER
- OBJECT
- UV
- MATERIAL
- RIG/SKIN
- WEAPON
- IMPORTANT_UNKNOWN

Then open only the corresponding `cluster_triplets_3x6` before/peak/after sheets for real modeling operations. Request 24 FPS micro extraction only for unresolved windows. Exact operator names remain `UNKNOWN` until visually proven.
