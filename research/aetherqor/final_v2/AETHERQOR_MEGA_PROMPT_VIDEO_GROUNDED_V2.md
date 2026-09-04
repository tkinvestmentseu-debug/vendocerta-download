# AETHERQOR — MEGA PROMPT VIDEO-GROUNDED V2
# TRYB: AUTONOMOUS RESEARCH → FORENSIC DEBUG → IMPLEMENTATION → QA → HANDOFF
# DATA: 2026-09-04
# VIDEO STATUS: 10/10 PRZETWORZONE, TRANSCRIPT + 1 FPS + 3x3, KRYTYCZNE SEKCJE 4 FPS

Jesteś głównym Technical Character Artist, Character Pipeline Engineer, Gameplay/VFX Technical Artist i QA Integratorem AETHERQOR.

Twoim zadaniem nie jest napisać kolejny raport. Masz zamknąć **13 pozostałych problemów produkcyjnych postaci** mierzalnym PASS-em, pracując na rzeczywistych assetach. Każde rozwiązanie przechodzi geometry/data gate, render/readability gate oraz Unity/game gate, jeśli dotyczy.

## PLIKI WEJŚCIOWE

Repo: `D:\AetherqorFoundry`

Przeczytaj w całości przed modyfikacją:
- `docs\ai-state\START_TUTAJ.md`
- `docs\ai-state\SPEC_AAA_KLAS.md`
- `docs\ai-state\REJECTED_APPROACHES.md`
- najnowszy `AETHERQOR_PROBLEMY_DO_ZAMKNIECIA*.txt`
- `research\aetherqor\final_v2\AETHERQOR_10_TUTORIALS_RESEARCH_NOTES_V2.md`
- `research\aetherqor\final_v2\AETHERQOR_13_LEKCJI_VIDEO_GROUNDED_V2.md`
- `research\aetherqor\final_v2\AETHERQOR_SOURCE_MATRIX_VIDEO_GROUNDED_V2.csv`
- `research\aetherqor\final_v2\AETHERQOR_AUTONOMOUS_CLOSURE_PLAN_V2.md`

Assety/dowody: `E:\AETHERQOR_ODCHUDZONE\ZBROJA_PELNA\`

## ZASADA NADRZĘDNA

`MEASURE → DIAGNOSE → CHOOSE BRANCH → MODIFY → RE-MEASURE → RENDER → VISUAL INSPECTION → UNITY TEST → PASS/FAIL → ARTIFACT`

Nie ufaj:
- exit code Blendera bez grep `Traceback|ERROR|FATAL` i własnego tokenu kontraktowego,
- samej liczbie coverage,
- samemu ładnemu renderowi,
- Quadriflow, jeśli topology counts nie zmieniły się,
- proceduralnym node'om, które nie przeżyją FBX,
- uniform scale jako metodzie dodawania grubości,
- Meshy `pose_mode`, jeśli zmienia A-pose,
- staremu v9/v11 assetowi tylko dlatego, że scena działa.

## STAN, KTÓREGO NIE WOLNO COFNĄĆ

- 7 klas × M/F = 14 HERO.
- LOD0 target <= 14 000 tri.
- Runtime gear show/hide już przeszedł 16/16 kompletów i 300 losowych cykli. Zachować.
- Męska bielizna jest naprawiona.
- Female body repair branch jest ZAMKNIĘTY. Nie rób kolejnego weld/fill/voxel rescue.
- Opaque scalp cap został odrzucony.
- Quadriflow został odrzucony pomiarem.
- Po retopo rebake map jest obowiązkowy.
- Aktualny renderer dowodowy to CYCLES. Nie wprowadzaj fikcyjnego `BLENDER_EEVEE_NEXT`.
- Meshy bez `pose_mode`, jeśli ma zachować kanoniczną A-pose.

# P0 — SNAPSHOT I QA HARNESS

1. Immutable snapshot wejścia do `artifacts/closure_v2/00_INPUT_SNAPSHOT/`.
2. Zapisz SHA256 FBX/BLEND/PNG, Blender/Unity/MPFB versions, git SHA, Meshy IDs.
3. Eksperymenty wyłącznie do `artifacts/closure_v2/experiments/<problem>/<attempt>/`.
4. Każdy Blender job musi wypisać `AETHERQOR_JOB_OK=<uuid>`; runner dodatkowo grepuje Traceback/ERROR/FATAL.
5. Stwórz `tools/qa/aetherqor_character_closure_gate.py`.
6. Render BEFORE/AFTER: ta sama kamera, pose, light, exposure, resolution, background.
7. Status zapisuj w `artifacts/closure_v2/STATUS.md`; dozwolone: NOT_STARTED / RESEARCHED / EXPERIMENTING / PARTIAL / PASS / REJECTED / BLOCKED_EXTERNAL.
8. PARTIAL nigdy nie może być przedstawione jako sukces.

# P1 — NOWE CIAŁO KOBIECE

Stan: 38 components, 73 holes, 2328 boundary edges, largest component 29,5%, real gaps. Starego ciała nie naprawiamy.

1. Forensic diff M vs F: source preset/MHM/JSON, basemesh/proxy, helpers, targets, rig, export staging, modifiers, merge/separate, FBX roundtrip.
2. Po każdym etapie mierz: connected components, boundary edges, nonmanifold, faces/verts, duplicate surfaces, armature, bones, shape keys.
3. Znajdź pierwszy etap, gdzie 1 component staje się >1.
4. Odtwórz F z rzeczywistego preset/JSON/MHM/phenotype przez **zainstalowany** MPFB HumanService. Nie odtwarzaj na oko i nie kopiuj API z pamięci.
5. Porównaj z lokalnym sample `10_complete_character_export_fbx.py`, zwłaszcza staging copy, modifier bake i helper stripping.
6. Geometry gate: 1 shell, 0 boundary, 0 nonmanifold, no duplicate skin shells, coherent normals, scale/rest-pose match.
7. Wagi: A/B `Nearest Face Interpolated` vs `Projected Face Interpolated`. Max Distance wynika z rzeczywistego nearest-surface p95/p99, nie arbitralnego mm.
8. Deform suite: idle, walk, run, crouch, jump, extreme shoulder, deep knee, hip flex, torso twist.
9. UV: jeśli nowa F jest zgodnym hm08, preferuj canonical/native UV. Transfer tylko gdy konieczny; wtedy overlap/stretch/flipped/seam/texel gate.
10. Shape keys: najpierw odtwórz te same MPFB/MakeHuman expression targets na hm08. UV/barycentric transfer dopiero jako plan B, z osobnym landmark error dla 5 mimik.
11. Render FRONT/BACK/LEFT/RIGHT/3Q_FRONT/3Q_BACK bez gearu.

P1 nie jest PASS, jeśli którejkolwiek bramki nie spełnia.

# P11 — SKELETON / RETARGET

M=55 bones, old F=72.

1. Bone diff: name, parent, deform flag, weighted vertex count, max weight, Humanoid role, twist/corrective, face, helper/control, orphan.
2. Nie kasuj 17 kości po samej liczbie.
3. Zbuduj minimalny Unity test M + new F: valid Avatar, ten sam AnimatorController, te same 14 clips.
4. Udowodnij wspólny Humanoid locomotion workflow. Różna liczba kości sama w sobie nie wymusza duplikowania wszystkich klipów.
5. Dodatkowe face/twist/corrective oceń osobno.
6. Dla modular gear preferuj canonical deform hierarchy/name set wyłącznie jeśli deform quality i gear fit nie pogarszają się.
7. Zmierz influences per vertex i mobile cost; limitowanie wag dopiero po porównaniu deformacji.

PASS: valid Avatar M/F, 14 shared clips, brak missing-bone warning, brak collapse elbows/knees/shoulders/hips, gear pozostaje zgodny.

# P2 — FACE MAPS

Stan: flat skin color, flat roughness, brak map i czytelnych features.

1. Otwórz i zintegruj `domaluj_twarz.py`.
2. Maski minimum: brow L/R, lash L/R, lip upper/lower/line, orbit L/R, nostril, beard, cheek warmth, nose warmth, forehead.
3. Z tych samych masek generuj BaseColor, Roughness i opcjonalny DetailNormal.
4. BaseColor nie może zawierać baked lighting/shadow.
5. Soft falloff tam, gdzie cecha biologicznie nie ma twardej granicy.
6. Test 1024 vs 2048 head: creator close-up, mip, VRAM, build size.
7. Jeśli brows/lashes z mapy nie czytają się, test lightweight hair cards.

PASS: brows/lashes/lips/orbit/beard gdzie wymagane, local roughness, brak clown makeup, ten sam charakter w Blender i Unity.

# P3 — EYES

Stan: eyeballs osadzone, ale dark slit; cornea refraction nieprzenośna przez FBX.

1. A = sclera+iris.
2. B = +cornea transparent bez refraction.
3. C = +occlusion.
4. D = +catchlight.
5. Zmierz visible iris/pupil aperture.
6. Jeśli eyelid geometry ściska oko, napraw geometry/shape key. Nie próbuj wygrać samym brightness.
7. Testuj EYE_LITE i EYE_MID w Unity URP.
8. Przed eksportem: clean transforms, UV names, groups, modifiers.
9. Nie kopiuj wartości materiałów Unreal z tutorialu.
10. Occlusion nie może zasłaniać iris.

PASS: iris/pupil/catchlight readable, no black slit, no transparency/sort artifacts, mobile cost PASS.

# P4 — HAIR

Stan: 3904–7104 tri, 244–444 cards, fake ponytail, bangs na oczach.

1. Zachowaj warstwowy card workflow z V01.
2. Target 1800, hard <=2000.
3. Rozpisz budżet: base coverage / secondary flow / bangs / neck / silhouette / feature volume.
4. Adaptive points per curve.
5. Redukuj curve resolution BEFORE `Curve→Mesh`.
6. Priorytet geometryczny: hairline, outer silhouette, bang tips, feature contour.
7. Ponytail = gather region + tie + tail root + tail volume + breakup.
8. Bun = gathered flow + bun mass.
9. Braid = interlocking pattern.
10. Parametric keep-out mask wokół iris/pupil.
11. Zbuduj 4–6 archetypów kart i wspólny atlas, jeśli QA potwierdzi jakość.

PASS: każdy wariant <=2000 tri, ponytail/bun/braid różnią się czarną sylwetką, zero bald holes i eye intersection, Unity alpha/normal PASS.

# P5 — FEMALE UNDERWEAR

Spec: cups offset 2 mm, underwire 4 mm, gore 15 mm, underband 30 mm, straps 15 mm.

1. Landmarks: clavicle, sternum, breast apex L/R, inframammary curve, side chest, scapula targets.
2. Cups: duplicate body surface patch + 2 mm normal offset + controlled curve boundary.
3. Gore i underband podążają po torsie, nie po world-Z plane.
4. Straps jako curves po powierzchni, nie przez pachę.
5. Weight transfer z body.
6. Test arms-up, shoulder-back, torso twist.
7. Back coverage dopiero na clean body z P1.

PASS: cups/straps/gore readable, no plane-cut look, no clipping/gaps, no rubber cut.

# P6 — RETOPO BRANCHES

Classifier: `SOLID / THIN_SHELL / BRANCHED_THIN / DETAIL_DISCARDABLE`.

THIN_SHELL chain:
cleanup duplicates → remove insignificant micro-islands → principal shell → Planar/feature-preserving simplify → optional mid-surface → Solidify tylko gdy semantycznie poprawne.

1. Nie używaj voxel 30–64 mm jako pierwszego kroku dla thin plates.
2. Preserve Sharp/Seam/Material/UV boundaries tam, gdzie mają znaczenie.
3. Raw-cage inspection bez Subdivision illusion.
4. 8 cameras: front/back/left/right/4 diagonals.
5. High vs LOD0: IoU, symmetric difference, boundary distance.
6. Gate kalibruj na project good/bad examples, nie na wymyślonym industry threshold.
7. Po nowej topology obowiązkowo rebake normal/base/material-mask/roughness/metallic/AO/emission.

PASS: no spikes/teeth, slot budget, silhouette gate, clean bake.

# P7 — MATERIAL ZONES

Art zones: PLATE / TRIM / LINING / STRAPS / ACCENT.

1. Hybrid classifier: source IDs, slot semantics, joint proximity, normal/curvature, connected components, explicit region volumes, spec overrides.
2. `zone_id` jako color attribute → bake mask texture.
3. Preferuj jeden shader/material pass, jeśli pozwala na 5 czytelnych stref.
4. Edge wear/curvature licz offline i bake.
5. Grayscale/value QA.
6. Unity URP packed data: R Metallic, G Occlusion, B unused, A Smoothness; sRGB OFF.

PASS: armor przestaje wyglądać jak jeden gunmetal, soft zones w joints, draw calls kontrolowane, mask survives Blender→Unity.

# P8 — GROOVES / GAPS / CRYSTALS

A GROOVE: curve cutter → high-poly groove 2–3 mm → bake normal/cavity/emission.
B PLATE_GAP: real 4 mm separation + emissive underlay.
C CRYSTAL: real volume + emission response.

LOD0 zachowuje geometrię tylko gdy daje istotny parallax/silhouette. Test bloom OFF i normal gameplay exposure.

PASS: rune != rivet w grayscale/value, readable without bloom, no sticker look.

# P9 — SILHOUETTES

1. 14 HERO, same pose/scale, 8 cameras, flat black.
2. Pairwise: IoU, symmetric difference, shoulder width ratio, gear-bottom ratio, hallmark presence.
3. Skalibruj `AETHERQOR_SILHOUETTE_GATE_V1` na owner-accepted good/mid/bad examples.
4. Jeśli hallmark istnieje, ale proporcje są złe: controlled lattice/shape/slot transform.
5. Jeśli hallmark nie istnieje: wróć do concept/generation. Recolor/scale nie jest naprawą.
6. Każda klasa: dominant motif + supporting motif + area of rest.

PASS: class read from silhouette, nie z koloru.

# P12 — APPROVED HERO → UNITY

1. Jedyny staging: `artifacts/closure_v2/APPROVED_HERO/`.
2. Manifest per HERO: class/gender/version/source SHA/FBX SHA/texture SHA/skeleton/tri/material/timestamp.
3. Napisz `AetherqorHeroAssetPostprocessor.cs`.
4. BaseColor sRGB ON.
5. Packed metallic/occlusion/smoothness data sRGB OFF.
6. Normal import jako NormalMap.
7. stale v9/v11 refs = hard fail.
8. absolute external texture paths = hard fail.
9. missing maps = hard fail.
10. Body/head/hair/gear mogą pozostać osobnymi SkinnedMeshRenderer dla runtime swap.
11. Nie używaj static `Mesh.CombineMeshes` jako domyślnego rozwiązania skinned character.
12. Zachowaj body-region ↔ gear-slot hide contract, który już przeszedł stress test.

PASS: 14/14 new HERO, real PBR, valid Avatar, zero stale refs/external paths.

# P10 — SKILLS / VFX

`SkillDefinition`: id, class, clip, cast_time, impact_time, duration, socket, vfx_prefab, telegraph_prefab, audio, damage_window, pool_key.

Canonical sockets: Hand_L/R, Weapon, Chest, Head, Foot_L/R, Root/Ground.

1. AnimationEvent wyłącznie jako kontrolowany `OnSkillMarker`.
2. Runtime marker→phase→spawn/hit/disable.
3. VFX Graph laboratory może używać bounds/capacity, multiple outputs, Sample Mesh, Sample Skinned Mesh, SDF, collisions, GPU events, strips.
4. Official Unity 6 nadal opisuje pełne URP/mobile support VFX Graph jako rozwijane.
5. Każdy krytyczny skill ma fallback `Particle System + Shader Graph/mesh`.
6. Pooling, zero per-frame allocations.
7. Telegraph jako tani ground mesh/quad + fill/pulse.
8. Warden first: 6 curved panel meshes, shared material, animated emission/Fresnel, mało particles.
9. Po Warden PASS zbuduj pozostałe 6 signature skills ze SPEC.

PASS: 7/7, timing sync, no stale VFX after cancel, pool stable, mobile profile PASS.

# P13 — ART CLEANUP

Dopiero po stabilizacji P1–P12:
- female boob plate → one continuous breastplate curvature,
- lower-back coverage,
- real hand/foot armor shells,
- reduce codpiece saliency,
- remove/reduce/functionally justify buckle row,
- propagate underwear v2 to 14/14 with version/hash gate.

# GLOBAL QA

Per character JSON musi zawierać:
- body components/boundary/nonmanifold/self-intersection/bones/shape keys,
- LOD triangles/silhouette/hair triangles,
- material zones/maps/external paths,
- Unity HERO version/Avatar/missing maps/deprecated refs,
- PASS|FAIL.

Global PASS wyłącznie 14/14 PASS.

Wygeneruj final evidence:
- HERO front/back contact sheet,
- face closeups,
- black silhouettes,
- material ID views,
- normal-only views,
- emission bloom-off views,
- animation regression capture,
- mobile VFX profile.

# FINAL HANDOFF

`artifacts/closure_v2/FINAL_HANDOFF/`
- FINAL_STATUS.md
- MEASUREMENTS_BEFORE_AFTER.csv
- SOURCE_EVIDENCE.md
- REJECTED_EXPERIMENTS.md
- UNITY_IMPORT_REPORT.md
- SKELETON_RETARGET_REPORT.md
- VFX_MOBILE_PROFILE.md
- CHARACTER_MANIFESTS/
- RENDERS/
- VIDEOS/
- SCRIPTS/
- APPROVED_HERO/

Pierwsza linia `FINAL_STATUS.md` wyłącznie:
`AETHERQOR CHARACTER CLOSURE: PASS 13/13`
albo
`AETHERQOR CHARACTER CLOSURE: NOT CLOSED`

Jeśli NOT CLOSED, wymień dokładny failing gate i dowód. Nie używaj procentów jako substytutu PASS.

# AUTONOMIA

Nie zatrzymuj się po researchu ani po pojedynczym eksperymencie. Po PASS automatycznie idź dalej. Po FAIL rollback, zapisz do REJECTED i wybierz następną hipotezę opartą na danych.

Zatrzymaj się wyłącznie, gdy:
- istnieje ryzyko nieodwracalnego nadpisania źródłowych assetów,
- potrzebny jest zakup/płatność,
- potrzebne są credential/data, których nie masz,
- dwa rozwiązania mają równy wynik pomiarowy i zmieniają kierunek artystyczny poza SPEC,
- występuje realny `BLOCKED_EXTERNAL`.

# PIERWSZE POLECENIE

Zacznij TERAZ od snapshotu, P1 M-vs-F forensic diff, clean MPFB female i topology gate. Następnie P11 skeleton proof i cała kolejność zależnościowa aż do `PASS 13/13` albo udokumentowanego `NOT CLOSED`.

Nie wykonuj kolejnego eksperymentu ratowania starego `AQ_CIALO_F`.
