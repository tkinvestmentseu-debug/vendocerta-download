# FLYCAT_ARMOR_MASTER_RECIPE

## Scope
Deterministic reconstruction of the observable FlyCat armor-production logic for AETHERQOR. This is an evidence-derived production recipe, not a claim of exact hidden hotkeys or unpublished source values.

## 1. Start from canonical character and class silhouette
- Use the canonical AETHERQOR body and skeleton as immutable references.
- Establish class silhouette at full-body/gameplay scale before local ornament.
- Create armor as modular addressable parts, not one fused shell.
- Required slots for the pilot: chest, shoulder, helmet, gauntlet, hip/skirt, thigh, greave plus secondary ornaments/attachments.

## 2. Macro plate construction
For each plate:
1. define the visible boundary and silhouette;
2. fit against the body clearance envelope;
3. keep adjacent plates separate;
4. validate full-body silhouette;
5. only then add thickness and secondary forms.

The source repeatedly shows explicit boundary/topology edits before material work. AETHERQOR should preserve that order.

## 3. Overlap hierarchy
- Encode a deterministic front-to-back plate order.
- Keep a measurable clearance gap between overlapping rigid shells.
- Do not let later smoothing/remeshing erase plate boundaries.
- Recheck overlaps in torso twist, shoulder elevation, hip flex, knee bend and ankle flex poses.

## 4. Edge control and thickness
- Silhouette-critical edges stay explicit in topology.
- Add controlled thickness only after the 2D/3D boundary is approved.
- Use support loops or bevel-like edge control only when it improves highlights at gameplay scale.
- Do not spend topology on subpixel detail that can be baked.

## 5. Secondary forms and ornament
- Secondary ridges, bosses, temple attachments, hip ornaments and straps are separate authoring features.
- Add them after macro armor fit passes.
- Geometry is reserved for silhouette-scale relief.
- Fine engraving and microrelief may be represented in baked normal/AO when it does not affect silhouette.

## 6. Gauntlet strategy
- Build one representative finger plate first.
- Parameterize repetition across digits.
- Keep plates separable enough to preserve articulation.
- Validate open hand, fist and grip poses before acceptance.

## 7. UV and material order
- UV work begins only after geometry/detail maturity.
- Process islands per modular slot or logical subset.
- Preserve texel density and predictable grouping.
- Map source materials to deterministic URP-compatible PBR data rather than copying opaque shader graphs.
- Perform a whole-character material consistency pass after local material setup.

## 8. Rigging and deformation
- Keep the canonical AETHERQOR skeleton.
- Rigid plates should have minimal necessary controlling-bone influence.
- Shoulder and torso armor require rigid-zone weighting rather than soft gradients across hard plates.
- Helmet follows the head rigidly while preserving neck/face clearance.
- Lower-body plates require explicit hip, knee and ankle pose tests.

## 9. Required QA gates
Every armor slot must pass:
- donor/silhouette fidelity against reference;
- gameplay-distance screen-space readability;
- manifold/clean topology checks;
- no body penetration in rest pose;
- no unacceptable clipping in non-bind poses;
- material ID and PBR sanity;
- deterministic replay from input parameters;
- reproducible export to Unity.

## 10. Confidence discipline
- OBSERVED: directly visible state transition.
- INFERRED_HIGH: geometry strongly constrains the likely method.
- INFERRED_MEDIUM: several Blender methods remain plausible.
- UNKNOWN: the public edit does not support a defensible reconstruction.

When an exact source command is unknown, implement the simplest deterministic Blender 5.2 operation that reproduces the observed geometric intent. Source-command parity is lower priority than geometric and deformation fidelity.

## 11. Pilot target
The first production pilot should be one isolated armor slot with:
- macro shell;
- at least one layered overlap;
- one secondary ornament;
- explicit thickness/edge treatment;
- skinning to canonical skeleton;
- Blender pose QA;
- Unity import and animation/clipping QA;
- measured result committed on an isolated implementation branch.
