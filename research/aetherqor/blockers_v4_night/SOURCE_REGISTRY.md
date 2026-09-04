# AETHERQOR V4 NIGHT ULTRA RESEARCH - SOURCE REGISTRY

Scope: resolve five measured production questions, not a general review. Target: mobile AAA, Unity 6 URP, Blender 5.2, 14k character budget, 90-300 px in gameplay.

## P1 - shell soup -> one clean watertight solid

1. CGAL 3D Alpha Wrapping user manual
   https://doc.cgal.org/latest/Alpha_wrap_3/index.html
   Why: exact algorithm contract. Accepts triangle soup, including disconnected/defective inputs. Alpha controls cavity access/detail; offset controls tightness. Documents two-sided wrapping failure mode around holes.

2. CGAL Alpha_wrap_3 free-function reference
   https://doc.cgal.org/latest/Alpha_wrap_3/group__AW3__free__functions__grp.html
   Why: explicitly states output is watertight, 2-manifold, intersection-free and strictly contains triangle soup.

3. CGAL 2023 improvements
   https://www.cgal.org/news/2023/12/17/alpha_wrapping_improvements/
   Why: robustness, speedups, successive LOD wraps, volumetric output, interpretation of alpha as carving-spoon size.

4. SIGGRAPH / ACM paper: Alpha Wrapping with an Offset
   https://doi.org/10.1145/3528223.3530152
   Why: algorithm guarantees, benchmark context, failure/complexity tradeoffs.

5. CGAL SWIG Python example for Alpha_wrap_3
   https://github.com/CGAL/cgal-swig-bindings/blob/main/examples/python/test_aw3.py
   Why: concrete Python call for both mesh and triangle-soup inputs.

6. SideFX Houdini VDB From Polygons
   https://www.sidefx.com/docs/houdini/nodes/sop/vdbfrompolygons.html
   Why: unsigned distance field does not require airtight input; voxel size is explicit detail floor; Preserve Holes uses generalized winding number; kitbashed/self-intersecting inputs discussed.

7. OpenVDB MeshToVolume
   https://www.openvdb.org/documentation/doxygen/MeshToVolume_8h.html
   Why: mesh->SDF/level-set APIs for standalone automation.

8. OpenVDB LevelSetRebuild
   https://www.openvdb.org/documentation/doxygen/LevelSetRebuild_8h.html
   Why: rebuild caveat: mesh->grid conversion closes internal bubbles; resolution changes can affect sign choices.

9. ZBrush DynaMesh PolyGroups
   https://help.maxon.net/zbr/en-us/Content/html/user-guide/3d-modeling/modeling-basics/creating-meshes/dynamesh/polygroups/polygroups.html
   Why: DynaMesh can preserve PolyGroups, but remains voxel-like remeshing and is resolution sensitive.

10. ZBrush ZRemesher hard surfaces
    https://help.maxon.net/zbr/en-us/Content/html/user-guide/3d-modeling/topology/zremesher/hard-surfaces/hard-surfaces.html
    Why: warns low target counts reduce hard-surface quality; recommends PolyGroups/curves/creases.

11. ZBrush ZRemesher reference
    https://help.maxon.net/zbr/en-us/Content/html/reference-guide/tool/polymesh/geometry/zremesher/zremesher.html
    Why: Keep Groups, Freeze Groups, Keep Creases behavior.

## P2 - panel lines / hard armor at 2600 tri

12. Android game texture optimization guidance
    https://developer.android.com/games/optimize/textures
    Why: explicitly says avoid imperceptible detail on small screens and split UV islands at sharp edges to support normal maps.

13. MikkTSpace reference implementation
    https://github.com/mmikk/MikkTSpace/blob/master/mikktspace.h
    Why: baker/render tangent basis must match or sampled normal maps produce shading errors.

14. Normal-map troubleshooting: hard edges and UV seams
    https://www.artstation.com/blogs/typhen/62VP/this-is-normal-4-normal-map-troubleshooting
    Why: practical hard-edge/UV seam relationship for clean hard-surface bakes.

15. Real-time hard-surface character breakdown
    https://www.therookies.co/blog/breakdowns/creating-a-real-time-hard-surface-character-rx-78-2-gundam-breakdown
    Why: production-style rule: preserve silhouette and constructive edges in geometry; remove high-poly-only support loops.

16. Sci-fi ninja production breakdown
    https://80.lv/articles/a-detailed-breakdown-of-making-a-sci-fi-ninja-with-zbrush-and-maya
    Why: Marmoset bake groups/cages and hair-card layering on a real-time character.

## P3 - hair cards, cap facets and blend mode

17. Ornatrix Transfer Normals modifier
    https://ephere.com/plugins/autodesk/max/ornatrix/docs/7/Transfer_Normals_Modifier.html
    Why: explicitly designed for game/realtime mesh hair to transfer distribution-mesh normals and smooth transition between hair planes and the scalp.

18. Ornatrix Maya Transfer Normals
    https://ephere.com/plugins/autodesk/maya/ornatrix/docs/4/Transfer_Normals_operator.html
    Why: same production concept in Maya pipeline.

19. Unity HDRP Hair docs
    https://docs.unity.cn/Packages/com.unity.render-pipelines.high-definition%4016.0/manual/hair-shader.html
    Why: hair cards are standard realtime representation; semi-transparent cards require sorting.

20. Unity transparency/alpha clipping tutorial
    https://learn.unity.com/tutorial/create-translucent-and-transparent-effects-1?version=2020.3
    Why: distinguishes alpha clipping from transparent surface rendering in Unity pipeline.

21. NVIDIA Vulkanised 2026 hair rendering deck
    https://vulkan.org/user/pages/09.events/vulkanised-2026/1145-Jiho-Choi-NVIDIA%201.pdf
    Why: explicitly lists classic hair-card authoring as Make cards -> Place cards -> Tweak mesh normals -> Export -> Tweak materials.

22. FFVII Remake hair discussion linking production breakdown
    https://www.reddit.com/r/blenderhelp/comments/1sxtwzn/how_do_you_create_game_ready_hair_that_looks_like/
    Why: points to the local video research target w8SjXHQ8ASY and specifically notes tweaked normals on hair cards.

## P4 - male/female deformation divergence

23. Reallusion CC5 armor/accessory production workflow
    https://magazine.reallusion.com/2026/05/11/character-creator-5-to-zbrush-accessories-armor-and-cloth-physics-workflow-equipping-alien-characters-for-production/
    Why: rigid shoulder/forearm/knee pieces linked directly to a bone; flexible chest/footwear uses transferred skin weights.

24. Blender weight-paint troubleshooting discussion
    https://community.gamedev.tv/t/how-do-i-fix-this-issue/226126
    Why: stray small weights can move distant clothing/armor; inspect bone-by-bone influences.

25. HeterSkinNet paper
    https://arxiv.org/abs/2103.10602
    Why: skin-weight prediction depends on geometric relation between mesh vertices and bones, not just algorithm identity.

26. RigNet paper
    https://arxiv.org/abs/2005.00559
    Why: rig/weight quality changes with mesh morphology and skeleton placement/topology.

## P5 - silhouette anchors at 64 px

27. Metrics Reloaded - Mask IoU
    https://metrics-reloaded.dkfz.de/metric-library/mask_iou
    Why: key pitfall: IoU is unaware of boundaries, distances, centers and detailed shape arrangement.

28. OpenCV Hausdorff distance extractor
    https://docs.opencv.org/3.0-beta/modules/shape/doc/shape_distances.html
    Why: ready contour-distance metric complementary to IoU.

29. Silhouette representation/matching comparative study
    https://www.sciencedirect.com/science/article/pii/S0262885609002248
    Why: compares occupancy, distance transform, contour signatures, Fourier descriptors, Hu moments, shape context, Hausdorff and more under noise/view changes.

30. 2025 game-character silhouette identifiability study
    https://www.kci.go.kr/kciportal/landing/article.kci?arti_id=ART003240384
    Why: League of Legends/Overwatch examples; key form elements remain decisive for identity even when skin silhouette changes.

31. Inner-distance shape classification
    https://pubmed.ncbi.nlm.nih.gov/17170481/
    Why: shape descriptor robust to articulation and useful where simple overlap metrics are insufficient.

## Existing local material to reuse, not redownload

Existing V3 package should already be local at:
D:\AetherqorFoundry\research\blockers_v3\CLAUDE_VIDEO_REPORT_33904162671

Reuse especially:
- b3_riot_character_art for P5 silhouette/readability
- b4_game_asset_optimization for P2 geometry/detail budgeting
- b6_marmoset_bakes for P2 normal/AO bake workflow
- b7_hair_cards_quick and b7_long_hair_cards for P3 hair layering and card density

Do not repeat general modular-gear research already closed by prior work.
