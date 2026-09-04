# AETHERQOR — 10 TUTORIALI: RESEARCH NOTES V2

Data: 2026-09-04
Tryb: VIDEO-GROUNDED

## Zasada

- **VIDEO** = obserwacja wsparta transkrypcją i/lub klatkami/planszami z danego filmu.
- **OFFICIAL** = informacja z dokumentacji producenta.
- **AETHERQOR INFERENCE** = decyzja projektowa wynikająca z połączenia źródła ze stanem AETHERQOR.
- Jeśli źródło desktop/offline używa Cycles, Unreal albo rozwiązania nieprzenośnego do URP mobile, bierzemy logikę konstrukcji, nie kopiujemy shaderu 1:1.

---

## V01 — Game-Ready Hair Cards in Blender
URL: https://www.youtube.com/watch?v=3bw2SnKQhwA
Czas: 22:18
Rozdziały: 01:10 base hair card; 07:10 textures; 13:00 second layer; 16:13 root transition; 18:30 bangs; 19:35 bun; 21:06 curves to mesh.

### VIDEO
- Fryzurę rozbija się najpierw na grupy zgodne z kierunkiem włosów.
- Workflow bazuje na Curve > Path i osobnej krzywej jako bevel object.
- Karty są układane warstwami od dołu do góry; druga warstwa jest rzadsza i lekko odsunięta od głównej masy.
- Korzenie trzeba dopasować do skóry bez przecinania głowy i uszu.
- Szerokość kart zależy od funkcji pasma: szerzej dla masy, wężej dla breakup/silhouette.
- Bangs i bun są osobnymi konstrukcjami.
- Przed Curve→Mesh autor redukuje curve resolution tak nisko, jak pozwala zachowanie kształtu; domyślna wysoka rozdzielczość jest za ciężka dla gry.
- Root transition używa maskowania/alpha, nie nieprzezroczystej kopuły.

### AETHERQOR INFERENCE
- Nie wracać do odrzuconego opaque scalp cap.
- Budżet 1800 tri rozdzielić na base coverage / secondary flow / bangs / silhouette / feature volume.
- Ponytail, bun i braid muszą być realnymi topologiami, nie wariantem parametru length.
- Najpierw redukować curve resolution, dopiero potem konwersja do mesh i finalny triangle count.

---

## V02 — Full Character UV Unwrap in Blender
URL: https://www.youtube.com/watch?v=gzAWTOUig3s
Czas: 11:26
Rozdziały: 00:46 separate UV parts; 06:27 prepare map; 07:50 remaining UVs; 08:43 organize tile.

### VIDEO
- Ciało jest dzielone logicznie na ręce, ramiona, tors, nogi, stopy i głowę.
- Seamy idą w mniej widocznych miejscach, np. po wewnętrznej/tylnej stronie.
- Brakujące seamy są dodawane, gdy unwrap nie otwiera części poprawnie.
- Używany jest Angle Based unwrap.
- Twarz dostaje większą powierzchnię UV, bo potrzebuje większej szczegółowości.
- Packing jest poprawiany ręcznie dla lepszego wykorzystania tile.

### AETHERQOR INFERENCE
- Jeśli nowe ciało F nadal jest hm08, preferować poprawne native/canonical UV zamiast bezsensownego transferu starej uszkodzonej siatki.
- Dla innej topologii mierzyć UV overlap, flipped faces, stretch, seam continuity i texel density twarzy.

---

## V03 — Hair Card Studio / procedural hair cards
URL: https://www.youtube.com/watch?v=GEpJLXyFz10
Czas: 09:10
Rozdziały: 00:36 install; 01:25 hair cards; 05:20 curls/frizz; 06:39 lighting; 06:50 render; 07:50 presets.

### VIDEO
- Narzędzie steruje points, root/tip thickness, density, spacing, curls i frizz.
- Więcej punktów daje gładszą krzywą i większą swobodę curl/frizz, ale zwiększa koszt.
- Eksport może generować diffuse/color, normal, alpha, specular i inne mapy.
- Presety tworzą różne archetypy kart.
- Cycles służy do authoring/bake jakości map, nie do runtime.

### AETHERQOR INFERENCE
- Zbudować małą bibliotekę typów kart: mass, transition, breakup, bangs, tie/ponytail, braid/bun.
- Zamiast stałej liczby segmentów stosować adaptive points per curve.

---

## V04 — Modular Armor: AI → Blender → Unity
URL: https://www.youtube.com/watch?v=n90VvHeGf48
Czas: 33:45
Rozdziały: 07:34 split geometry Blender; 20:42 Unity/UV fixes; 24:09 rigging; 28:07 animation; 30:40 appearance.

### VIDEO — KLUCZOWY DOWÓD DLA MODULARNEGO GEARU
- Autor tworzy bazę bez pancerza oraz pancerz w tej samej pozie/proporcjach, żeby geometrie się pokrywały.
- Próba "exploding out individual parts of armor" dała słabe dopasowanie, liczne szczeliny i widoczną skórę.
- Najbardziej powtarzalną metodą okazało się cięcie **zarówno ciała, jak i zbroi na odpowiadających granicach**.
- Przy lustrzanych częściach małe kontrolowane overlap w osi jest dopuszczone, jeśli usuwa seam; połówki są łączone.
- Po problemach z normalami autor robi recalc/flip i poprawny FBX export.
- W Unity aktywacja chest armor idzie razem z ukryciem odpowiadającego regionu ciała, aby usunąć poke-through.
- Head musi być niezależny od body, jeśli body jest ukrywane slotami.
- Rig jest traktowany wspólnie, a w Unity używany jest Humanoid.

### AETHERQOR INFERENCE
- To bezpośrednio wspiera istniejący hide-body-region, który już przeszedł 16/16 kompletów i 300 losowych cykli.
- Nie wracać do naiwnych osobnych chunks przy pozostawieniu pełnego ciała pod spodem.
- Granice body-region ↔ gear-slot mają być kontraktem.
- Gear pozostaje removable SkinnedMeshRenderer/slotem; nie wolno łamać wymogu equip/unequip tylko dlatego, że tutorial pokazuje prostszy kompromis.

---

## V05 — Modeling Armor and Accessories in Blender
URL: https://www.youtube.com/watch?v=9gdRo9hy-wM
Czas: 100:36
Zakres: armor on base mesh, cleanup, extrude, separate armor/accessories, belts, plates, straps, arm/leg armor, helmet, cloth.

### VIDEO
- Elementy przypisane głównie do jednej kości i nieprzechodzące przez joint mogą być osobnymi częściami.
- Breastplate przechodzący przez wiele joints/spine jest budowany silnie w korelacji z bazowym ciałem, bo niezależna luźna bryła może klipować podczas animacji.
- Loose cloth jest osobne.
- Autor buduje outline pancerza na istniejącej powierzchni, kontroluje edge loops, usuwa n-gony i dopiero potem rozwija detal.
- Straps, plates i accessories mają własną logikę geometryczną.

### KONFLIKT
Tutorial czasem integruje breastplate z bazową siatką. AETHERQOR wymaga removable chest, więc **nie wolno trwale scalać chest z body**.

### AETHERQOR INFERENCE
- Wykorzystać zasadę body-correlated construction: removable chest shell ma być wyprowadzony z powierzchni/landmarków ciała i transferować wagi.
- Thin plate, strap i cloth nie mogą przechodzić przez jeden wspólny remesh.

---

## V06 — 2D Image → Stylized Character in Blender
URL: https://www.youtube.com/watch?v=Lw70aXMD90Y
Czas: 09:47
Rozdziały: 00:25 head; 02:37 body; 03:17 retopology; 03:41 UV; 03:56 skin paint; 05:22 Substance→Blender; 06:19 dress; 07:20 brows/eyes.

### VIDEO
- Sculpt przechodzi przez retopology i projekcję kształtu na nową siatkę.
- Face paint rozdziela base tone, ciemniejszy orbit/nose, cheeks/lips, highlights/freckles i roughness.
- Hair ma kierunkową masę bazową i dodatkowe pasma budowane warstwowo.
- Tight dress jest tworzona "using body as the base", podobnie do retopologii.
- Oko ma sclera, iris, local redness, caruncle i jawny catchlight cue.

### AETHERQOR INFERENCE
- P2: procedural face masks muszą odtwarzać warstwową logikę cech, nie jeden flat color.
- P5: cups/underband/straps budować z body landmarks/surface, nie world-Z plane.
- P3: catchlight może być jawnie projektowany, ale musi przejść Unity test.

---

## V07 — Full Realistic Character Workflow
URL: https://www.youtube.com/watch?v=BUVMW-vdp4A
Czas: 46:10
Rozdziały: 01:54 sculpt; 07:34 retopo; 12:23 reprojection; 14:46 UV; 16:51 production sculpt; 17:23 pores; 19:43 texture; 23:41 maps; 29:05 skin shading; 35:02 groom.

### VIDEO
- Design i silhouette muszą być rozstrzygnięte przed retopologią. Retopo jest techniczne, nie projektowe.
- Nie dodaje się finalnych porów przed rozwiązaniem formy i retopo.
- Retopo idzie general-to-specific: duże funkcjonalne loops przed lokalnym detalem.
- Workflow używa polygon/extrude + Shrinkwrap + Mirror i trzyma topologię możliwie prostą.
- Auto-topology może wyglądać przekonująco, ale nie dawać funkcjonalnych loopów ust/oczu.
- Reprojection przenosi shape/mid-frequency detail na poprawną topologię.
- UV wykonywane jest po reprojection, żeby pasowało do finalnej geometrii.
- BaseColor ma zawierać kolor, nie baked lighting/shadow.
- Roughness i scattering są osobnymi mapami i są oceniane w final renderze.
- Workflow jest iteracyjny: mapy są wielokrotnie oceniane po eksporcie.
- Oczy oraz groom małych elementów mocno wpływają na realizm.

### AETHERQOR INFERENCE
- P9: brak hallmark/silhouette nie zostanie naprawiony przez retopo ani recolor. Wtedy wracamy do konceptu/generacji.
- P2: oddzielić BaseColor od roughness i nie utrwalać fake AO/light jako skóry.
- UDIM z tutorialu nie jest automatycznie rozwiązaniem mobile.

---

## V08 — Retopology for Beginners / Correct Way
URL: https://www.youtube.com/watch?v=CuQzPDs99yM
Czas: 30:30
Rozdziały: 05:31 settings; 24:23 demo.

### VIDEO
- Shrinkwrap + face snapping są używane razem.
- Mirror ma Clipping.
- Minimalny Displace może służyć wyłącznie do viewport z-fightingu.
- Autor ostrzega przed modelowaniem retopo z włączonym Subdivision Surface, bo daje fałszywie ładny obraz zamiast realnej siatki.
- Retopo jest budowane jako raw polygons.
- Najważniejsza reguła: jak najmniej loopów na początku, rozdzielczość dopiero tam, gdzie trzeba.
- Zbyt gęsta siatka na starcie to typowy błąd.

### AETHERQOR INFERENCE
- P6: thin-shell nie może zaczynać od brutalnego voxel 30–64 mm.
- Ocena raw cage + silhouette jest obowiązkowa.
- Potrzebny branch geometry, nie one-size-fits-all remesh.

---

## V09 — Game Ready Eyes Blender → Unreal
URL: https://www.youtube.com/watch?v=97nGK7wBGQI
Brak rozdziałów.

### VIDEO
- System rozdziela cornea, eye body/sclera i iris.
- Autor czyści shape keys/modifiers/vertex groups i aplikuje transforms przed eksportem.
- UV map names są normalizowane przed join, bo różne UV sets mogą psuć połączenie.
- Oczy mogą być złączone/mirrorowane, potem rozdzielone L/R i przypięte do rigu.
- Niepotrzebne vertex groups są usuwane.
- Iris eksportuje texture + normal.
- Materiał jest Unreal-specific i tutorial sam przedstawia go jako szybki game-ready shortcut, nie perfekcyjne oko.

### AETHERQOR INFERENCE
- Bierzemy organizację geometrii i eksportu, nie Unreal material values.
- Testować EYE_LITE i EYE_MID w Unity URP.
- Eye occlusion zostaje tylko jeśli nie zasłania iris.

---

## V10 — Unity VFX Graph Learning Templates
URL: https://www.youtube.com/watch?v=DKVdg8DsIVY
Czas: 20:02
Rozdziały: 01:36 contexts; 03:29 spawn; 04:10 outputs; 05:38 bounds; 05:56 capacity; 06:20 orient; 08:00 flipbook; 11:28 Sample Mesh; 12:16 Sample Texture; 12:39 SDF; 13:46 Sample Skinned Mesh; 15:18 collisions; 16:20 GPU event; 16:45 decals; 17:40 strips.

### VIDEO
- Architektura: Spawn → Initialize → Update → Output.
- Atrybuty przenoszą dane pomiędzy kontekstami.
- Jedna symulacja może mieć wiele outputs.
- Bounds i Capacity są realnymi parametrami kosztu/zakresu.
- Orient/rotation/pivots sterują billboard/mesh/strip.
- Flipbook korzysta z TexIndex.
- Sample Mesh / Sample Texture 2D wiążą cząstki z geometrią/UV.
- SDF może służyć do surface/collision logic.
- Sample Skinned Mesh może emitować/followować animowaną powierzchnię; stabilny random attribute pomaga utrzymać próbkę.
- GPU Event on collide może tworzyć child effect.
- Particle strips są użyteczne dla trails.

### OFFICIAL
Unity 6: VFX Graph jest production-ready dla HDRP, a pełne wsparcie URP i kompatybilnych urządzeń mobilnych nadal jest rozwijane.
Źródło: https://docs.unity3d.com/6000.0/Documentation/Manual/com.unity.visualeffectgraph.html

### AETHERQOR INFERENCE
- VFX Graph jako laboratorium/prototyp oraz produkcja tylko po benchmarku PASS.
- Krytyczne skille muszą mieć fallback Particle System + Shader Graph/mesh.
- Capacity, bounds, overdraw, transparency i memory wchodzą do mobile gate.

---

# WNIOSKI PRZEKROJOWE

1. **Body-correlated construction** powtarza się w kilku źródłach. Removable gear ma wynikać z powierzchni/landmarków ciała, a nie z przypadkowo pociętej bryły.
2. **Body-region ↔ gear-slot jest kontraktem.** Tutorial modular armor wprost pokazuje szczeliny po naiwnym rozbiciu zbroi. AETHERQOR ma już właściwy fundament hide regions.
3. **Retopo to kilka problemów.** Body deform mesh, thin plate, strap, cloth, hair card i crystal potrzebują różnych gałęzi.
4. **Design przed retopo.** Jeśli klasy mają ten sam obrys, decymacja ani shader tego nie naprawi.
5. **Face realism jest sumą niezależnych sygnałów.** BaseColor, local roughness, orbit, lips, brows, lashes, eye geometry/catchlight i groom muszą być rozdzielne.
6. **Mobile VFX potrzebuje dual path.** VFX Graph daje zaawansowane narzędzia, ale dopóki official Unity 6 nie deklaruje pełnego URP/mobile support, fallback mobile jest częścią Definition of Done.
