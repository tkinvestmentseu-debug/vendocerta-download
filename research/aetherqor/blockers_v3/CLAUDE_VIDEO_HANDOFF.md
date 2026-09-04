# AETHERQOR Blockers V3 — Claude Code Video Research Handoff

## Cel

Ten pakiet jest wejściem dla Claude Code do zamknięcia siedmiu blockerów AETHERQOR na podstawie realnych materiałów wideo, transkrypcji, klatek 1 fps, plansz 3x3 i klatek wysokiej częstotliwości 4 fps.

## Jak czytać pakiet

1. Otwórz `FINAL_STATUS.md` i sprawdź, czy wszystkie 11 pozycji mają komplet `meta + sheets + frames`; brak kompletu traktuj jako blocker danych.
2. Dla każdego filmu najpierw przeczytaj `manifest.json`, `transcript.txt` lub `TRANSCRIPT_MISSING.txt`, `frame_index.csv`, `sheet_index.csv` i `high_detail_index.csv`.
3. Obejrzyj wszystkie plansze 3x3 po kolei. Każda plansza odpowiada dziewięciu kolejnym sekundom materiału.
4. Gdy plansza pokazuje istotny detal techniczny, otwórz odpowiadające jej surowe klatki 1 fps. Dla segmentów oznaczonych jako krytyczne użyj klatek 4 fps.
5. Nie opieraj wniosków wyłącznie na transkrypcji. Techniki modelowania, topology, UV, bake, hair cards i deformation muszą być potwierdzane obrazem.
6. Każdy wniosek techniczny zapisuj z: slug filmu, timecode, nazwą klatki/planszy, zastosowaniem do konkretnego blockera i krótkim uzasadnieniem.

## Mapowanie filmów na blockery

- `b1_zbrush_game_res`, `b1_zremesher_game_ready`, `b1_blender_geometry_repair` -> B1 broken armor shells / clean plate reconstruction.
- `b3_riot_character_art` -> B3 class silhouette, readability, proportions.
- `b4_game_asset_optimization` -> B4 mobile/game asset optimization, LOD decisions.
- `b5_armor_modeling_gloves`, `b5_maya_gloves` -> B5 glove/gauntlet construction and topology.
- `b6_ai_to_game_uv_bake`, `b6_marmoset_bakes` -> B6 low-poly UV ownership, cage and high-to-low baking.
- `b7_hair_cards_quick`, `b7_long_hair_cards` -> B7 hair cards, density, silhouette and game-ready construction.

## Twardy kontrakt wykonawczy

Dla każdego blockera wykonaj sekwencję:

`SOURCE READ -> VIDEO FRAME REVIEW -> CODE -> REAL EXISTING AETHERQOR ASSET -> AUTOMATED QA -> PROOF RENDER -> METRICS -> IMPLEMENTED_PASS / IMPLEMENTED_FAIL -> CHECKPOINT COMMIT`

Nie kończ na `RESEARCH_DONE`. Wynik ma być wdrożeniem na realnym assetcie AETHERQOR albo `IMPLEMENTED_FAIL` z konkretną przyczyną techniczną i dowodem.

## Priorytet

1. Broken armor shells
2. Rigid plate skinning
3. Class identity / silhouette
4. Triangle budget benchmark
5. Gloves
6. UV ownership / bake
7. Hair cards

## Bezpieczny tryb

- Nie nadpisuj surowych plików Meshy.
- Pracuj na kopiach/stagingu.
- Przed i po każdej zmianie zapisuj metryki i render porównawczy.
- Nie wracaj jako domyślne rozwiązanie do global Boolean Union dla open shell soup, default voxel remesh cienkich open shells, Quadriflow, QRemeshify na problematycznych skorupach, global body-distance push ani Laplacian smoothing płyt.

## Wymagany raport końcowy Claude Code

Dla B1-B7 podaj:
- źródła i timecode,
- czego nauczył materiał wideo,
- dokładne zmiany w kodzie/pipeline,
- asset pilota,
- before/after metrics,
- proof render path,
- testy automatyczne,
- status `IMPLEMENTED_PASS` albo `IMPLEMENTED_FAIL`,
- commit SHA.

Na końcu utwórz jedną tabelę `BLOCKER | VIDEO EVIDENCE | IMPLEMENTATION | QA | STATUS | COMMIT`.
