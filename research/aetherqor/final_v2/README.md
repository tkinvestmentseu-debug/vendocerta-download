# AETHERQOR VIDEO-GROUNDED CLOSURE PACK V2

Data: 2026-09-04

## Status źródeł

10/10 tutoriali zostało pobranych i przetworzonych przez self-hosted runner. Dla każdego źródła powstały metadata/transcript, klatki 1 fps i plansze 3x3; dla rozdziałów oznaczonych jako krytyczne także materiał 4 fps. Oznacza to, że ten pack zastępuje wcześniejszy appendix, w którym video nie było bezpośrednio dostępne.

## Pliki

1. `AETHERQOR_MEGA_PROMPT_VIDEO_GROUNDED_V2.md` — główna dyrektywa wykonawcza dla Claude.
2. `AETHERQOR_13_LEKCJI_VIDEO_GROUNDED_V2.md` — 13 decyzji produkcyjnych, każda z gate PASS/FAIL.
3. `AETHERQOR_10_TUTORIALS_RESEARCH_NOTES_V2.md` — notatki źródłowe z 10 tutoriali z rozdzieleniem VIDEO / OFFICIAL / AETHERQOR INFERENCE.
4. `AETHERQOR_SOURCE_MATRIX_VIDEO_GROUNDED_V2.csv` — matryca filmów i dokumentacji oficjalnej.
5. `AETHERQOR_AUTONOMOUS_CLOSURE_PLAN_V2.md` — 42 zadania w kolejności zależnościowej.

## Zasada dowodowa

Nie przypisuj tutorialowi wniosku, którego nie pokazuje ani nie mówi. Shader/render desktop lub Unreal/Cycles nie jest automatycznie przepisem dla Unity 6 URP mobile. Źródła wideo dają techniki konstrukcji, kolejność operacji i diagnostykę. Decyzje mobile muszą przejść osobny benchmark na docelowym urządzeniu.

## Najważniejsze nowe rozstrzygnięcia po analizie video

- Modular armor tutorial bezpośrednio pokazuje, że naiwne rozbijanie gotowej zbroi na osobne części powoduje szczeliny i widoczną skórę. Najbardziej powtarzalna metoda opiera się na odpowiadających granicach ciała i pancerza oraz ukrywaniu regionu ciała pod aktywnym gearem.
- Hair tutorials pokazują warstwową konstrukcję kart, osobne topologie dla bangs/bun i konieczność redukcji rozdzielczości krzywych przed Curve→Mesh.
- Character/retopo tutorials pokazują, że design i silhouette muszą być rozstrzygnięte przed retopologią, a retopo ma zaczynać się od prostych, funkcjonalnych loopów i dopiero później dostawać rozdzielczość.
- Armor/clothing tutorials powtarzają body-correlated construction: element przechodzący przez wiele stawów musi być silnie zgodny z deformującą powierzchnią ciała. W AETHERQOR oznacza to removable shell wyprowadzony z body landmarks/surface, nie trwałe scalenie z ciałem.
- Eye tutorial daje użyteczny podział cornea/sclera/iris i porządek eksportu, ale wartości materiałów Unreal nie są przenoszone do URP.
- VFX Graph tutorial daje mechanikę Spawn/Initialize/Update/Output, capacity, bounds, mesh/skinned-mesh sampling, collision, events i strips. Oficjalna dokumentacja Unity 6 nadal opisuje pełne wsparcie URP/mobile VFX Graph jako rozwijane, więc produkcyjny fallback mobile jest obowiązkowy.
