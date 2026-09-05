# AETHERQOR V7 — SOURCE REGISTRY

Purpose: authoritative/public evidence for class-closure architecture. Video timecodes are added after local frame processing. Do not treat third-party extracted competitor meshes as official production budgets.

## P1 — tier texturing and texture reuse

1. Adobe Substance 3D — Trim Sheets with Substance Painter
   https://www.adobe.com/learn/substance-3d-painter/web/trim-sheets-with-substance-painter
   Key fact: trim sheets texture many assets with one texture set and are explicitly presented as an efficient texture-memory workflow.

2. Adobe Substance 3D YouTube — Create Trim Sheets in Substance 3D Painter Part 1
   https://www.youtube.com/watch?v=dE4LWGMwypc

3. Polygon Academy — Planning & Creating Trim Sheets For Games
   https://www.youtube.com/watch?v=DipfrjCgYW8
   Focus: planning standardized layouts for maximum reuse.

4. Polygon Academy — Trim Sheets in Substance Painter: bake + smart materials
   https://www.youtube.com/watch?v=CarefswACgs

5. Polygon Academy — UV mapping trim sheets
   https://www.youtube.com/watch?v=VEHsZniXguY

6. GDC Vault / Insomniac Games — The Ultimate Trim: Texturing Techniques of Sunset Overdrive
   https://www.gdcvault.com/play/1022323/The-Ultimate-Trim-Texturing-Techniques
   Key fact: Insomniac standardized a reusable trim/normal layout specifically for production speed, memory usage and performance.

7. Microsoft / Simplygon — Automated Asset Optimization for Mobile Games
   https://developer.microsoft.com/en-us/games/articles/2025/10/automated-asset-optimization-for-mobile-games-with-simplygon/
   Key fact: material merging and geometry culling are explicit mobile optimization tools; recommends measurement on target device.

8. Simplygon — Material Merging
   https://simplygon.com/features/materialmerging
   Key fact: multiple materials can be consolidated into a single atlas; normal/color/opacity/vertex-color casters support LOD/material simplification.

9. Simplygon — Getting started with draw call optimization in Unity
   https://www.simplygon.com/blog/2bb52051-f380-47bb-b295-126ddc12306d
   Character example: body/eyes/clothes merged from three draw calls to one, with texture downscaling as a deliberate quality/performance tradeoff.

10. Android Developers — Optimize textures in games
    https://developer.android.com/games/optimize/textures
    Use for texture format/compression/memory decisions and screen-size relevance.

## P2 — small props, geometry vs bake, screen-space relevance

11. Android Developers — Optimize textures in games
    https://developer.android.com/games/optimize/textures
    Key principle: avoid detail that is imperceptible at target screen size.

12. ZBrushLIVE — baking only small detail into Normal/Displacement
    https://pixologic.com/zbrushlive/askzbrush-is-there-a-way-to-bake-out-the-small-details-when-creating-a-normal-displacement-map/
    Key fact: high-frequency sculptural detail can be selectively transferred into maps rather than geometry.

13. Marmoset — tangent-space bake workflow (video evidence in V3/V7 p2_small_detail_bake)
    https://www.youtube.com/watch?v=Yxr7RZgOB5M

14. AETHERQOR V3 AI-to-game UV/bake material
    https://www.youtube.com/watch?v=wCZcYKI-tGg

15. AETHERQOR V4 hard-surface game/PBR workflow
    https://www.youtube.com/watch?v=UEeDBndWwys

16. Simplygon documentation — screen-size based optimization example
    https://documentation.simplygon.com/SimplygonSDK_10.4.199.0/unity/quickstarts/csharpapi_simpleremeshingandbaking.html
    Key fact: optimization can target an on-screen size, e.g. 300 px, rather than a context-free triangle number.

17. Valve Dota 2 Item Model Requirements
    https://help.steampowered.com/en/faqs/view/5FB8-4078-8B2A-C52B
    Use as production evidence that close/loadout context and game-view context have different practical detail requirements.

## P3 — enhancement visualization without particle VFX

18. Unity URP Lit Shader manual
    https://docs.unity.cn/Manual/urp/lit-shader.html
    Key fact: emission map/color are built-in surface properties; emission can be driven without a separate renderer.

19. Unity Shader Graph URP Lit reference
    https://docs.unity3d.com/jp/current/Manual/urp/prebuilt-shader-graphs-urp-lit.html
    Key fact: emission is a material/shader input and can be parameterized.

20. Unity Scripting API — MaterialPropertyBlock
    https://docs.unity.cn/ScriptReference/MaterialPropertyBlock.html
    Key fact: per-renderer material values can vary while referencing the same material; changing render state is a different issue and must be profiled in the actual SRP setup.

21. Unity Scripting API — Renderer.GetPropertyBlock/SetPropertyBlock
    https://docs.unity.cn/6000.1/Documentation/ScriptReference/Renderer.GetPropertyBlock.html

22. Unity YouTube — Shader Graph colored glow
    https://www.youtube.com/watch?v=qTYOWRWuBQg

23. URP HDR Glow — Shader Graph
    https://www.youtube.com/watch?v=KLuyf9gqCik

24. Material emission fading/property-block example
    https://www.youtube.com/watch?v=A6mdaOySVQM

## P4 — materials, meshes and draw calls

25. Unity 6 manual — Optimizing draw calls
    https://docs.unity.cn/6000.0/Documentation/Manual/reduce-draw-calls-landing.html
    Key fact: combining meshes, SRP Batcher and instancing solve different parts of render cost.

26. Unity manual — Introduction to draw-call optimization
    https://docs.unity.cn/Manual/optimizing-draw-calls.html
    Key fact: render-state changes, especially material changes, are expensive; SRP Batcher reduces CPU setup cost but does not magically turn many renderers/material passes into one draw.

27. Unity Learn — Optimizing Graphics in Unity
    https://learn.unity.com/tutorial/optimizing-graphics-in-unity
    Key fact: on mobile, draw-call optimization is particularly important; using fewer textures/materials improves batching opportunities.

28. Simplygon — Unity material merging character example
    https://www.simplygon.com/blog/2bb52051-f380-47bb-b295-126ddc12306d

29. Simplygon YouTube — Unity Aggregation with Material Baking + Reduction
    https://www.youtube.com/watch?v=xGM1trJDHz8
    Example reports 11 meshes / 4 materials / 10220 tri -> 1 mesh / 1 material / 4164 tri for mobile optimization. Treat as tutorial example, not universal target.

30. Unity Performance Tips: Draw Calls
    https://www.youtube.com/watch?v=IrYPkSIvpIw

31. Unity Optimization — reducing 3D object draw calls
    https://www.youtube.com/watch?v=vU3au56UV_E

32. Simplygon Modular Seams video used in V5/V6/V7
    https://www.youtube.com/watch?v=eqyrdKu_yKk

## P5 — class recognition and top-down clarity

33. Valve — Dota 2 Workshop Character Art Guide
    https://help.steampowered.com/en/faqs/view/0688-7692-4D5A-1935
    Strong production evidence: heroes are designed to be immediately identifiable from above; silhouette, pose, weapon, value gradient, value patterning, color/saturation, directionality and game-view evaluation all contribute.

34. Riot Games — Clarity in League
    https://www.leagueoflegends.com/en-us/news/dev/clarity-in-league/
    Key production principle: silhouette is central, but primary characteristic, animation, VFX and other cues contribute to recognition.

35. Riot Games — VALORANT Shaders and Gameplay Clarity
    https://www.riotgames.com/en/news/valorant-shaders-and-gameplay-clarity
    Key fact: detail breaks down with distance; shader/value treatment is deliberately designed around readability.

36. Metrics Reloaded — IoU limitations
    https://metricsreloaded.dkfz.de/metric_days/intersection_over_union/
    Key fact: IoU does not encode boundary distance, local contour differences or perceptual identity.

37. OpenCV — Hausdorff Distance Extractor
    https://docs.opencv.org/4.x/d0/de1/classcv_1_1HausdorffDistanceExtractor.html

38. Riot character-art / silhouette video used in prior AETHERQOR research
    https://www.youtube.com/watch?v=PfpE5dNTWeI

39. NGDC — Game Art Bible, parts 1/2
    https://www.youtube.com/watch?v=vuXxfnCM56A
    https://www.youtube.com/watch?v=YaDIbe2GeCY

40. Valve/Dota related visual reference video
    https://www.youtube.com/watch?v=nk2wViKSh_M

## AETHERQOR local evidence to reuse

- V3: D:\AetherqorFoundry\research\blockers_v3\CLAUDE_VIDEO_REPORT_33904162671
- V4: D:\AetherqorFoundry\research\blockers_v4_night\ULTRA_RESEARCH_2026-09-04_NIGHT
- V5: D:\AetherqorFoundry\research\blockers_v5_architecture\ULTRA_RESEARCH_2026-09-05
- V6: D:\AetherqorFoundry\research\blockers_v6_urgent\ULTRA_RESEARCH_2026-09-05_URGENT

Do not redownload an older video if the exact source already exists locally and the evidence set is complete; V7 should still create its own local set when needed for its catalog and record source provenance explicitly.
