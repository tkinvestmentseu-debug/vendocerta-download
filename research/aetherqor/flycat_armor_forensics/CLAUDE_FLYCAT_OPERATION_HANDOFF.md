# AETHERQOR — FLYCAT ARMOR OPERATION FORENSICS -> CLAUDE CODE REPLAY

Local root after workflow success:
`D:\AetherqorFoundry\research\flycat_armor_forensics\hQhTGMk47qI`

## Mission
Reverse-engineer every VISIBLE modeling operation in FlyCat's public armor tutorial and convert the sequence into an auditable, deterministic Blender 5.2/AETHERQOR production recipe. The goal is not to imitate mouse coordinates. The goal is to reproduce the same modeling logic, topology decisions, modifier order, selection logic and shape-building sequence with Blender Python/MCP wherever possible.

## Read order
1. `TARGET.md`
2. `manifest.json`
3. `transcript.txt` or `TRANSCRIPT_MISSING.txt`
4. `frame_index.csv`
5. `sheet_index.csv`
6. ALL `contact_sheets_3x3` sequentially
7. `dense_8fps_index.csv`
8. ALL `dense_sheets_8fps_6x6` sequentially
9. selected full-resolution `dense_frames_8fps`
10. 24 FPS MICRO windows for ambiguous operations
11. current AETHERQOR character/gear code, assets, contracts and closed research decisions

## Operation ledger
Create `FLYCAT_OPERATION_LEDGER.csv` with columns:
`seq,start_time,end_time,body_region,object,mode,selection_state,observed_ui_action,likely_blender_operator,hotkey_or_mouse,parameters,modifier_stack_before,modifier_stack_after,visible_result,confidence,evidence_frames,aetherqor_equivalent,automation_method`.

Confidence values only:
- `OBSERVED`
- `INFERRED_HIGH`
- `INFERRED_MEDIUM`
- `UNKNOWN`

Never fabricate a hotkey/click. If the public edit skips it, record `UNKNOWN` while still describing the before/after geometry state.

## Phase segmentation
Build `FLYCAT_PHASES.md`. Segment the entire 55:52 video by actual workflow, not arbitrary time chunks. For each phase record:
- exact time range;
- armor/body part;
- source geometry used;
- topology construction method;
- symmetry/mirror use;
- extrusion/inset/bevel/subdivision/sculpt operations;
- shrink/fit relation to body;
- modifier order;
- edge support strategy;
- thickness strategy;
- cleanup/retopo step;
- UV/material/rig step if visible;
- whether the operation is directly reusable in AETHERQOR.

## Dense-review rule
Use 1 FPS only for navigation. 8 FPS is the normal operation-analysis evidence. If an operator/menu/click cannot be distinguished at 8 FPS, run the local segment extractor at 24 FPS around that exact interval, normally 1-5 seconds before/after. Do not generate 24 FPS for the whole video unless necessary.

## Required technical reconstruction
For every armor component shown, identify:
1. starting mesh/source;
2. whether geometry is duplicated/extracted from body or built separately;
3. Edit/Object/Sculpt mode transitions;
4. vertex/edge/face selection intent;
5. extrude/inset/scale/slide/loop-cut/knife/bevel actions;
6. Mirror/Subdivision/Solidify/Shrinkwrap/etc. order if visible;
7. exact numeric values when UI shows them;
8. crease/sharp/support-loop strategy;
9. topology density added for silhouette vs surface detail;
10. how plates overlap and terminate;
11. how the model avoids paper-thin or melted armor appearance;
12. how hands/gauntlets/boots/torso/shoulders are treated differently;
13. when detail is geometry versus texture/bake;
14. rig/weight implications if shown.

## AETHERQOR conversion
Create `FLYCAT_TO_AETHERQOR_MAPPING.md` with three classifications per technique:
- `ADOPT_DIRECTLY`
- `ADAPT_TO_AETHERQOR`
- `DO_NOT_ADOPT`

Reasons must reflect AETHERQOR constraints: mobile 90-300 px, screen-space proof, modular slots, donor fidelity, Alpha Wrap already proven for soup cleanup, 14k current target as an allocation constraint rather than blind per-slot decimation, Unity 6 URP, existing rig/retarget system.

Do NOT reopen closed soup-remesher research. Use Alpha Wrap where needed, but the purpose here is to learn FlyCat's clean intentional hard-surface construction and feature hierarchy.

## Deterministic replay
Create a reusable Blender 5.2 implementation under project tooling, not a mouse macro. Prefer `bpy` data API/operators plus Blender MCP checks. Required output:
- `flycat_armor_recipe.md`
- `flycat_armor_replay.py` or a modular set of scripts
- `flycat_armor_parameters.json`
- `FLYCAT_REPLAY_LIMITS.md`

The script must separate:
- deterministic operations that can be fully automated;
- artist/vision-dependent selections that require semantic inputs;
- operations impossible to recover exactly from the edited public video.

## Real AETHERQOR pilot
Do not stop at documentation. Pick one AETHERQOR body/slot where this method is appropriate and make a controlled pilot using the FlyCat-style construction order. Prefer a clean hard-surface slot where donor fidelity can be measured, not a closed problem already solved better by Alpha Wrap.

Compare CURRENT vs FLYCAT-STYLE at:
- donor silhouette/contour similarity front/3-4/side/game camera;
- triangle count;
- macro-edge survival;
- visible faceting at 90/150/220/300 px;
- body penetration/clipping;
- animation/deformation where relevant;
- build/runtime compatibility.

## Final files
- `FLYCAT_OPERATION_LEDGER.csv`
- `FLYCAT_PHASES.md`
- `FLYCAT_ARMOR_MASTER_RECIPE.md`
- `FLYCAT_TO_AETHERQOR_MAPPING.md`
- `FLYCAT_REPLAY_LIMITS.md`
- deterministic Blender scripts/parameters
- pilot metrics and proof renders
- checkpoint commit

Allowed final verdicts for the pilot: `IMPLEMENTED_PASS`, `IMPLEMENTED_FAIL`, `RESEARCH_CONFIRMED_NEEDS_ENGINEERING`.

## Important source limitation
The public video is an edited tutorial. FlyCat's separate creator package is described publicly as 33 HD process videos with normal-speed/accelerated sections and Blender project files. Those private/paid files are NOT part of this evidence unless the owner separately obtains and supplies them. Therefore the ledger must distinguish visible facts from reconstruction/inference.
