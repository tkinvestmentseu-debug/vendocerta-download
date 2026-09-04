# AETHERQOR — AUTONOMOUS CLOSURE PLAN V2

Cel: doprowadzić 13 problemów do mierzalnego PASS bez powtarzania obalonych eksperymentów.

## 42 zadania w kolejności zależnościowej

### P0 — snapshot i QA
1. Zrób immutable input snapshot.
2. Zapisz SHA256 assetów, Blender/Unity/MPFB versions, git SHA, Meshy IDs.
3. Dodaj kontrakt `AETHERQOR_JOB_OK=<uuid>` do wszystkich blender headless jobs i grep `Traceback|ERROR|FATAL`.
4. Zbuduj centralny JSON schema dla geometry/render/Unity gates.
5. Zablokuj wspólny rig kamery/światła/exposure dla BEFORE/AFTER.

### P1 — nowa kobieta
6. Zrób dokładny M vs F pipeline diff.
7. Dodaj topology probe po każdym etapie pipeline.
8. Znajdź pierwszy krok, w którym F przechodzi z 1 connected component do >1.
9. Odtwórz F z rzeczywistego preset/JSON/MHM na hm08.
10. Zbuduj clean export staging według zainstalowanego MPFB `10_complete_character_export_fbx.py`.
11. Geometry gate: 1 shell, 0 boundary, 0 nonmanifold, no duplicates.
12. Weight transfer A/B: Nearest Face Interpolated vs Projected Face Interpolated.
13. Zrób deform suite: idle/walk/run/crouch/jump/shoulder/knee/hip/torso twist.
14. UV gate: native hm08 first, transfer only if required.
15. 5 shape-key gate: recreate targets first, UV/barycentric only fallback.

### P11 — skeleton
16. Bone inventory 55 vs 72.
17. Klasyfikacja dodatkowych kości na deform/twist/face/helper/orphan.
18. Shared Humanoid controller test z 14 clips.
19. Wybór canonical deform skeleton po pomiarze deformacji i gear fit.

### P2/P3 — face/eyes
20. Wpięcie `domaluj_twarz.py` w chain.
21. BaseColor/Roughness/DetailNormal procedural bake.
22. 1024 vs 2048 face map experiment.
23. Eye A/B/C/D isolation: sclera+iris / +cornea / +occlusion / +catchlight.
24. EYE_LITE vs EYE_MID Unity mobile profile.

### P4/P5 — hair/underwear
25. Hair triangle decomposition per visual function.
26. Adaptive curve resolution i Curve→Mesh dopiero po redukcji.
27. Real ponytail/bun/braid topology.
28. Hair keep-out around iris/pupil.
29. Female bra landmark solver.
30. Cups/gore/underband/straps surface construction.
31. Underwear weight transfer + arms-up/twist deformation tests.

### P6/P7/P8 — armor topology/material/emission
32. Geometry classifier SOLID/THIN_SHELL/BRANCHED_THIN/DETAIL_DISCARDABLE.
33. THIN_SHELL planar/feature-preserving branch zamiast voxel-first.
34. 8-view LOD silhouette gate.
35. Pełny rebake po zmianie topology.
36. Material-zone mask generator PLATE/TRIM/LINING/STRAPS/ACCENT.
37. Offline edge-wear/curvature bake.
38. Groove/gap/crystal authoring branch + bloom-off gate.

### P9/P12/P10/P13
39. 14 HERO black-silhouette matrix i kalibracja `AETHERQOR_SILHOUETTE_GATE_V1`.
40. Approved HERO staging + `AetherqorHeroAssetPostprocessor.cs` + stale/external hard fail.
41. 7 `SkillDefinition` + canonical sockets + pooling + Particle/Shader mobile fallback + opcjonalny VFX Graph benchmark.
42. Art cleanup 6 items + 14/14 regression + FINAL_HANDOFF.

## Reguła autonomii

Po PASS automatycznie przejdź do następnego kroku. Po FAIL rollback, zapisz próbę do `REJECTED_APPROACHES.md` i wybierz następną hipotezę wynikającą z danych. Nie zatrzymuj się po samym researchu.

Zatrzymaj się wyłącznie przy: ryzyku nieodwracalnego nadpisania źródła, zakupie/płatności, braku credential/data, nierozstrzygalnej decyzji artystycznej nieobjętej SPEC albo realnym `BLOCKED_EXTERNAL`.
