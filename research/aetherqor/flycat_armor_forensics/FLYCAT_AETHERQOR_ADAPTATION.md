# FLYCAT_AETHERQOR_ADAPTATION

## Purpose
Translate the observed FlyCat armor workflow into a deterministic mobile AETHERQOR pipeline while preserving the canonical body, skeleton and modular gear behavior.

## Rules

1. Body_Rigged is authoritative for scale, skeleton, bind pose and deformation envelope.
2. Each gear slot is generated and validated independently. Gear-on and gear-off must work without rebuilding the body.
3. Donor geometry is a visual/form reference. Generated replay output is written to isolated output paths and never replaces the source asset.
4. Macro silhouette and plate boundaries are resolved before thickness, bevel, ornaments, UV and material work.
5. Rigid plate pieces use minimal controlling bones. Cloth-like or flexible pieces may use broader weighting only when deformation requires it.
6. Body penetration is measured in bind pose and representative animation poses before Unity promotion.
7. Screen-space review is mandatory at 90, 150, 220 and 300 px character height. Small relief that does not survive gameplay scale is baked rather than retained as geometry.
8. Final slot budgets follow the existing AETHERQOR mobile allocation. The pilot records actual triangle count rather than assuming compliance.
9. Materials target Unity 6 URP PBR. Source channels are mapped explicitly and import settings are recorded.
10. Every run emits JSON metrics, deterministic names, source hashes where available and a replay version.

## Pilot choice
Use one rigid armor slot with clear macro boundaries and animation exposure. Chest is preferred when an isolated chest donor is already available; otherwise Shoulders or Greaves are acceptable. The runner must choose an existing local source and must not call external generation services.

## QA gates

### Geometry
- valid mesh and finite coordinates
- no accidental loose fragments in generated slot
- explicit thickness on visible shell edges
- macro ridges and major overlaps survive simplification
- triangle count recorded before and after replay modifiers

### Donor fidelity
Compare generated slot bounds and rendered silhouette against the selected local source. Record normalized projected silhouette overlap when both renders can be produced consistently. If not, record image dimensions and a documented visual gate rather than fabricating a metric.

### Screen space
Render the isolated fitted slot/body at character heights 90, 150, 220 and 300 px. Record macro-edge survival and visible faceting for every target size.

### Body penetration
Evaluate the armor against Body_Rigged in bind pose and representative torso/limb poses. Record intersection findings and minimum intentional gap where measurable.

### Rig and animation
Confirm armature modifier, expected vertex groups, weighted coverage and deformation under at least one non-bind pose. Rigid panels must not appear rubbery.

### Gear on/off
Unity import must permit the slot renderer/object to be disabled without affecting the body renderer, skeleton or unrelated slots.

### Material
Verify material slot count, texture references, URP-compatible import and absence of missing-material fallback.

## Promotion policy
The pilot remains isolated until all measured gates are recorded. Passing technical checks does not automatically replace production gear. Promotion requires the pilot result file and visual review evidence.
