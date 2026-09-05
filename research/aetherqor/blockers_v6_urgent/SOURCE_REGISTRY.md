# AETHERQOR V6 — SOURCE REGISTRY

Evidence policy:
- PRIMARY/OFFICIAL: engine/vendor/game-developer documentation or first-party art guide.
- PRODUCTION BREAKDOWN: experienced production artist/tutorial with concrete workflow.
- EXTRACTED/REUPLOAD: useful only as a range clue, never as an official studio budget.
- HYPOTHESIS: AETHERQOR engineering proposal requiring local measurement.

## P1 — triangle architecture / quality variants

### PRIMARY/OFFICIAL

1. Microsoft Game Dev / Simplygon — Automated Asset Optimization for Mobile Games with Simplygon
https://developer.microsoft.com/en-us/games/articles/2025/10/automated-asset-optimization-for-mobile-games-with-simplygon/
Evidence: mobile devices span low/mid/high capability; optimize differently per device; always review on actual mobile/in camera context; character-focused mobile games often maintain a highly detailed focus version and a lower-resolution gameplay version; rig/bone/influence reduction is part of the budget.

2. Simplygon — Low-poly character optimization
https://www.simplygon.com/blog/0179d2c5-a440-49d7-850a-0a9a94152d1b
Evidence: recommends OnScreenSize or maximum deviation over one triangle ratio/count because assets tolerate reduction differently. Their worked mobile example is 3.7k source -> 2.8k at 100px -> 2.1k at 60px -> 1.0k at 30px. This is NOT an AAA character budget; it is strong evidence for screen-space-driven architecture.

3. Microsoft Game Dev — Four Fundamental Simplygon Tools for Automated Character Optimization
https://developer.microsoft.com/en-us/games/articles/2025/09/four-fundamental-simplygon-tools-for-automated-character-optimization/
Evidence: production character optimization combines triangle reduction, vertex weights, bone reduction and material merging rather than one global mesh ratio.

4. Microsoft Game Dev — 3 Advanced Simplygon Tools to Improve Your Automated Character LOD Pipeline
https://developer.microsoft.com/en-us/games/articles/2025/11/simplygon-tools-automated-character-lod-pipeline/
Evidence: near-camera character LODs need topology preservation; quad reduction is specifically presented for close character LOD work.

5. Valve Dota 2 Workshop — Item Model Requirements
https://help.steampowered.com/en/faqs/view/5FB8-4078-8B2A-C52B
Evidence: separate LOD0 and LOD1; LOD0 is close/loadout/showcase, lower LOD1 is normal top-down gameplay; LOD0 can be ~2x as detailed depending on hero/item/budget; polygon density is concentrated where silhouette/deformation and prominent edges need it.

### EXTRACTED/REUPLOAD — RANGE ONLY, NOT OFFICIAL LIMITS

Wuthering Waves public reuploads show large variation that likely mixes character versions/accessories/exports:
- Chixia: ~30.1k tris https://sketchfab.com/3d-models/chixia1-1-wuthering-waves-7d2dd67016924805951e9e9eef543761
- Jianxin: ~33.3k tris https://sketchfab.com/3d-models/jianxin1-03-wuthering-waves-508d7a068fbb48d2b10f52bf70ddcd53
- Danjin: ~33.8k tris https://sketchfab.com/3d-models/danjin1-1-wuthering-waves-da237b367d5649a39e8bb13dda0eb505
- Encore: ~36.1k tris https://sketchfab.com/3d-models/encorenew1-1-wuthering-waves-7bfa0d20d0bd4422a35d56cef71e9de6
- Carlotta: ~91.3k tris https://sketchfab.com/3d-models/carlotta-montelli-wuthering-waves-a0798264c0c3458bbe8960cbcd34a82c
- Lynae: ~103.5k tris https://sketchfab.com/3d-models/lynae-from-wuthering-waves-e59593637d424294a7361d428d9147bc
Interpretation: useful evidence that a single internet number is unsafe without LOD/export provenance; NOT proof of Kuro's runtime target.

Genshin public/reuploaded examples:
- Skirk ~28.9k tris, but uploader credits an MMD model: https://sketchfab.com/3d-models/genshin-impact-skirk-e56bdb29d65c4edb82cd853b7312cce4
- older scene claiming an official miHoYo model totals ~28.1k for the scene: https://sketchfab.com/3d-models/genshin-impact-scene-fa345e2979544abe94fa05acf1d62f4b
Again: weak range evidence only.

No trustworthy first-party polygon budget was found for Diablo Immortal, Genshin Impact, Wuthering Waves or Black Desert Mobile. Do not fabricate one. A community/marketplace model named after a game is not proof of that game's runtime geometry.

## P2 — one-sided shell / culling / local thickness

### PRIMARY/OFFICIAL

6. Unity 6 URP Lit Shader material reference
https://docs.unity.cn/Manual/urp/lit-shader.html
Evidence: Render Face Front is default and culls back faces; Render Face Both renders both sides and is intended for small flat objects such as leaves; Alpha Clip is an opaque/cutout-style threshold behavior.

7. Valve Dota 2 Character Art Guide
https://help.steampowered.com/en/faqs/view/0688-7692-4D5A-1935
Evidence: game view has higher priority than loadout; add backface polygons where necessary; triangles should support silhouette/deformation/readability, not hidden geometry by default.

8. Valve Dota 2 Item Model Requirements
https://help.steampowered.com/en/faqs/view/5FB8-4078-8B2A-C52B
Evidence: use geometry for prominent edges when textures cannot support them; each polygon should contribute to silhouette/deformation.

### PRODUCTION BREAKDOWN

9. Michael Pavlovich — Low Resolution Character Creation: Clothing and Accessories Techniques (YouTube course indexed by Class Central)
https://www.classcentral.com/course/youtube-05-low-res-creation-clothing-accessories-geo-reduction-material-ids-vertex-normals-more-271536
Evidence index explicitly includes 'One Sided Cloth Meshes' and 'Edge Extrude for Cloth Assets'. Use as workflow evidence, not a mobile GPU benchmark.

10. FastTrack / game-ready character workflow transcription
https://www.skillshare.com/en/classes/creating-3d-game-characters-for-games-and-film-part-two-game-ready/386921736
Evidence: artist selectively models thickness where the side of a cloth piece must read, deletes inner/extra topology that is not visible, and can extrude open borders rather than shell an entire detailed piece. Use as production-practice evidence, not a universal rule.

## P3 — controlled free reduction / seams

### PRIMARY/OFFICIAL

11. Blender 5.2 Manual — Decimate Modifier
https://docs.blender.org/manual/en/5.2/modeling/modifiers/generate/decimate.html
Evidence: Collapse mode supports a Vertex Group and Factor to control which parts of the mesh are decimated; also supports symmetry. Free and directly available in the current toolchain.

12. CGAL Surface_mesh_simplification user/reference manual
https://doc.cgal.org/latest/Surface_mesh_simplification/
Evidence: edge_is_constrained_map marks edges that cannot be collapsed; Constrained_placement can keep points on constrained edges from moving. Strong deterministic seam-lock candidate.

13. Simplygon Modular Seams
https://documentation.simplygon.com/SimplygonSDK_10.1.400.0/api/tools/modularseams.html
Evidence: shared border coordinates are analyzed once; the stored seam structure is reused so modular parts receive identical deterministic seam reduction and remain gapless. This is the architecture to emulate for free.

14. Simplygon GeometryData vertex weights
https://documentation.simplygon.com/api/concepts/geometrydata.html
Evidence: larger vertex weights preserve important features more strongly during reduction. Reference behavior for AETHERQOR's free equivalent.

Optional free alternatives to evaluate locally if Blender control is insufficient:
- CGAL constrained edge collapse (preferred deterministic hard constraint).
- PyMeshLab quadric edge collapse with preserve-boundary / boundary weight, useful for open boundaries but weaker for semantic modular seam constraints.
- libigl decimation in C++ with custom edge costs; Python default API may expose less control, so do not assume callbacks exist without testing.

## P4 — hair card layering / mobile transparency

### PRIMARY/OFFICIAL

15. Apple Developer — Rendering high-fidelity characters, hair cost section
https://developer.apple.com/documentation/realitykit/rendering-high-fidelity-characters
Evidence: hair cost is driven by card/strand overdraw, geometry and fragment lighting; minimize overlapping translucent layers; use an opaque base layer for scalp/inner hair mass so depth rejects layers behind it; prefer cards; fit card geometry closely to alpha silhouette.

16. Epic MetaHuman — Hair Card Generator in Dataflow
https://dev.epicgames.com/documentation/metahuman/hair-card-generator-in-dataflow-in-unreal-engine
Evidence: explicit production hierarchy:
- Core: base scalp coverage, wider cards, fewer triangles.
- Mid: primary shapes, increased clumping and more triangles.
- Top: most visible layer, highest triangle allocation and breakup.
- Flyaway: separate controlled loose hairs.
No universal percentage is published; AETHERQOR must calibrate at 1800 tri.

17. Unity 6 URP Lit/Simple Lit docs
https://docs.unity.cn/Manual/urp/lit-shader.html
Evidence: Transparent materials are blended; Alpha Clipping behaves as cutout; Render Face Both renders two-sided cards. Combine with mobile profiling rather than assuming desktop tutorials transfer directly.

### PRODUCTION BREAKDOWN

18. Existing local V5/V4 hair videos, already successfully processed:
- MxOfDMIl97U — card layering fundamentals.
- QLGLjeIrjWE — Blender card construction/curvature.
- Fp4g0GlNFu0 — row/layer construction.
- EmU62lWMhSU — Unity URP hair-card shader behavior.
- w8SjXHQ8ASY — production character hair / normals reference.
Reuse local evidence before redownloading.

## P5 — top-down class identity

### PRIMARY/OFFICIAL

19. Valve Dota 2 Character Art Guide
https://help.steampowered.com/en/faqs/view/0688-7692-4D5A-1935
Evidence: Dota's aesthetics are explicitly designed to keep every hero immediately and uniquely identifiable FROM ABOVE during gameplay. Silhouette must read at first glance, but pose, weapon, value gradient, value patterning, color/saturation and animation all contribute. Game view is prioritized over loadout.

20. Riot — Clarity in League
https://www.leagueoflegends.com/en-us/news/dev/clarity-in-league/
Evidence: silhouette is described as the most important champion-recognition channel; champions should have a defining primary characteristic. Riot also treats recognition as a multi-channel clarity budget involving animation, VFX/SFX/model changes.

21. Riot — Ask Riot: Let's Talk Clarity
https://www.leagueoflegends.com/en-gb/news/dev/ask-riot-let-s-talk-clarity/
Evidence: silhouette + readable VFX/SFX can preserve recognition even when animation/style changes; shape language/material/color proportions also matter.

22. Riot — VALORANT Shaders and Gameplay Clarity
https://www.riotgames.com/en/news/valorant-shaders-and-gameplay-clarity
Evidence: gameplay-important character readability can be preserved with deliberately simplified/scaled material responses; translucency sorting is treated as a serious performance/clarity problem.

No authoritative source found a universal IoU threshold for human class recognition. Treat any fixed 0.85 as an internal heuristic until calibrated against timed human recognition on AETHERQOR's actual seven classes.

## SOURCE USAGE RULE

Every final conclusion must label the evidence class. Extracted/reuploaded mesh counts may motivate a test range but may NEVER be written as 'the official budget of game X'. First-party architecture/process guidance has higher authority than a random model download or forum post.
