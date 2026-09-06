# FLYCAT_BLENDER_44_TO_52_MAP

Target is Blender 5.2. Reproduce observed modeling intent with stable data APIs instead of matching every Blender 4.4 UI gesture.

## Mapping

- Plate-boundary shaping: bmesh vertex and edge coordinate edits using named regions.
- Separate modular plate: create a new mesh from an explicit boundary or selected source faces.
- Repeated finger and skirt plates: duplicate from a recipe with explicit transforms.
- Symmetric armor: Mirror modifier or mirrored geometry generated from the recipe.
- Thickness: Solidify with explicit thickness and offset.
- Edge control: Bevel or support-loop generation with explicit width and segment values.
- Raised ring or boss: parametric profile, extrusion and bevel.
- Secondary ridges: direct mesh strips or curve-derived mesh selected by the part recipe.
- UV: deterministic unwrap and pack only after geometry passes QA.
- Materials: Principled BSDF with stable material slots.
- Rig binding: Armature modifier referencing the canonical AETHERQOR skeleton.
- Rigid plate weighting: minimal controlling bones, normalized weights, capped influences.
- Pose QA: known test poses and clips with numeric clearance checks.

## Rules

1. Apply object scale before thickness, bevel and export validation.
2. Prefer bmesh and direct bpy data properties over context-sensitive operators.
3. Give every generated part a stable name, slot tag and recipe version.
4. Keep modifier order explicit and validate it after creation.
5. Measure geometry before and after modifiers.
6. Use explicit export axis, scale, armature and animation settings.
7. Replay must be idempotent and may modify only its own generated outputs.
8. Source assets and unrelated work remain read-only.

## Recommended rigid-plate order

macro fit -> symmetry -> thickness -> bevel/edge control -> normals if required -> armature deformation

This order is the AETHERQOR replay policy where the exact source modifier stack is not directly observable.
