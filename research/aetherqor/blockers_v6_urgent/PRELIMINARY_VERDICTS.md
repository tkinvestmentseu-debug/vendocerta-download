# AETHERQOR V6 — PRELIMINARY VERDICTS

These are starting decisions for experiments. They are NOT final until local tests pass.

## P1 — 14k budget

VERDICT: `14K_UNIVERSAL_REJECT_FOR_TESTING`

Reason: current assembled minima do not mathematically fit, and authoritative mobile/LOD guidance favors context/device/screen-size variants rather than one count for every viewing mode.

Required test ladder: 14k / 20k / 28k / 40k at 90 / 150 / 220 / 300 px plus equipment close-up.

Do not claim an exact competitor budget. Public extracted models are weak evidence and often lack LOD provenance.

## P2 — full Solidify

VERDICT: `FULL_SOLIDIFY_NOT_DEFAULT`

Candidate architecture: one-sided rigid outer shell with front-face rendering/backface culling plus local rim/sidewall geometry and selective interior patches only where cameras can see them.

Full Solidify remains legal for specific pieces only if the inside is genuinely visible enough to justify the cost.

## P3 — second global decimation

VERDICT: `GLOBAL_RATIO_REJECT`

Candidate architecture:
- approved slot min/target/max levels,
- protected silhouette/deformation/seam sets,
- Blender vertex-group weighting for soft importance,
- CGAL constrained edges for hard seam locks where available,
- canonical seam representation shared by mating slots,
- global allocator choosing legal slot levels based on screen-space error per triangle saved.

If the legal minima exceed the global target, return BUDGET_ARCHITECTURE_IMPOSSIBLE instead of damaging geometry.

## P4 — hair crown faceting

VERDICT: `GEOMETRY_LAYERING_PROBLEM`

Do not repeat scalp-normal transfer, cap-only SEG increase, prior solid dome, or inverted-normal duplicates.

Candidate architecture:
- trimmed hidden opaque/near-opaque inner hair mass for depth coverage,
- irregular/staggered main-card roots and endpoints,
- more curvature only on visually important primary/top cards,
- secondary breakup cards that prevent aligned depth boundaries,
- alpha-clipped two-sided gameplay cards as first material candidate; compare against dither and blend in motion.

## P5 — class identity

VERDICT: `IOU_ALONE_INSUFFICIENT`

Existing anchor-area >=10% gate can pass even when the anchor never reaches the silhouette boundary. Add outer contour contribution, radial mass/sector descriptors and timed human recognition. Do not require every class to carry a long weapon; require a stable primary identity cue that survives the actual top-down gameplay camera.

## Evidence discipline

Final statuses may only be:
- IMPLEMENTED_PASS
- IMPLEMENTED_FAIL with exact reason
- RESEARCH_CONFIRMED_NEEDS_ENGINEERING
- BLOCKED_EXTERNAL

No `RESEARCH_DONE` status is accepted.
