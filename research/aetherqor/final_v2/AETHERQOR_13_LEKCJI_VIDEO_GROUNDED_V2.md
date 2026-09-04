# AETHERQOR — 13 LEKCJI PRODUKCYJNYCH V2

Źródło stanu: `AETHERQOR_PROBLEMY_DO_ZAMKNIECIA(1).txt`
Źródła video: 10/10 tutoriali przetworzonych przez lokalny runner.
Zasada: każda lekcja kończy się decyzją, eksperymentem i mierzalnym gate.

---

# 1. NOWE CIAŁO KOBIECE, ZERO KOLEJNYCH NAPRAW STAREGO

## Stan
38 connected components, 73 holes, 2328 boundary edges, largest component 29,5%, realne luki. Próby ray/weld/fill i volumetric union zostały już obalone.

## Źródła
OFFICIAL MPFB: hm08 ma stałą topologię niezależnie od phenotype. HumanService tworzy basemesh i potrafi odtworzyć charakter z JSON/MHM/presetu. Oficjalny sample FBX używa staging copy, bake modifierów i stripping helper geometry.
Blender 5.2 Data Transfer potrafi transferować vertex groups i UV przez interpolated mappings.

## Decyzja
1. Forensic diff M vs F krok po kroku.
2. Znaleźć pierwszy etap, gdzie F przechodzi 1 component → >1.
3. Odtworzyć kobietę na czystym hm08 z rzeczywistego phenotype/presetu.
4. Jeśli nadal hm08, preferować canonical MPFB UV.
5. Wagi: A/B `Nearest Face Interpolated` vs `Projected Face Interpolated`, zwycięzca po deform error.
6. Shape keys: najpierw odtworzyć te same MPFB/MakeHuman targets. UV/barycentric transfer tylko plan B.

## Gate
PASS: 1 body shell, 0 boundary, 0 nonmanifold, brak duplicate skin shells, zgodna skala/rest pose, spójne normalne, 6-view render bez luk.

---

# 2. TWARZ: MAPY I WARSTWY, NIE FLAT COLOR

## Stan
Flat skin color, jedna roughness 0.58, brak BaseColor/Roughness maps, brows/lashes/lips/orbit/beard.

## Video
Full Character i Realistic Character rozdzielają base tone, orbit/nose variation, cheeks/lips, highlights/freckles i roughness. Realistic Character podkreśla, że BaseColor nie powinien zawierać baked lighting.

## Decyzja
Wpiąć `domaluj_twarz.py` w produkcyjny chain. Wspólne maski mają generować BaseColor + Roughness + opcjonalny DetailNormal.
Maski minimum: brow L/R, lash L/R, lip upper/lower/line, orbit L/R, nostril, beard, cheek warmth, nose warmth, forehead.
Test face 1024 vs 2048 po creator close-up, mip, VRAM i build size.

## Gate
Brows/lashes/lips/orbit/beard czytelne gdzie wymagane, local roughness, brak clown makeup, Blender→Unity parity.

---

# 3. OCZY GAME-READY: GEOMETRIA I APERTURE PRZED SHADEREM

## Stan
Eye position poprawiony do ok. 1 mm clearance. Obecne 4-object eye + occlusion. Refraction nie przeżywa FBX. Oko nadal czyta się jako dark slit.

## Video
Game Ready Eyes rozdziela cornea, sclera/body i iris oraz mocno pilnuje cleanup/UV przed eksportem. Full Character pokazuje rolę sclera, iris, caruncle i catchlight cue.

## Decyzja
A/B/C/D: A sclera+iris; B +cornea transparent bez refraction; C +occlusion; D +catchlight. Zmierzyć widoczną powierzchnię iris/pupil. Jeśli powieki ściskają oko, naprawić geometry/shape, nie podbijać shaderu.
EYE_LITE vs EYE_MID w Unity URP.

## Gate
Iris/pupil/catchlight czytelne, brak black slit, brak transparency artifacts, mobile cost PASS.

---

# 4. WŁOSY <=2000 TRI I PRAWDZIWE WARIANTY

## Stan
3904–7104 tri, 244–444 cards, fake ponytail, bangs na oczach.

## Video
Hair tutorial: warstwowe cards, second layer, root transition, osobne bangs/bun, redukcja curve resolution przed mesh. Hair Card Studio: point count, density, curl/frizz, presety i różne typy kart.

## Decyzja
Target 1800, hard <=2000. Adaptive curve segmentation. Priorytet: hairline, outer silhouette, bang tips, feature volume. Ponytail=gather+tie+root+volume+breakup; bun=gathered flow+mass; braid=interlocking pattern. Keep-out mask wokół iris/pupil.

## Gate
Każdy wariant <=2000 tri, ponytail/bun/braid różne w czarnej sylwetce, zero bald holes, zero hair-eye intersection, Unity alpha/normal PASS.

---

# 5. BIELIZNA KOBIECA JAK ODZIEŻ, NIE PLANE CUT

## Stan
Bra to pas cięty płaszczyzną. Spec: cups offset 2 mm, underwire 4 mm, gore 15 mm, underband 30 mm, straps 15 mm.

## Video
Full Character buduje tight clothing na bazie powierzchni ciała. Armor tutorial pokazuje, że części crossing joints muszą być skorelowane z deformującą bazą. Modular Armor pokazuje gaps po przypadkowych chunks.

## Decyzja
Landmarks: clavicle, sternum, breast apex L/R, inframammary curve, side chest, scapula. Cups=surface patch + 2 mm normal offset + controlled curve boundary. Gore/underband podążają po torsie. Straps=curves po powierzchni, nie przez pachę. Weight transfer z body + arms-up/twist test.

## Gate
Cups/straps/gore czytelne, zero plane-cut look, zero clipping/gaps, poprawny back coverage.

---

# 6. THIN-SHELL RETOPO TO OSOBNA GAŁĄŹ

## Stan
2 075 051 → 13 919 tri. Voxel 30–64 mm usuwa wyspy, ale tworzy spikes. Quadriflow odrzucony.

## Video + official
Retopo tutorial: raw polygons, mało loopów na początku, Shrinkwrap+snap, bez Subdivision illusion. Blender 5.2: Planar Decimate dla mainly flat surfaces z Delimit Material/Seam/Sharp/UV.

## Decyzja
Classifier: SOLID / THIN_SHELL / BRANCHED_THIN / DETAIL_DISCARDABLE.
THIN_SHELL: cleanup → micro-island importance → principal shell → Planar/feature-preserving simplify → optional mid-surface → Solidify tylko jeśli semantycznie poprawne. Po retopo pełny rebake.

## Gate
Brak spikes/teeth, 8-view silhouette w skalibrowanym gate, slot w budżecie, clean bake.

---

# 7. 5 STREF ARTYSTYCZNYCH BEZ AUTOMATYCZNYCH 5 DRAW CALLI

## Stan
Zbroja czyta się jako jeden gunmetal.

## Decyzja
PLATE / TRIM / LINING / STRAPS / ACCENT. Hybrid classifier: source IDs, slot semantics, joint proximity, curvature/normal, components, explicit region volumes, spec overrides. zone_id jako color attribute → bake mask. Edge wear liczyć offline.

## Official Unity
URP Lit/Complex Lit channel packing: R Metallic, G Occlusion, B unused, A Smoothness; sRGB OFF dla packed data.

## Gate
Strefy różne także w grayscale/roughness, draw calls kontrolowane, maska przeżywa Blender→Unity.

---

# 8. RUNY TO GROOVE / GAP / CRYSTAL, NIE STICKER

## Stan
Runy są płaskie i podobne do nitów.

## Decyzja
GROOVE: curve cutter → high-poly groove 2–3 mm → bake normal/cavity/emission. PLATE_GAP: realne 4 mm rozdzielenie płyt + emissive underlay. CRYSTAL: real volume + emission response. LOD0 zachowuje geometrię tylko gdzie parallax/silhouette tego wymaga.

## Gate
Bloom OFF, runa różna od nitu w grayscale/value, funkcja czytelna z gameplay distance, zero sticker look.

---

# 9. SILHOUETTE PRZED RETOPO I SHADE

## Stan
5/7 klas zbyt podobne.

## Video
Realistic Character: design/silhouette ma być rozstrzygnięty przed retopo; retopo jest etapem technicznym.

## Decyzja
14 HERO, ten sam pose/scale, 8 kamer, flat black. Pairwise: IoU, symmetric difference, shoulder width, gear bottom, hallmark presence. Nie wymyślać industry threshold. Skalibrować `AETHERQOR_SILHOUETTE_GATE_V1` na good/mid/bad examples. Jeśli hallmark nie istnieje, wrócić do concept/generation, nie recolor.

## Gate
Klasa rozpoznawalna z black silhouette według project gate.

---

# 10. 7 SIGNATURE SKILLS Z MOBILE FALLBACK

## Stan
Brak finalnych signature VFX.

## Video
VFX Templates: Spawn→Initialize→Update→Output, capacity/bounds, multiple outputs, flipbook, Sample Mesh, Sample Skinned Mesh, SDF, collisions, GPU events, decals, strips.

## Official Unity 6
AnimationEvent może wywołać funkcję w konkretnym punkcie animacji. VFX Graph jest production-ready dla HDRP, ale pełne wsparcie URP/mobile nadal jest rozwijane.

## Decyzja
`SkillDefinition` + canonical sockets + pooling. AnimationEvent tylko jako kontrolowany marker fazy. Każdy skill: telegraph, cast cue, impact, sustain/trail, cleanup. Primary mobile fallback: Particle System + Shader Graph/mesh. VFX Graph tylko po benchmarku PASS.

## Gate
7/7, timing zgodny z animacją, zero stale VFX po cancel, pool stable, mobile profile PASS.

---

# 11. JEDEN WORKFLOW ANIMACJI, NIE ŚLEPE 72→55

## Stan
M=55 bones, old F=72.

## Official Unity 6
Humanoid retargeting pozwala zastosować ten sam zestaw animacji do różnych humanoidów z poprawnie skonfigurowanym Avatar. Dodatkowe twist/face/deform bones nadal trzeba sklasyfikować.

## Decyzja
Bone diff: humanoid/deform, twist/corrective, facial, helper/control, orphan. Test M + new F: valid Avatar, same AnimatorController, same 14 clips. Canonical deform hierarchy/naming tylko po deform test PASS.

## Gate
Valid Avatar M/F, 14 shared clips, brak missing-bone warnings/collapse, gear pozostaje na miejscu.

---

# 12. APPROVED HERO → DETERMINISTYCZNY UNITY IMPORT

## Stan
Unity nadal używa v9/v11 i placeholderów, absolutne texture paths. Runtime gear toggle działa i ma zostać zachowany.

## Video
Modular Armor potwierdza znaczenie poprawnych normals/transforms, niezależnych body/head regions i show/hide underlying body.

## Decyzja
Jedyny staging `APPROVED_HERO`. Manifest: class/gender/version/SHA/skeleton/tri/material/timestamp. `AetherqorHeroAssetPostprocessor.cs`: BaseColor sRGB ON, packed data linear, NormalMap type, missing-map hard fail, stale-v9/v11 hard fail, external-path hard fail. Modular parts mogą pozostać oddzielnymi SkinnedMeshRenderer. Nie używać static Mesh.CombineMeshes jako domyślnego skinned combine.

## Gate
14/14 nowych prefabów, real PBR, valid Avatar, zero stale refs, zero external paths.

---

# 13. ART DIRECTION CLEANUP PO NAPRAWIE SYSTEMOWEJ

- female boob plate → jedna ciągła zewnętrzna krzywizna,
- lower back → pełne pokrycie,
- hands/toes → real armor shells,
- codpiece → mniejsza saliency/height/protrusion,
- 8 buckles → usunąć/redukować/nadać funkcję,
- underwear v2 → 14/14 HERO z version/hash gate.

Nie poprawiać tych rzeczy na starych assetach przed P1/P6/P12.

## Gate
Final contact sheet 14 HERO + art checklist 6/6 PASS.

---

# KOLEJNOŚĆ ZALEŻNOŚCIOWA

P0 snapshot + QA harness → P1 new female body → P11 skeleton/retarget → P2 face → P3 eyes → P4 hair → P5 female underwear → P6 thin-shell retopo → P7 material zones → P8 grooves/emission → P9 silhouettes → P12 approved Unity import → P10 skills/VFX → P13 art cleanup → FINAL 14/14 regression.

Nie propagować assetu dalej, jeśli jego lokalny gate jest FAIL.
