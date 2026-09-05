# AETHERQOR V8 — SOURCE REGISTRY

Purpose: authoritative docs first, production breakdowns second, developer forums/community as supporting evidence only. Video evidence lives in `videos.psv` and must be verified frame-by-frame before promotion to a conclusion.

## A1 — terrace/fairing/feature-preserving surface repair

- CGAL Polygon Mesh Processing manual — fairing, smoothing, tangential relaxation, feature detection: https://doc.cgal.org/latest/Polygon_mesh_processing/index.html
- CGAL fair(): https://doc.cgal.org/latest/Polygon_mesh_processing/group__PMP__meshing__grp.html
- CGAL global remeshing / constrained edges: https://doc.cgal.org/latest/Polygon_mesh_processing/group__PMP__meshing__grp.html
- Use only as candidate after Alpha Wrap. V8 must test local terrace reduction versus donor fidelity; no claim that fairing is automatically correct for armor.

## A2 — curvature vs UV-space cavity

- Blender Geometry/Pointiness documentation: https://docs.blender.org/manual/en/latest/render/shader_nodes/input/geometry.html
  Pointiness is a Cycles curvature approximation based on mesh geometry, not a 2D Gaussian blur over UV space.
- Marmoset Toolbag baking tutorial / curvature: https://marmoset.co/posts/toolbag-baking-tutorial/
- Adobe Substance curvature baker: https://helpx.adobe.com/substance-3d-bake/bakers/curvature.html
  Includes seam-handling concepts and geometry-derived curvature.
- xatlas: https://github.com/jpcy/xatlas — controlled UV parameterization candidate only if geometry-space bake does not solve runtime artifact.

## A3 — boot/game-scale shape readability

- V8 video evidence uses game-character hard-surface/accessory and LOD material already validated by the runner. The important local proof is donor -> pre-decim -> post-decim -> gameplay LOD comparison at 90/150/300 px.
- Marmoset normal/bake material remains supporting evidence that maps cannot restore missing silhouette.

## A4 — hair material and real screen scale

- Unity URP hair shader reference, CC0: https://github.com/itsFulcrum/Unity-URP-Hair-Shader
- Shader demo video: https://www.youtube.com/watch?v=EmU62lWMhSU
- Alternative URP anisotropic shader, MIT: https://github.com/cathyhlshih/UnityURPAnisoHighlightHairShader
- Production hair-card evidence in V3/V4/V5/V6 should be reused. V8 question is not another card-construction pass; it is whether the observed defect survives correct Unity material + target screen scale.

## A5 — anomalous source/provenance

- No external source can tell us why one AETHERQOR pauldron is 15,208 tri. External research is only for mesh/component inspection patterns. Root cause must come from local provenance, connected components, bbox/anatomical overlap, asset path/hash and generator logs.

## B1/C2 — male/female refit and class identity

- Riot Games, Clarity in League: https://www.leagueoflegends.com/en-us/news/dev/clarity-in-league/
  Primary characteristic and silhouette are central to recognition; model/animation/VFX all participate in clarity.
- Valve Dota 2 Character Art Guide: https://help.steampowered.com/en/faqs/view/0688-7692-4D5A-1935
  Character must read from gameplay/top-down view; game view takes priority.
- V4/V5 rig/clothing transfer video evidence should be reused for deformation mechanics.
- Community discussions about female armor are NOT authority for AETHERQOR art direction. C2 remains owner decision after comparable proofs.

## B2 — Unity FBX material loss/remap

- Unity 6 Model Importer Materials: https://docs.unity.cn/6000.2/Documentation/Manual/FBXImporter-Materials.html
- Unity `ModelImporter.SearchAndRemapMaterials`: https://docs.unity.cn/ScriptReference/ModelImporter.SearchAndRemapMaterials.html
- Unity `AssetImporter.AddRemap`: https://docs.unity3d.com/cn/current/ScriptReference/AssetImporter.AddRemap.html
- Unity `ImportViaMaterialDescription`: https://docs.unity.cn/6000.1/Documentation/ScriptReference/ModelImporterMaterialImportMode.ImportViaMaterialDescription.html
- Unity AssetPostprocessor documentation: https://docs.unity3d.com/ScriptReference/AssetPostprocessor.html
- UnityCsReference ModelImporter material UI/remap behavior: https://github.com/Unity-Technologies/UnityCsReference/blob/master/Modules/AssetPipelineEditor/ImportSettings/ModelImporterMaterialEditor.cs

Interpretation to test: Unity project Material assets should be authoritative; FBX should preserve stable semantic slot/material identifiers and importer should remap deterministically instead of relying on fragile embedded round-trip state.

## B3 — SkinnedMeshRenderer aggregation

- Unity API/manual for Mesh, SkinnedMeshRenderer, bone weights and bindposes. Verify against Unity 6 installed docs/API before implementation.
- Unity developer discussions on combining skinned meshes and bindpose/bone-index relationships.
- UMA, MIT: https://github.com/umasteeringgroup/UMA
- `UMAProject/Assets/UMA/Core/StandardAssets/UMA/Scripts/SkinnedMeshCombiner.cs` is a real open-source reference implementation.
- Whinarn UnityMeshSimplifier, MIT: https://github.com/Whinarn/UnityMeshSimplifier — includes mesh combining utilities; inspect applicability before adopting.
- lxteo UnitySkinnedMeshCombiner: https://github.com/lxteo/UnitySkinnedMeshCombiner — useful algorithm reference but repository exposes no license metadata; DO NOT COPY without license clarification.
- Community supporting evidence: runtime combine can be done on equip/confirm rather than per-frame; performance claims must be measured in AETHERQOR, especially Unity 6 URP.

## B4/B5/C1 — class anchors, weapons and recognition

- Valve Dota 2 Character Art Guide: https://help.steampowered.com/en/faqs/view/0688-7692-4D5A-1935
- Riot Clarity in League: https://www.leagueoflegends.com/en-us/news/dev/clarity-in-league/
- Neither source establishes a universal anchor-height percentage or IoU threshold. They support evaluation in actual gameplay view and stable primary identity cues.

## B6 — shield/backpiece attachment

- Use local skeleton/transform diagnostics first. V4 clothing/rig attachment evidence can inform bone ownership, but the actual root cause is AETHERQOR-specific.

## C3 — visual tier bands

- Reuse V7 URP emission/material-parameter evidence.
- Do not use global Bloom as sole carrier of rank identity. Compare day/night/no-bloom under controlled exposure in Unity 6 URP.

## Developer forum / community sources — supporting, not normative

- Unity Discussions for material remap, skinned combine, bindposes and blendshapes.
- Reddit r/Unity3D/r/gamedev discussions on modular character combining, draw calls and runtime combine. Treat anecdotes as hypotheses, not performance proof.
- Polycount discussions on UV seams/curvature and hair-card specular are useful workflow experience, but local Unity proof wins.

## Evidence quality labels

- A: official engine/library/studio documentation.
- B: production tutorial or source code with clear provenance/license.
- C: forum/community experience.
- D: hypothesis/local inference pending experiment.

Every final V8 verdict must distinguish these levels and attach local proof metrics.
