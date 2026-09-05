# AETHERQOR V5 — SOURCE REGISTRY

Sources are ranked by authority. Claude must distinguish OFFICIAL / PRIMARY, PRODUCTION BREAKDOWN, EXTRACTED-GAME-MODEL EVIDENCE, and COMMUNITY/SECONDARY. Do not turn a weak source into a hard budget rule.

## P1 — character triangle architecture / mobile LOD

### OFFICIAL / PRIMARY

1. Microsoft / Simplygon — Automated Asset Optimization for Mobile Games with Simplygon
https://developer.microsoft.com/en-us/games/articles/2025/10/automated-asset-optimization-for-mobile-games-with-simplygon/
Key evidence to verify: mobile characters often use multiple quality versions; a higher-detail character can be used when the character is the focus and a lower-resolution version in gameplay; judge on actual mobile device and actual screen context.

2. Microsoft / Simplygon — Four Fundamental Simplygon Tools for Automated Character Optimization
https://developer.microsoft.com/en-us/games/articles/2025/09/four-fundamental-simplygon-tools-for-automated-character-optimization/
Key evidence: skinning-aware triangle reducer; extra geometry can be allocated in deformation zones; vertex weighting allows artist-preserved regions; material merging is part of character optimization architecture.

3. Microsoft / Simplygon — Three Advanced Tools for Automated Character LOD
https://developer.microsoft.com/en-us/games/articles/2025/11/simplygon-tools-automated-character-lod-pipeline/
Key evidence: Quad Reducer for LOD0/platform variants; modular seams for modular characters; per-part reduction can preserve deterministic shared boundaries.

4. Simplygon — Quad Reducer
https://www.simplygon.com/features/quadreducer
Key evidence: preserves topology/quad strips, open edges, UVs, normals; targets by ratio/count/max deviation/screen size.

5. Simplygon — Vertex Weights
https://simplygon.com/features/vertexweighting
Key evidence: per-vertex importance can drive where triangles are retained.

6. Simplygon — Modular Seams
https://simplygon.com/features/modularseams
Key evidence: interchangeable character parts can be optimized separately while preserving exact shared borders.

7. Unity 6 — Set culling mode in a shader
https://docs.unity.cn/6000.0/Documentation/Manual/set-culling-mode.html
Key evidence: back-face culling is default because it avoids GPU work on faces not visible in the final image; Cull Off should be used only when necessary. This is directly relevant to one-sided shells versus global two-sided rendering.

8. Unity — Optimize mobile game performance: graphics and assets
https://unity.com/blog/games/optimize-your-mobile-game-performance-expert-tips-on-graphics-and-assets
Key evidence: mobile is highly sensitive to overdraw/alpha blending; judge skinned mesh and rendering cost in engine, not only polygon count.

9. Unity URP performance documentation
https://docs.unity.cn/6000.0/Documentation/Manual/urp/understand-performance.html
https://docs.unity.cn/Manual/urp/configure-for-better-performance.html
Key evidence: triangle count is only one part of cost; draw calls, passes, pixel cost, transparency and bandwidth are critical on mobile.

### EXTRACTED-GAME-MODEL / PROVENANCE MUST BE CHECKED

These are useful as evidence that 14k may be far below some shipped/high-detail character assets, but they are NOT official studio budgets and may include extraction/re-upload transformations. Claude must inspect whether weapon/hair/accessories are included and label confidence.

10. Wuthering Waves — Lingyang model page: 38.3k triangles
https://sketchfab.com/3d-models/lingyang-wuthering-waves-1624c5b578e04eaeb657f522262490b8

11. Wuthering Waves — Encore model page: 36.1k triangles
https://sketchfab.com/3d-models/encorenew1-1-wuthering-waves-7bfa0d20d0bd4422a35d56cef71e9de6

12. Wuthering Waves — Chixia model page: 30.1k triangles
https://sketchfab.com/3d-models/chixia1-1-wuthering-waves-7d2dd67016924805951e9e9eef543761

13. Wuthering Waves — Carlotta page: 91.3k triangles
https://sketchfab.com/3d-models/carlotta-montelli-wuthering-waves-a0798264c0c3458bbe8960cbcd34a82c

14. Wuthering Waves — Lynae page: 103.5k triangles
https://sketchfab.com/3d-models/lynae-from-wuthering-waves-e59593637d424294a7361d428d9147bc

15. Genshin — Arlecchino page: 30.8k triangles
https://sketchfab.com/3d-models/genshin-impact-arlecchino-69cb7d3a1b8a4fb48b0125229b952916

16. Genshin — Skirk page: 28.9k triangles
https://sketchfab.com/3d-models/genshin-impact-skirk-e56bdb29d65c4edb82cd853b7312cce4

17. Diablo-style community game character page: 35.2k triangles
https://sketchfab.com/3d-models/diablo-immortal-gaming-character-e497960651574cf08993ac5fefef1e7e
Important: community-created, not proof of Blizzard production budget. Use only as weak context.

## P2 — shell soup reconstruction

18. CGAL 6.2 Alpha_wrap_3 manual
https://doc.cgal.org/latest/Alpha_wrap_3/index.html
Primary evidence: triangle soup is supported input; alpha controls cavity/feature scale; offset controls distance/tightness.

19. CGAL Alpha_wrap_3 free function docs
https://doc.cgal.org/latest/Alpha_wrap_3/group__AW3__free__functions__grp.html
Primary guarantee to verify: watertight, 2-manifold, intersection-free output strictly containing input triangle soup.

20. CGAL 3D Alpha Wrapping announcement
https://www.cgal.org/2022/05/18/alpha_wrap/
Primary evidence: designed to be robust to duplicates, degeneracies, holes/gaps, self-intersections, non-manifold features and inconsistent orientation.

21. SideFX — VDB From Polygons
https://www.sidefx.com/docs/houdini/nodes/sop/vdbfrompolygons.html
Primary evidence: unsigned distance fields do not require airtight input; Preserve Holes uses generalized winding number; self-intersecting/kit-bashed input can be rasterized, but internal-hole behavior is a tradeoff.

## P3 — decimation of modular character / protected edges

22. Simplygon — Modular Seams documentation
https://documentation.simplygon.com/SimplygonSDK_10.1.400.0/api/tools/modularseams.html
Primary evidence: per-part optimization with deterministic reduction of shared seam borders.

23. Simplygon — Triangle Reducer
https://simplygon.com/features/trianglereducer
Primary evidence: character LOD chains, geometry importance, skinning preservation and modular seams are explicit production features.

24. Microsoft / Simplygon — Optimize 3D Models for Strategy Games
https://developer.microsoft.com/en-us/games/articles/2026/05/optimize-3d-models-for-strategy-games-with-simplygon/
Primary evidence: reduction should be judged from actual top-down camera; very low targets can require remeshed proxies; screen/camera context matters more than arbitrary global ratio.

## P4 — hair-card scalp coverage and occlusion

25. Jennifer Bloemeke — Research: Realistic Real Time Hair
https://jennyb.artstation.com/projects/4b8vQ2
Production breakdown evidence: opaque base layer to cover scalp, breakup layer with more transparent cards, then flyaways/transitional hair.

26. The Rookies — Game Art by Jennifer Bloemeke
https://www.therookies.co/entries/3132
Same layered hair-card workflow with visual breakdown.

27. Sushan Manandhar — Hair Cards for Game Characters tutorial
https://www.artstation.com/artwork/bKKAYn
Production-style tutorial learned from Vertex School / Jansen Turk; explicit row layering and hair chunks.

28. Unity URP experimental hair-card shader
https://github.com/itsFulcrum/Unity-URP-Hair-Shader
Useful implementation reference, but explicitly experimental and not physically accurate. Do not treat as authoritative performance guidance.

29. Unity mobile optimization article
https://unity.com/blog/games/optimize-your-mobile-game-performance-expert-tips-on-graphics-and-assets
Primary engine guidance: minimize overdraw and alpha blending on mobile.

## P5 — gameplay-camera silhouette/readability

30. Microsoft / Simplygon strategy-game optimization
https://developer.microsoft.com/en-us/games/articles/2026/05/optimize-3d-models-for-strategy-games-with-simplygon/
Primary optimization evidence: top-down camera should directly drive geometry decisions and validation.

31. Existing AETHERQOR V3 Riot character-art video evidence
Local path: D:\AetherqorFoundry\research\blockers_v3\CLAUDE_VIDEO_REPORT_33904162671
Slug: b3_riot_character_art
Do not redownload; reuse existing 1fps/3x3 evidence.

32. Existing AETHERQOR V4 top-down / silhouette contracts and proof
Search project for KONTRAKT_SYLWETEK.md and existing masks/results.

33. Inviox silhouette-recognition article
https://www.invioxstudios.com/blog/how-long-it-takes-for-players-to-recognize-a-character-silhouette
Secondary source only. It claims recognition tests and context-aware testing; verify methodology before trusting numerical claims.

## Required source discipline

For every final claim use one of:
- PROVEN_PRIMARY
- PROVEN_LOCAL_MEASUREMENT
- PRODUCTION_BREAKDOWN
- EXTRACTED_MODEL_WEAK_EVIDENCE
- COMMUNITY_SECONDARY
- HYPOTHESIS

Never use extracted Sketchfab model counts as if Pearl Abyss/Kuro/HoYoverse officially published those budgets.
