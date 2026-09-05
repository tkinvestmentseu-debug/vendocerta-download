# AETHERQOR V8 — OTWARTE PROBLEMY DO ROZSTRZYGNIĘCIA

Stan: 2026-09-05. To nie jest backlog wszystkiego, tylko pytania, dla których nadal brakuje sprawdzonej metody, kosztu albo decyzji artystycznej. Nie powtarzać metod już obalonych pomiarem.

## A1. Fasetowanie torsów — „tłuczone szkło” na wszystkich 14

Objaw: kirys przy barkach i podołku wygląda jak poziome półki/plastry Z. Przy 300 px widoczne wyraźnie, przy 90 px jako szum obrysu.

Obalone: flat shading; usunięcie wewnętrznej wyspy Solidify; Decimate Planar (kirys SI 3,16% -> 5,78%); hipoteza 278 reversed faces; kolejność modyfikatorów (decymacja przed Solidify już wdrożona).

Zmierzona sygnatura przyczyny: loft „convex envelope per Z slice”. Skrzydełka/pióra barkowe donora zmieniają szerokość obwiedni z plastra na plaster, a A-pose potrafi przeciągnąć bryłę aż w stronę przedramion.

Alpha Wrap poprawił donor fidelity kirysa 0,761 -> 0,950 IoU, ale nie zmierzono, czy tarasy znikają, czy wrap wiernie utrwala podarte krawędzie donora.

Rozstrzygnąć: raw donor Alpha Wrap vs torso-cropped donor Alpha Wrap; zmierzyć wysokość uskoku między sąsiednimi pasmami Z, silhouette jitter, donor P95/P99, zachowanie prawdziwych krawędzi. Jeśli trzeba, zbadać lokalne feature-preserving fairing/smoothing po wrapie, ale tylko z twardym limitem odchylenia od donora.

## A2. Mozaika „pęknięć” — 461 wysp UV

`ember_chest_f` ma 461 UV islands. Dylatacja podniosła coverage 88,1% -> 99,0–99,9%, ale ciemne obwódki zostały. Random-color UV islands pokrywają się 1:1 z mozaiką. Obecny cavity liczy Gaussian blur w 2D texture space, więc każdy seam staje się fałszywą krawędzią.

Dodatkowo `_cavity.png` nie jest używany bezpośrednio przez runtime Unity; wpływ idzie przez `MODS.B`, a jego realny mix w Unity nie został zmierzony.

Rozstrzygnąć w tej kolejności: (1) prawdziwy geometry-space curvature/concavity bake zamiast 2D Gaussian cavity; (2) porównać Blender Cycles Pointiness, Marmoset curvature/concavity i ewentualnie Substance curvature; (3) zmierzyć seam artifact w Unity; (4) dopiero jeśli nadal potrzebne, eksperyment z redukcją chart count/nowym UV. Nie rozwalać UV tylko dlatego, że liczba 461 wygląda źle.

## A3. Buty czytają się jak kapcie — 14/14

Zaokrąglona bryła bez czytelnej podeszwy, noska i pięty. Przy 300 px widoczne, przy 90 px ledwo.

Brak diagnozy. Historycznie 78 tri czytało się jak bosa stopa. Wierzch buta to otwarta skorupa z 176 boundary edges. Lewy i prawy but mogą mieć skrajnie różny pipeline historycznie (jeden przebudowany do 144 vertices, drugi mógł pozostać 24 444 przez próg 0,01).

Rozstrzygnąć donor vs pre-decimation vs post-decimation vs gameplay LOD w 90/150/300 px. Zmierzyć sole thickness, toe projection, heel height, ankle break, silhouette delta. Werdykt musi wskazać: DONOR_AUTHORING / RECONSTRUCTION / ALLOCATION_DECIMATION / LOD.

## A4. Fasetowanie włosów — dotychczasowy pomiar niewiarygodny

Pięć prób geometrii wykonano, ale pomiar zamykający dług miał dwie niekontrolowane zmienne: render head ~200 px / char ~1400 px przy celu char 90–300 px (head ok. 13–44 px), oraz brak właściwego hair shadera — isotropic Principled BSDF roughness 0,40 powodował jasne specular facets na kartach. Defekt nigdy nie został potwierdzony w Unity; 60+ renderów było w Cycles.

Najpierw poprawić pomiar, nie geometrię: downscale istniejących proofów do realnej skali; następnie Unity 6 URP A/B na tej samej geometrii: current material vs anisotropic hair material, dokładnie 90/150/300 px char, ruch kamery i kilka kierunków światła. Dopiero potem decydować, czy istnieje problem geometryczny.

## A5. Ember_M pauldron_L — anomalne źródło

Jeden `pauldron_L` ma source 15 208 tri przy ok. 1052 dla tego slotu w pozostałych kompletach. Dostaje 200 tri, czyli ok. 76x compression. Objaw: postrzępione kolce.

Rozstrzygnąć provenance: generator error, wrong donor, kilka obiektów zrośniętych, czy rzeczywiście bardziej złożony poprawny donor. Dodać automatyczny source sanity gate przed alokatorem: ratio do mediany slotu, connected components, bbox/anatomical overlap, asset path/hash/provenance.

# B. KIERUNEK ZNAMY, BRAKUJE METODY/KOSZTU

## B1. Ujednolicenie M i F

Zmierzono m.in.: chest Warden M=2600 F=5806; Veilblade M=2599 F=5806; Druid M=2600 F=1499; Frost M=1500 F=2600. `coif` = 4648 dla każdego M i 9968 dla każdego F, czyli wspólny asset per płeć, bez class identity. Warden_F, Storm_F, Veilblade_F, Ember_F czytają się prawie jak jedna postać w różnych ciemnych paletach.

Zbadać trzy produkcyjne drogi: (A) refit class donor M -> body F przy zachowaniu macroform; (B) istniejąca forma F + transfer class pattern/emission; (C) sex-specific reauthoring. Nie podejmować decyzji artystycznej za właściciela, ale zrobić dwa porównywalne proofy: SAME_IDENTITY_REFIT i SEX_SPECIFIC_FORM oraz metryki class read, donor fidelity, collision, deformation.

## B2. Materiały giną w FBX round-tripie

Render QA został zamaskowany flagą `--warstwy-ciemne`, ale eksport/import nadal gubi materiały także po stronie Unity: underlayer, eyes, skin, `AQ_CATCH_L/R`, puste material slots na `bracer_L/R` w 9 kompletach.

Rozstrzygnąć exporter-side vs deterministic Unity importer remap. Unity material assets powinny być kandydatem na source of truth. Zbadać ModelImporter material remapping, AssetPostprocessor, `SearchAndRemapMaterials`, `AssetImporter.AddRemap`, stable semantic material names/IDs. Zbudować material manifest i regression test na wszystkich 14.

## B3. Scalanie SkinnedMeshRenderer — 43 -> docelowo mała liczba

Stan: 32 materials, 53 meshes, 43 SMR + 10 MR. Poprzednie kontrakty celowały w <=4 materials, <=6 meshes, ale nowy próg ma wynikać z pomiaru, nie dogmatu.

Ryzyko: bone index remap, bindposes, weights, blendshapes, submeshes, `.001` silent suffix, skinning niewidoczny w bind pose. Projekt już raz stracił skinning przez `use_selection` bez armatury.

Rozstrzygnąć przez pilot na jednej postaci. Zbudować stable skeleton map, remap bone indices, preserve bindposes/weights/blendshapes/material families. Walidować w animacji na 21 clipach i skrajnych pozach, nie tylko bind pose. Porównać render/vertex deformation przed-po. Przejrzeć UMA i inne open-source combiners jako reference, z pełnym license gate.

## B4. Kotwica 40–70% wysokości

Nowe odniesienie pomiarowe z Garena: sword ~68% height, cape ~54%; wcześniejsze 10–15% było wielokrotnie mniejsze. Nie przenosić jednak 68% jako uniwersalnego progu. Nasze anchors to często shoulder/back pieces, więc taki wymiar może zabić animację/kolizję.

Znany problem: overlap pauldronu spada do 0,4% w run, bo anchor jest statyczny na Spine2, a shoulder porusza się z inną kością.

Rozstrzygnąć w prawdziwej gameplay camera: radial excursion, outer contour contribution, recognition, collision over full animation, właściwy bone ownership. Anchor ma być primary identity cue, nie spełniać arbitralnego procentu.

## B5. Brak slotu weapon

`SLOT_EKWIPUNKU` nie ma `weapon`, mimo że Bible ma niewykorzystany budżet weapon/offhand 1400+1200 i źródła branżowe traktują broń jako silny class identity carrier.

Rozstrzygnąć techniczną architekturę: dodać first-class weapon/offhand slot, gameplay/display LOD, bone attachment, budget, material family, equip semantics i QA. Osobno właściciel musi zdecydować zakres produkcyjny: 7 broni od zera vs adaptacja istniejących klasowych weapon donors.

## B6. Frost shield wisi obok postaci

Shield: 0,0% collision with gear i 0,0% with body, vertical span 1014 mm na char 1,88 m. Wygląda jak prostokąt doczepiony z tyłu.

Zdiagnozować plik: parent bone, local/world transform, closest surface distance, intended attachment points, animation trajectory. Jeśli to worn shield/backpiece, zdefiniować minimalny attachment/contact semantic i zmierzyć przez idle/run/combat.

# C. WYMAGAJĄ DECYZJI WŁAŚCICIELA LUB LUDZI

## C1. Human calibration class recognition

IoU 0,85 nie ma branżowego potwierdzenia. Zbudować pełny 7AFC: stimulus 500/750/1000 ms; 64/90/128/150/220 px; silhouette, +anchor, color/material, motion. Tooling i trial set mają być gotowe; finalne thresholdy mogą mieć status BLOCKED_EXTERNAL_HUMAN_CALIBRATION do czasu odpowiedzi ludzi.

## C2. Female silhouette policy

Decyzja artystyczna: female ma być wariantem tego samego class design czy osobnym projektem. Technicznie przygotować dwa proofy i policzyć konsekwencje dla class read, donor fidelity, kosztu produkcji, reuse i deformacji. Nie zgadywać decyzji.

## C3. Ile rang ma wyglądać inaczej

Kontrakt: 7 rang w 3 pasmach. dE przy progu 25 dał 2 stany. V7 dał 3–4 bands w nocy i 1 w dzień, bo bloom jest globalny/progowy. To konflikt projektowy.

Shader/data architecture ma obsługiwać config-driven bands bez duplikacji materiałów. Zbudować test w day/night/no-bloom/controlled exposure i dostarczyć właścicielowi zestaw porównawczy 2 vs 3 vs 4 bands. Exact 7 gameplay ranks pozostaje niezależne od liczby czytelnych visual bands.

# ZASADY V8

Nie powtarzać zamkniętych tematów tylko dlatego, że pojawiają się w starym tutorialu. Alpha Wrap jako metoda soup jest zamknięty i działa; V8 może go użyć jako narzędzia w eksperymencie A1/A3/A5, ale nie robi kolejnego researchu czy działa. VDB, QRemeshify, Quadriflow, generalny ZRemesher/QuadRemesher jako soup solver, generic MPB-vs-SRP, VFX Graph, retarget, URP map packing są zamknięte.

Każdy problem musi skończyć się jednym z: IMPLEMENTED_PASS, IMPLEMENTED_FAIL, RESEARCH_CONFIRMED_NEEDS_ENGINEERING, BLOCKED_EXTERNAL. Nie używać RESEARCH_DONE.
