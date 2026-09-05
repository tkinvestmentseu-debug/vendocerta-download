# AETHERQOR — PYTANIA DO ZAMKNIECIA SIEDMIU KLAS — 2026-09-05

Staly kontekst: mobile AAA, Unity 6 URP, Blender 5.2, 14 000 tri jako aktualny budzet gameplay, postac 90-300 px, 7 klas x 2 plcie. Alpha Wrap jest zamkniety pomiarem i NIE jest przedmiotem tej fali.

## P1 — 7 tierow x 19 slotow bez eksplozji tekstur

Mamy 98 zestawow tekstur tierow w kolejce. Naiwna architektura daje 7 x 19 = 133 zestawy na klase i 931 dla siedmiu klas.

Do rozstrzygniecia:
- trim sheets vs atlasy vs wspolna baza PBR + maski ID + parametr tieru;
- ile tekstur powinno byc realnie unikalnych dla kompletnej postaci;
- czy tier powinien zmieniac teksture, czy przede wszystkim kolor/material/emisje/detail mask;
- jaki jest sensowny budzet pamieci tekstur na postac mobile;
- jak zejsc z obecnych 32 materialow / 53 meshes bez utraty modularnosci i bez 931 zestawow.

Wymagany wynik: konkretna architektura UV/material/tier dla AETHERQOR, wraz z formatem masek i testem pamieci/draw calls.

## P2 — pierscienie i drobne rekwizyty przy 90-300 px

Mamy lancuch pierscien.py / ring_fit.py / dodaj_pierscienie.py, ale nie wiemy czy pierscien powinien istniec jako gameplay geometry.

Do rozstrzygniecia:
- geometria vs normal/albedo/roughness bake;
- minimalny ekranowy rozmiar/coverage, przy ktorym osobna geometria daje mierzalna wartosc;
- osobny model tylko dla equipment/inspect camera;
- zasada dla sprzaczek, amuletow, nitow, lancuszkow i pierscieni.

Wymagany wynik: screen-space gate i routing GAMEPLAY_GEOMETRY / CLOSEUP_GEOMETRY / BAKE_ONLY / REMOVE.

## P3 — +0 do +10 bez 56 profili VFX

Mamy 56 profili efektow i 10 tabel wzmocnienia, ale nie wiemy czy gracz odroznia 11 poziomow przy 90-300 px.

Do rozstrzygniecia:
- emission/material mask/roughness-color modulation versus particle VFX;
- czy jeden wspolny material/shader + parametry wystarczy;
- ile progow jest faktycznie rozroznialnych w gameplay i equipment closeup;
- czy zmiana wartosci property utrzymuje pozadana architekture SRP Batcher/draw calls w naszym realnym setupie.

Wymagany wynik: 3-4 lub inna liczba progow potwierdzona testem, jedna tabela mapujaca +0..+10 do progow wizualnych i Unity implementation test.

## P4 — 32 materialy i 53 siatki na jednej postaci

Do rozstrzygniecia:
- ile materialow/submeshes powinien miec nasz gameplay character;
- co atlasowac razem, a co zachowac osobno (skin, hair, eyes, transparent, weapon, cloth/armor);
- kiedy laczyc sloty po equipie i jak zachowac wymiennosc;
- SRP Batcher nie jest rownoznaczny z jednym draw callem: zmierzyc Frame Debugger/Profiler;
- koszt 1/5/10 postaci na ekranie.

Wymagany wynik: target render-state architecture i automatyczny QA limit materialow/submeshes/rendererow.

## P5 — kalibracja rozpoznawalnosci siedmiu klas

IoU 0.85 jest lokalnym heurystykiem, nie standardem. Bramka przechodzi, ale mag i wieszcz w kamerze gry moga byc myleni.

Do rozstrzygniecia researchowo:
- jakie cechy poza sylwetka sa uzywane w top-down/MOBA/MMO: value, color, weapon/anchor, pose, motion, VFX;
- jakie metryki automatyczne maja sens jako predyktory pomylki czlowieka;
- jak zbudowac krotki 7AFC test i confusion matrix;
- jak mierzyc czy anchor faktycznie zmienia zewnetrzny kontur, zamiast tylko zajmowac 10% maski wewnatrz plaszcza.

Wymagany wynik: gotowy protokol 7AFC 0.5-1.0 s dla 64/90/128/150/220 px oraz metryki IoU + contour + outer-anchor contribution + radial mass descriptor.

## WAZNE: execution bottleneck

Research nie ma udawac, ze zamknie wykonanie siedmiu klas sam. Rownolegle w projekcie pozostaja: przebieg 6 kompletow, naprawa magenty, integracja 7 kotwic, pierscienie, tiery po FIT_V3 i rozszerzenie LOD. Research ma usunac ryzyko kolejnego zlego wyboru architektonicznego i dac Claude konkretne testy do natychmiastowego wdrozenia.

## Zamkniete — nie badac ponownie

Alpha Wrap; VDB; ZRemesher/Quad Remesher/Quadriflow/QRemeshify jako odpowiedz na shell soup; 3-8 mm geometry panel gaps przy 2600 tri; runtime equip/hide/transmog; MPB vs SRP Batcher jako ogolny temat; VFX Graph mobile; retarget; URP/Lit map packing; male/female forearm stretch.
