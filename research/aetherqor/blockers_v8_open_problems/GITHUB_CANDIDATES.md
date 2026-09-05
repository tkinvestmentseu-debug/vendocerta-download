# AETHERQOR V8 — GITHUB CANDIDATES

Do not vendor a repository because its README sounds useful. First verify license, Unity/Blender version assumptions, algorithm fit, maintenance state and build a minimal AETHERQOR pilot. No replacement of working local code without proof.

| Project | Area | License | V8 use | Decision now |
|---|---|---|---|---|
| `umasteeringgroup/UMA` | modular avatar / skinned mesh combining | MIT | study production-grade bone/mesh/overlay combination patterns | STRONG_REFERENCE, PILOT SELECTED PARTS |
| `Whinarn/UnityMeshSimplifier` | Unity mesh simplification/combining | MIT | inspect MeshCombiner and simplification utilities | REFERENCE/PILOT, not automatic adoption |
| `itsFulcrum/Unity-URP-Hair-Shader` | URP hair cards shader | CC0-1.0 | A4 controlled material A/B, anisotropic highlight breakup | SAFE ALGORITHM DONOR after Unity 6 port/test |
| `cathyhlshih/UnityURPAnisoHighlightHairShader` | URP Shader Graph anisotropic hair | MIT | second A4 implementation/reference | SAFE REFERENCE/PILOT |
| `jpcy/xatlas` | UV parameterization/atlas | MIT | A2 controlled UV alternative if geometry-space curvature is insufficient | EXPERIMENT ONLY |
| `lxteo/UnitySkinnedMeshCombiner` | skinned mesh combine + bones/blendshapes | no license metadata observed | B3 algorithm comparison | REFERENCE ONLY, DO NOT COPY CODE |
| `fedackb/mesh-fairing` | Blender mesh fairing | no license metadata observed | A1 conceptual comparison to CGAL/local fairing | REFERENCE ONLY, DO NOT COPY CODE |
| `Unity-Technologies/UnityCsReference` | Unity editor/importer reference source | Unity reference license, not generic MIT donor | B2 understand material importer/remap behavior | READ ONLY / API BEHAVIOR REFERENCE |

## B3 pilot rules — skinned combine

Candidate code must prove all of the following on ONE AETHERQOR promoted character before broader integration:

1. Bone identity resolved by stable skeleton path/semantic ID, not object suffix accident.
2. Every source bone index remapped to destination bone index.
3. Bindposes correspond 1:1 to destination bones.
4. Bone weights preserved numerically, including influence normalization/limits used by project.
5. Submeshes/material-family mapping preserved or intentionally merged.
6. Normals, tangents, UVs and colors preserved.
7. Blendshapes preserved where present.
8. No `.001` silent skeleton/material identifier drift.
9. Animation regression across all 21 current clips.
10. Compare deformed geometry/render before vs after in non-bind poses.

UMA is the strongest open-source reference because it is an actual modular-avatar framework and MIT licensed. Do not copy the small unlicensed `lxteo` project even if its code is simpler.

## A4 pilot rules — hair shader

`itsFulcrum/Unity-URP-Hair-Shader` is explicitly experimental and originally tested on Unity 2021.3, so V8 must not drop it into production blindly. Port only the minimal ideas required for measurement:

- anisotropic tangent-based highlight direction,
- normal map support,
- alpha card handling,
- anisotropic noise/highlight breakup.

Compile on Unity 6 URP, then compare current vs candidate on the exact same hair mesh at true gameplay scale. Measure shader variants, passes, overdraw/GPU cost and temporal stability.

`cathyhlshih/UnityURPAnisoHighlightHairShader` provides an MIT Shader Graph reference and can be used as a second implementation check.

## A2 pilot rules — xatlas

Do not use xatlas as a reflexive cure for 461 islands. First change cavity source to geometry-space curvature. Only if Unity still shows seams after that:

- run xatlas or equivalent on a duplicate mesh,
- measure chart count,
- texel density distribution,
- stretch/distortion,
- donor bake error,
- seam length,
- final Unity artifact score.

Fewer islands is not automatically better if it destroys density or creates bake distortion.

## A1 pilot rules — fairing

Feature-preserving fairing/smoothing is only allowed AFTER the donor-crop/Alpha-Wrap causality test. Do not smooth the whole cuirass. Build a terrace detector and select only suspect vertices/regions; preserve hard feature edges and enforce donor-distance/silhouette limits.

## Dependency policy

Every third-party candidate must be classified:

- `ADOPT`: license verified, tests pass, dependency acceptable.
- `PORT_IDEA`: reimplement small algorithmic idea locally with attribution/license compliance where required.
- `REFERENCE_ONLY`: study, do not copy.
- `REJECT`: wrong problem, stale/incompatible, or loses QA.

Record exact commit/tag inspected in `EXTERNAL_CODE_EVALUATION.csv` so future builds do not silently change behavior.
