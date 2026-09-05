# AETHERQOR V5 — PUNKTY DO RESEARCHU 2026-09-05

Kontekst staly: mobile AAA, Unity 6 URP, Blender 5.2, budzet postaci 14 000 tri, postac w gameplay ma 90-300 px, 7 klas x 2 plcie.

Cel: rozstrzygnac piec konkretnych problemow. Nie robic przegladu ogolnego. Kazda odpowiedz ma prowadzic do decyzji architektonicznej i testu na realnym AETHERQOR.

## P1. Na co naprawde idzie 14 000 tri?

Zmierzone sloty po Solidify:
- kirys 2600 -> ~5200 tri
- helm 1500 -> ~3000
- nagolenniki 896 -> 1792
- but 782 -> ~1560
- rekawica 636 -> ~1270
- pas 560 -> 1120
- naramiennik 526 -> 1052
- karwasz 392 -> 784

Suma po Solidify dla 12 zintegrowanych obiektow: 12 535 / 14 000 tri. Zostaje 1465 tri na cialo, wlosy, bielizne i szesc warstw tkaniny. Sama podloga 200 tri x 11 obiektow = 2200, wiec obecny budzet jest matematycznie niespojny.

Przekroczenia stref:
- z_hands 2021 vs 700 (+189%)
- z_legs 3121 vs 1800
- z_feet 1540 vs 700

Kirys 595 tri i helm 358 tri sa fasetowane mimo 100% use_smooth=True; FACE/EDGE/OFF render piksel-w-piksel identyczny. Normal bake z donora 1.65M tri ratuje detal powierzchni, ale nie sylwetke.

Rozstrzygnac:
- realne LOD0/gameplay triangle counts nowoczesnych high-end mobile characters 2024-2026, szczegolnie Wuthering Waves / Genshin / Diablo Immortal / BDM;
- czy publiczne liczby sa pelnym renderowanym characterem, czy tylko body/mesh bez broni/wlosow/gear;
- typowy podzial body / armor-clothing / hair / weapons-accessories;
- czy 14k powinno byc gameplay LOD, a nie universal hero/equipment LOD;
- czy armor plates powinny byc one-sided shell z lokalna gruboscia tylko na widocznych rimach zamiast globalnego Solidify;
- koszt Cull Off kontra dodatkowe interior triangles;
- ile modularnych slotow jest faktycznie widocznych jednoczesnie i czy 19 runtime slots oznacza 19 osobnych geometry layers czy logiczne slots scalone do mniejszej liczby renderowanych shells.

## P2. OVERLAPPED_SHELL_SOUP -> jedna valid bryla

Donory Meshy to nachodzace otwarte plyty bez wspolnej objetosci.

Stan metod:
- isolated Voxel Remesh: helm SI=0.21%, ale kirys dominant island 1.8-11.5% dla 0.5-3.0 mm
- Z-slice loft + Shrinkwrap PROJECT: kirys SI=0.24%, ale concavity i panel lines gina
- bone-axis loft: naramiennik SI=0.00%, ale wymaga body substrate w calym zakresie
- B2 max(donor_r, body_r+14mm): but PASS-like, naramiennik body penetration 37.74%

Nie powtarzac: QRemeshify, Quadriflow, weld+holes_fill, Boolean Union na soup, Laplacian, samo podniesienie do 25k.

Rozstrzygnac CGAL Alpha_wrap_3:
- triangle soup jako bezposredni input;
- watertight / orientable / 2-manifold / intersection-free guarantees;
- alpha i offset dla skali 10-40 cm i gapow 3-8 mm;
- kiedy cavity/gap zostaje zalany;
- praktyczny CLI/Python/Blender bridge;
- CGAL vs Houdini VDB From Polygons / SDF vs ZBrush Dynamesh+ZRemesher vs Exoside Quad Remesher vs Instant Meshes.

## P3. Druga decymacja niszczy sloty juz bedace w budzecie

Skorupy wchodza do lancucha juz w targetach 392-2600 tri, ale retopo_postaci.py ponownie rozdziela globalne 14k i tnie je drugi raz.

Objawy:
- naramiennik: boundary loops 16/16 -> 11/11 i 11/12, utrata symetrii
- nogawica: stepped artifacts na lydce
- Decimate Planar Delimit=Sharp pogorszyl kirys SI 3.16% -> 5.78%

Rozstrzygnac:
- production architecture: per-part targets + global allocator czy whole-character reduction;
- jak zachowac suma <= target bez niszczenia juz zatwierdzonych slotow;
- vertex locks / geometry importance / vertex weights / modular seam protection / screen-size target;
- czy runtime LOD powinien byc generowany per modular slot z globalnym solverem budzetu;
- jak chronic silhouette/boundary loops i deformation zones.

## P4. Hair cards: faceting przez occlusion boundaries miedzy kartami

5 stylow 1600-2000 tri, scalp exposure 1.11-2.43%.

Wyczerpane:
1. scalp normal transfer DATA_TRANSFER/CUSTOM_NORMAL/POLYINTERP_NEAREST, max_distance 0.06, mix 0.72: custom normals sa, obraz bez roznicy;
2. wiekszy SEG cap: 4/5 stylow ponad budzet przy seg=4, wszystkie ponad przy 5/6;
3. solid scalp dome: exposure 1.83% -> 0.00%, mniej tri, ale faceting zostal i prostokat wystaje 3/4.

Diagnoza: defekt pochodzi z main/underlay layers i granic okluzji nakladajacych sie plaskich kart.

Rozstrzygnac:
- production scalp-coverage architecture przy ~1800 tri;
- opaque base cards / cap texture / layered clumps / breakup cards;
- czy granice okluzji naprawia geometria (curved cards, more layers), depth/sorting, alpha clip/dither/blend czy material;
- URP mobile: DITHERED vs Alpha Clip vs Alpha Blend + two-sided/backfaces, koszt overdraw i sorting.

## P5. Sylwetka w gameplay camera, gdy klasa nie ma broni

Obecny gate: 21 par x 6 views x 2 resolutions, pairwise IoU <=0.85, anchor >=10% maski. 0/21 par ponad threshold.

Problem: camera azimuth 35°, elevation 50°. Klasy bez dlugiego/ukosnego elementu, np. mag w plaszczu i wrozbita w kapturze, zlewaja sie w ciemne plamy; roznica glownie z footprintu.

Rozstrzygnac:
- czy top-down MMO identity ma byc niesiona glownie silhouette, czy celowo wspierana przez weapon/prop/color/material/VFX/animation;
- czy kazda klasa potrzebuje top-down protruding anchor;
- jakie metryki poza IoU koreluja z recognition: contour Hausdorff/Chamfer, radial descriptor, confusion matrix, timed human recognition;
- jak kalibrowac kontrakt pod real gameplay camera zamiast ortho-style test masks.

## Zamkniete, nie badac ponownie

- runtime equipment/unequip/hide-masks/transmog
- MaterialPropertyBlock vs SRP Batcher
- VFX Graph mobile URP
- retarget animacji
- URP/Lit packing
- male/female gauntlet stretch: biala lista wag max 2 influences daje 1.000x na 8 pomiarach
- ogolny modular gear / BDM / Silkroad research
