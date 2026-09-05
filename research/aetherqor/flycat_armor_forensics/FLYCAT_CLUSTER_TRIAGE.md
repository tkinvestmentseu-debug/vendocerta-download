# FLYCAT_CLUSTER_TRIAGE

Status: PASS 2 COMPLETE — all cluster-peak sheets reviewed

Source evidence: `AETHERQOR_FLYCAT_SEMANTIC_REVIEW`
- 647 change clusters total (`C0001`–`C0647`)
- 18 sequential `cluster_peaks_6x6` sheets
- one representative peak frame per cluster
- whole-video phase map already recorded in `FLYCAT_PHASES.md`

Important limitation: this pass is semantic triage from peak frames only. It does **not** establish exact operators, hotkeys, modifier order, or numeric parameters. Exact operation claims require `BEFORE -> PEAK -> AFTER` triplet review, with 24 FPS micro extraction only where the triplet remains ambiguous.

## Coverage by phase

| Phase | Approx. time | Cluster range | Count | Dominant visible activity |
|---|---:|---:|---:|---|
| P00 | 00:00–00:55 | C0001–C0006 | 6 | finished-character showcase / reference |
| P01 | 00:55–03:20 | C0007–C0046 | 40 | early armor blockout / macro silhouette |
| P02 | 03:20–06:00 | C0047–C0092 | 46 | helmet, neck, forearm, small component refinement |
| P03 | 06:00–09:00 | C0093–C0138 | 46 | torso/chest/helmet/arm topology refinement |
| P04 | 09:00–12:00 | C0139–C0187 | 49 | gauntlets, hip ornament, thigh, shin/greave work |
| P05 | 12:00–15:00 | C0188–C0236 | 49 | shoulder/chest/leg refinement and plate overlaps |
| P06 | 15:00–18:00 | C0237–C0293 | 57 | skirt/loin/cloth-adjacent armor, decorations, cleanup |
| P07 | 18:00–24:30 | C0294–C0369 | 76 | full-set refinement and ornamental-detail pass |
| P08 | 24:30–27:00 | C0370–C0389 | 20 | boots/attachments, then UV preparation/packing |
| P09 | 27:00–30:00 | C0390–C0425 | 36 | file/material handoff and Blender shader setup |
| P10 | 30:00–39:30 | C0426–C0552 | 127 | material lookdev / surface differentiation |
| P11 | 39:30–43:30 | C0553–C0587 | 35 | UV / normal / mask / texture verification |
| P12 | 43:30–48:20 | C0588–C0622 | 35 | rigging / skinning / weight-paint / deformation checks |
| P13 | 48:20–54:30 | C0623–C0636 | 14 | polearm/halberd modeling and weapon UV work |
| P14 | 54:30–55:53 | C0637–C0647 | 11 | weapon material finalization / final presentation |

## Semantic findings from all 647 peaks

### Geometry/modeling half (P01–P08)
- The workflow repeatedly alternates between isolated-part closeups and full-character checks.
- Armor remains visibly modular: helmet/neck pieces, torso/chest, shoulders, forearms, gauntlets, hip/waist parts, thigh plates, greaves/boots and skirt/loin components are worked as distinguishable pieces rather than one monolithic shell.
- Wire/topology views recur throughout the modeling pass, especially on torso, shoulder, limb and lower-body plate regions.
- Plate boundaries and overlap relationships are established during modeling, before the UV/material phase.
- Large-form silhouette is checked repeatedly before and during local detail refinement.
- Ornament/detail work is visibly later than the first-pass macro forms.
- Around 25:45–26:00 the visual workflow transitions decisively from geometry closeups to UV/layout work.

### Material / UV half (P09–P11)
- Geometry is largely mature before extended shader/material work begins.
- The character is evaluated as a whole while multiple material families are tuned, with visibly distinct metal, leather/cloth, chainmail and accessory regions.
- Normal-looking purple maps, grayscale masks, packed atlases and subset-specific texture views appear in the verification phase.
- Peak frames alone are insufficient to prove exact channel semantics; these remain unresolved until targeted UI/triplet review.

### Rigging / deformation (P12)
- Armature views, weight-paint heat maps, T/posed states and shoulder/torso deformation checks are clearly visible.
- Rig/skin work is a distinct late validation stage after geometry and material assembly.
- This supports keeping AETHERQOR's non-bind-pose clipping/deformation gate separate from the modeling gate.

### Weapon (P13–P14)
- The polearm/halberd is developed as a real first-class asset from simple shaft/head forms through silhouette, internal cutout, hook/flared side forms, grip/wrap details, ornament and UV/material work.
- This reinforces the AETHERQOR decision to treat `weapon` as a first-class slot with its own geometry/material/LOD/QA contract.

## High-value triplet-review targets

The next pass must prioritize real modeling transitions rather than navigation or material-preview noise. Review triplets first for:
1. shell/plate creation or separation from the body/base surface;
2. explicit plate-boundary changes on torso/chest, shoulder, thigh and greave parts;
3. edge-control changes that alter silhouette or highlight behavior;
4. thickness creation / shell depth changes;
5. overlap/layer ordering between adjacent plates;
6. symmetry/mirror-like state changes on armor or weapon parts;
7. visible topology changes around gauntlets/fingers and curved plate junctions;
8. rig/weight changes where before/after deformation differs;
9. weapon head silhouette and internal-opening construction;
10. any UI state showing a modifier/operator name or numeric parameter clearly enough to support `OBSERVED`.

## Confidence policy for next pass

- `OBSERVED`: operator/modifier/state transition is directly visible or uniquely determined by UI/state change.
- `INFERRED_HIGH`: geometry state strongly constrains the operation but UI does not prove the exact command.
- `INFERRED_MEDIUM`: several plausible Blender operations could explain the same state transition.
- `UNKNOWN`: public edit/cut or insufficient evidence prevents a defensible reconstruction.

## Next required output

Build `FLYCAT_OPERATION_LEDGER.csv` from selected `cluster_triplets_3x6` evidence. Do not open all 108 triplet sheets blindly. Use this peak pass to target only real modeling/rig/weapon operations, and request 24 FPS micro evidence only for short unresolved windows.