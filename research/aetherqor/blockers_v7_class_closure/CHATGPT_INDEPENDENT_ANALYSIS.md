# AETHERQOR V7 — CHATGPT INDEPENDENT ANALYSIS

This document is an independent technical position. Claude must verify it against V7 video frames, authoritative sources and real AETHERQOR measurements. Do not treat any numeric threshold marked EXPERIMENT as an industry standard.

## P1 — tier architecture

### Diagnosis
931 full unique texture sets is an architecture failure, not a production challenge. The scalable unit should be material family + reusable surface library + masks + parameter table. A tier system should not multiply every PBR channel by every slot unless the visual content genuinely changes.

### Proposed AETHERQOR model
1. Keep one UV0 for baked unique macro information where required.
2. Reserve reusable trim/atlas regions for metal borders, leather seams, cloth hems, runic strips and repeating plate language.
3. Add one compact tier mask texture or pack tier regions into an existing mask map.
4. Store tier appearance in data, not new materials: palette IDs, smoothness/metallic offsets, emission intensity/color, detail-normal scale, optional dirt/wear scalar.
5. Generate only rare tier-specific overlay textures when the art direction requires unique painted glyphs or motifs.

### Suggested material families
- BODY_SKIN
- FACE_EYES if face close-up requires independent quality
- HAIR
- OPAQUE_METAL_GEAR
- OPAQUE_CLOTH_LEATHER
- WEAPON
- TRANSPARENT_SPECIAL only when unavoidable

A 19-slot logical equipment system does not require 19 renderer materials.

### Required data files
`tier_visual_table.json` with fields:
`tier, base_palette_id, accent_palette_id, metal_smoothness, cloth_smoothness, emission_intensity, emission_color, detail_normal_scale, wear_scalar`.

`material_family_manifest.json` maps slots to shared families and texture atlases.

### Memory experiment
For one complete promoted character calculate GPU memory for:
- current 32-material layout;
- 2K shared gear atlas family;
- 2x 2K atlases split metal vs cloth/leather;
- 4K closeup atlas + 2K gameplay atlas.
Use actual platform compression. Report resident bytes, not PNG file size.

## P2 — rings / buckles / amulets

The correct question is not 'is a ring geometry?' but 'does this feature produce a stable screen-space cue?'.

### Automatic projected-size tool
For each micro-prop and camera sample, project its bounding box and silhouette to pixels. Output:
`slot, prop, view, character_height_px, bbox_width_px, bbox_height_px, occupied_pixels, silhouette_delta_pixels`.

### EXPERIMENT routing rules
- silhouette_delta < 1 px and occupied_pixels < 4: REMOVE gameplay geometry; bake only if texture contribution remains visible.
- occupied_pixels 4-16 but no silhouette change: NORMAL/ALBEDO/ROUGHNESS bake preferred.
- stable silhouette delta >=1-2 px in at least two key views: geometry candidate.
- independent motion/physics: geometry may be justified even if small, but test readability.
- equipment/inspect camera: separate high-detail accessory variant allowed.

### Rings specifically
At 90-300 px character height a finger ring is expected to be below reliable gameplay geometric readability. Do not mass-integrate 14 rings until the projected-size script proves otherwise. Keep `pierscien.py` for equipment-closeup LOD if needed.

## P3 — enhancement +0..+10

### Proposed architecture
One enhancement mask sampled in the existing URP gear shader. Exact numeric +0..+10 remains UI/gameplay data; visual layer compresses it into perceptually meaningful bands.

Recommended parameters:
`_EnhanceLevel01`
`_EnhanceColor`
`_EnhanceEmission`
`_EnhanceSmoothnessBoost`
`_EnhanceMaskStrength`

Do not swap material assets for every level.

### Visual-band experiment
Render all eleven levels in a controlled rotating-light clip and real arena clip at 90, 150, 220, 300 px. Ask observers pairwise whether N and N+1 differ. Collapse adjacent levels when discrimination is weak. A likely result is 3-4 visual bands, but this is not assumed.

### GPU/CPU test
For 10 characters compare:
A. 11 duplicated material assets / instances
B. shared material + supported per-renderer parameter path
C. shared material + small lookup texture/structured data if needed
Measure draw calls, SetPass/state changes, SRP batches, main-thread render time and GPU time. Keep whichever is measurably best in the actual Unity 6 URP project.

## P4 — 32 materials / 53 meshes

### Diagnosis
32 materials means many state boundaries. 53 meshes means many renderer/submesh submission points unless merged elsewhere. SRP Batcher can reduce CPU setup but does not erase all draws. The current count deserves redesign.

### Runtime architecture candidate
Authoring remains modular. After equipment changes, build cached render groups:
1. OPAQUE_BODY_GEAR skinned aggregate where compatible
2. HAIR
3. EYES/FACE only if necessary
4. WEAPON
5. OFFHAND if independently animated
6. TRANSPARENT_SPECIAL

Do not rebuild every frame. Rebuild only on equip/unequip/transmog changes and cache meshes by equipment signature where memory permits.

### Tests
- current 53/32
- shared materials only, no mesh merge
- mesh merge by material family
- full compatible opaque aggregation + separate special groups
Measure on 1, 5, 10 characters.

### QA gates to implement
`renderer_count_gameplay`
`material_count_gameplay`
`submesh_count_gameplay`
`draw_calls_character_pass`
`texture_resident_bytes_character`
`skin_bones_per_renderer`
No hard thresholds until device data is collected; first goal is to quantify the actual reduction and identify visual regressions.

## P5 — 7AFC class recognition

### Why current gate can lie
Pairwise IoU can be low because footprints differ while the classes are still perceptually confusable. Anchor area can be >=10% while fully contained inside the same robe contour.

### Add contour attribution
During mask render, render class anchor to a separate ID buffer. For every pixel/edge on the final silhouette contour, attribute which object generated it. Compute:
`outer_anchor_contribution`.
This directly measures whether the anchor changes the outline.

### Radial mass descriptor
At the projected centroid sample 16 angular sectors and record furthest silhouette radius normalized by character height. Compare descriptors between classes. This catches top-view mass distribution differences that IoU can dilute.

### Human test app
Generate a local HTML/Unity test with randomized trials:
- 7 alternatives always visible after stimulus disappears
- exposure 750 ms default
- 64/90/128/150/220 px
- stages silhouette, +anchor, normal material/color, idle animation
- log class, response, correct, latency, resolution, condition, participant ID
Output confusion matrix and per-pair confusion rate.

### Acceptance calibration
Do not invent a universal cutoff. Correlate IoU, Hausdorff/Chamfer, radial distance and outer-anchor contribution with human error. Select the smallest metric set that predicts confusion in these seven classes.

## Global instruction
Do not spend the V7 cycle re-researching Alpha Wrap, shell soup, VFX Graph, runtime equipment architecture, retarget or URP map packing. V7 exists to stop five new scaling mistakes before they enter production.
