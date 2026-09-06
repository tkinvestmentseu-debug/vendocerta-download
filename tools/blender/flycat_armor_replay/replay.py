"""Deterministic FlyCat-derived armor replay for Blender 5.2.

This module intentionally reproduces the observable production logic (explicit shell,
controlled thickness/edge treatment, preserved modularity, rigid-zone skinning QA)
rather than pretending to know hidden FlyCat hotkeys or unpublished values.

Typical invocation:
  blender --background --python replay.py -- \
    --input-blend base.blend --slot GEAR_Chest --out out_dir --budget 5200
"""
from __future__ import annotations

import bpy
import bmesh
import hashlib
import json
import math
import os
import statistics
import sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree

REPLAY_VERSION = "flycat-aetherqor-1.0"


def parse_args() -> dict[str, str]:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    out: dict[str, str] = {}
    i = 0
    while i < len(argv):
        if argv[i].startswith("--"):
            key = argv[i][2:]
            if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
                out[key] = argv[i + 1]
                i += 2
                continue
            out[key] = "true"
        i += 1
    return out


def log(msg: str) -> None:
    print(f"[FLYCAT-REPLAY] {msg}", flush=True)


def tri_count(obj: bpy.types.Object) -> int:
    if obj.type != "MESH":
        return 0
    return sum(max(0, len(p.vertices) - 2) for p in obj.data.polygons)


def bbox_world(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


def combined_bbox(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    pts: list[Vector] = []
    for obj in objects:
        if obj.type == "MESH":
            pts.extend(obj.matrix_world @ Vector(c) for c in obj.bound_box)
    if not pts:
        raise RuntimeError("NO_MESH_FOR_BBOX")
    return (
        Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
        Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))),
    )


def find_body() -> bpy.types.Object:
    exact = bpy.data.objects.get("BODY_BASE")
    if exact and exact.type == "MESH":
        return exact
    candidates = [o for o in bpy.data.objects if o.type == "MESH" and "body" in o.name.lower()]
    if not candidates:
        raise RuntimeError("BODY_NOT_FOUND")
    return max(candidates, key=tri_count)


def find_armature() -> bpy.types.Object:
    exact = bpy.data.objects.get("ARMATURE_AETHERQOR_HUMANOID")
    if exact and exact.type == "ARMATURE":
        return exact
    candidates = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if not candidates:
        raise RuntimeError("ARMATURE_NOT_FOUND")
    return max(candidates, key=lambda o: len(o.data.bones))


def clean_mesh(obj: bpy.types.Object, merge_distance: float) -> dict[str, int]:
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    before_v = len(bm.verts)
    before_f = len(bm.faces)
    if bm.verts:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge_distance)
    if bm.faces:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.validate(verbose=False, clean_customdata=False)
    mesh.update(calc_edges=True)
    return {
        "verts_before": before_v,
        "verts_after": len(mesh.vertices),
        "faces_before": before_f,
        "faces_after": len(mesh.polygons),
    }


def topology_stats(obj: bpy.types.Object) -> dict[str, float | int | bool]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    boundary = sum(1 for e in bm.edges if e.is_boundary)
    nonmanifold = sum(1 for e in bm.edges if not e.is_manifold)
    loose = sum(1 for v in bm.verts if len(v.link_edges) == 0)
    volume = None
    try:
        if nonmanifold == 0 and bm.faces:
            volume = abs(float(bm.calc_volume(signed=False)))
    except Exception:
        volume = None
    stats = {
        "boundary_edges": boundary,
        "nonmanifold_edges": nonmanifold,
        "loose_vertices": loose,
        "watertight": bool(nonmanifold == 0 and len(bm.faces) > 0),
        "volume": volume,
    }
    bm.free()
    return stats


def apply_modifier(obj: bpy.types.Object, modifier: bpy.types.Modifier) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    try:
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    finally:
        obj.select_set(False)


def controlled_finish(obj: bpy.types.Object, body_height: float, budget: int) -> dict[str, object]:
    """Apply conservative thickness/edge treatment without remeshing away authored boundaries."""
    before_tri = tri_count(obj)
    topo_before = topology_stats(obj)
    actions: list[dict[str, object]] = []

    # Only add shell thickness when the source behaves like an open surface.
    # Existing closed donor plates keep their authored thickness untouched.
    boundary_ratio = topo_before["boundary_edges"] / max(1, len(obj.data.edges))
    if (not topo_before["watertight"]) and boundary_ratio > 0.002:
        backup = obj.data.copy()
        mod = obj.modifiers.new("FLYCAT_ControlledThickness", "SOLIDIFY")
        mod.thickness = body_height * 0.0016
        mod.offset = 0.0
        mod.use_even_offset = True
        mod.use_quality_normals = True
        apply_modifier(obj, mod)
        after = tri_count(obj)
        accepted = after <= max(int(budget * 1.15), int(before_tri * 1.35))
        if not accepted:
            old = obj.data
            obj.data = backup
            bpy.data.meshes.remove(old)
        else:
            bpy.data.meshes.remove(backup)
        actions.append({"operation": "controlled_thickness", "accepted": accepted, "triangles": tri_count(obj)})

    # Micro bevel is deliberately tiny. It exists to preserve a readable highlight,
    # not to manufacture form or smooth away plate boundaries.
    bevel_backup = obj.data.copy()
    pre_bevel = tri_count(obj)
    bevel = obj.modifiers.new("FLYCAT_MacroEdgeHighlight", "BEVEL")
    bevel.width = body_height * 0.00075
    bevel.segments = 2
    bevel.limit_method = "ANGLE"
    bevel.angle_limit = math.radians(58.0)
    bevel.harden_normals = True
    try:
        apply_modifier(obj, bevel)
        post_bevel = tri_count(obj)
        accepted = post_bevel <= max(int(budget * 1.15), int(pre_bevel * 1.28))
    except Exception as exc:
        log(f"bevel failed conservatively: {exc}")
        accepted = False
    if not accepted:
        if obj.modifiers.get("FLYCAT_MacroEdgeHighlight"):
            obj.modifiers.remove(obj.modifiers["FLYCAT_MacroEdgeHighlight"])
        old = obj.data
        obj.data = bevel_backup
        bpy.data.meshes.remove(old)
    else:
        bpy.data.meshes.remove(bevel_backup)
    actions.append({"operation": "macro_edge_highlight", "accepted": accepted, "triangles": tri_count(obj)})

    return {
        "triangles_before_finish": before_tri,
        "triangles_after_finish": tri_count(obj),
        "topology_before_finish": topo_before,
        "topology_after_finish": topology_stats(obj),
        "actions": actions,
    }


def mesh_signature(obj: bpy.types.Object) -> str:
    h = hashlib.sha256()
    h.update(REPLAY_VERSION.encode("ascii"))
    for v in obj.data.vertices:
        h.update((f"{v.co.x:.7f},{v.co.y:.7f},{v.co.z:.7f};").encode("ascii"))
        # Vertex weights are part of deterministic replay state.
        groups = sorted((g.group, round(float(g.weight), 7)) for g in v.groups)
        h.update(repr(groups).encode("ascii"))
    for p in obj.data.polygons:
        h.update((",".join(str(i) for i in p.vertices) + ";").encode("ascii"))
    return h.hexdigest()


def evaluated_points(obj: bpy.types.Object, depsgraph: bpy.types.Depsgraph, max_points: int = 2200) -> list[Vector]:
    ev = obj.evaluated_get(depsgraph)
    mesh = ev.to_mesh()
    try:
        verts = mesh.vertices
        step = max(1, len(verts) // max_points)
        return [ev.matrix_world @ verts[i].co for i in range(0, len(verts), step)][:max_points]
    finally:
        ev.to_mesh_clear()


def penetration_metrics(gear: bpy.types.Object, body: bpy.types.Object) -> dict[str, object]:
    deps = bpy.context.evaluated_depsgraph_get()
    bpy.context.view_layer.update()
    bvh = BVHTree.FromObject(body, deps, epsilon=0.0)
    signed: list[float] = []
    points = evaluated_points(gear, deps)
    for p in points:
        hit = bvh.find_nearest(p)
        if not hit or hit[0] is None or hit[1] is None:
            continue
        loc, normal, _index, _distance = hit
        signed.append(float((p - loc).dot(normal)))
    eps = 0.00035
    inside = [d for d in signed if d < -eps]
    near = [d for d in signed if abs(d) <= eps]
    return {
        "samples": len(signed),
        "inside_body_samples": len(inside),
        "near_surface_samples": len(near),
        "inside_fraction": (len(inside) / len(signed)) if signed else None,
        "signed_clearance_min_m": min(signed) if signed else None,
        "signed_clearance_median_m": statistics.median(signed) if signed else None,
        "method": "nearest_surface_normal_signed_distance_proxy",
        "epsilon_m": eps,
    }


def pose_test(gear: bpy.types.Object, body: bpy.types.Object, armature: bpy.types.Object) -> dict[str, object]:
    candidates = [
        ("spine", ("spine2", "chest", "spine1", "spine"), (0.0, 0.0, math.radians(14))),
        ("upperarm_l", ("upperarm_l", "upperarm.l", "leftarm", "arm_l"), (math.radians(24), 0.0, 0.0)),
        ("upperarm_r", ("upperarm_r", "upperarm.r", "rightarm", "arm_r"), (-math.radians(24), 0.0, 0.0)),
    ]
    saved: dict[str, object] = {}
    applied: list[str] = []
    names = list(armature.pose.bones.keys())
    try:
        for label, tokens, rot in candidates:
            bone = None
            for token in tokens:
                compact = token.lower().replace("_", "").replace(".", "")
                bone = next((b for b in armature.pose.bones if compact in b.name.lower().replace("_", "").replace(".", "")), None)
                if bone:
                    break
            if not bone:
                continue
            saved[bone.name] = bone.matrix_basis.copy()
            bone.rotation_mode = "XYZ"
            bone.rotation_euler.rotate_axis("X", rot[0]) if rot[0] else None
            bone.rotation_euler.rotate_axis("Y", rot[1]) if rot[1] else None
            bone.rotation_euler.rotate_axis("Z", rot[2]) if rot[2] else None
            applied.append(f"{label}:{bone.name}")
        bpy.context.view_layer.update()
        metrics = penetration_metrics(gear, body)
        metrics["applied_bones"] = applied
        metrics["pose_kind"] = "procedural_non_bind_stress_pose"
        return metrics
    finally:
        for name, matrix_basis in saved.items():
            armature.pose.bones[name].matrix_basis = matrix_basis
        bpy.context.view_layer.update()


def weighted_coverage(obj: bpy.types.Object) -> dict[str, object]:
    weighted = 0
    max_influences = 0
    for v in obj.data.vertices:
        influences = [g for g in v.groups if g.weight > 1e-6]
        if influences:
            weighted += 1
        max_influences = max(max_influences, len(influences))
    arm_mods = [m for m in obj.modifiers if m.type == "ARMATURE"]
    return {
        "vertex_groups": len(obj.vertex_groups),
        "weighted_vertices": weighted,
        "total_vertices": len(obj.data.vertices),
        "weighted_fraction": weighted / max(1, len(obj.data.vertices)),
        "max_influences_observed": max_influences,
        "armature_modifiers": len(arm_mods),
        "parent_is_armature": bool(obj.parent and obj.parent.type == "ARMATURE"),
    }


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def ensure_camera_and_light(center: Vector, height: float) -> tuple[bpy.types.Object, bpy.types.Object]:
    cam_data = bpy.data.cameras.get("FLYCAT_QA_Camera") or bpy.data.cameras.new("FLYCAT_QA_Camera")
    cam = bpy.data.objects.get("FLYCAT_QA_Camera") or bpy.data.objects.new("FLYCAT_QA_Camera", cam_data)
    if cam.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    cam.location = (center.x, center.y - height * 3.0, center.z)
    look_at(cam, center)
    bpy.context.scene.camera = cam

    light_data = bpy.data.lights.get("FLYCAT_QA_Light") or bpy.data.lights.new("FLYCAT_QA_Light", "AREA")
    light = bpy.data.objects.get("FLYCAT_QA_Light") or bpy.data.objects.new("FLYCAT_QA_Light", light_data)
    if light.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(light)
    light.data.energy = 1000
    light.data.shape = "DISK"
    light.data.size = height * 2.0
    light.location = (center.x + height, center.y - height * 1.5, center.z + height)
    look_at(light, center)
    return cam, light


def alpha_mask() -> tuple[list[bool], int, int]:
    image = bpy.data.images.get("Render Result")
    if image is None:
        raise RuntimeError("NO_RENDER_RESULT")
    w, h = image.size
    px = list(image.pixels)
    return ([px[i] > 0.05 for i in range(3, len(px), 4)], w, h)


def mask_metrics(mask: list[bool], w: int, h: int) -> dict[str, object]:
    idx = [i for i, v in enumerate(mask) if v]
    if not idx:
        return {"visible_pixels": 0, "bbox_width_px": 0, "bbox_height_px": 0, "perimeter_pixels": 0, "edge_density": None}
    xs = [i % w for i in idx]
    ys = [i // w for i in idx]
    perimeter = 0
    for i in idx:
        x, y = i % w, i // w
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if nx < 0 or nx >= w or ny < 0 or ny >= h or not mask[ny * w + nx]:
                perimeter += 1
                break
    area = len(idx)
    return {
        "visible_pixels": area,
        "bbox_width_px": max(xs) - min(xs) + 1,
        "bbox_height_px": max(ys) - min(ys) + 1,
        "perimeter_pixels": perimeter,
        "edge_density": perimeter / max(1, area),
    }


def render_mask(obj: bpy.types.Object, body_height: float, body_center: Vector, target_px: int, path: str) -> tuple[list[bool], int, int, dict[str, object]]:
    scene = bpy.context.scene
    cam, _light = ensure_camera_and_light(body_center, body_height)
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = True
    cam.data.ortho_scale = body_height * 512.0 / max(1, target_px)

    visible_state = {o.name: o.hide_render for o in bpy.data.objects}
    for o in bpy.data.objects:
        if o.type == "MESH":
            o.hide_render = (o != obj)
    obj.hide_render = False
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    mask, w, h = alpha_mask()
    for name, hidden in visible_state.items():
        if name in bpy.data.objects:
            bpy.data.objects[name].hide_render = hidden
    return mask, w, h, mask_metrics(mask, w, h)


def mask_iou(a: list[bool], b: list[bool]) -> float | None:
    if len(a) != len(b):
        return None
    inter = sum(1 for x, y in zip(a, b) if x and y)
    union = sum(1 for x, y in zip(a, b) if x or y)
    return inter / union if union else None


def screen_space_qa(replay: bpy.types.Object, donor: bpy.types.Object, body: bpy.types.Object, out: str) -> dict[str, object]:
    bmn, bmx = bbox_world(body)
    height = bmx.z - bmn.z
    center = (bmn + bmx) * 0.5
    renders = os.path.join(out, "renders")
    os.makedirs(renders, exist_ok=True)
    result: dict[str, object] = {}
    baseline_edge_density = None
    for target in (90, 150, 220, 300):
        _mask, _w, _h, metrics = render_mask(replay, height, center, target, os.path.join(renders, f"replay_{target}px.png"))
        result[str(target)] = metrics
        if target == 300:
            baseline_edge_density = metrics.get("edge_density")
    if baseline_edge_density:
        for target in (90, 150, 220, 300):
            m = result[str(target)]
            ed = m.get("edge_density")
            m["macro_edge_survival_proxy"] = bool(m.get("visible_pixels", 0) >= 20 and ed is not None and ed <= baseline_edge_density * 3.5)
            m["faceting_proxy"] = "PASS" if m["macro_edge_survival_proxy"] else "REVIEW"
        
    donor_mask, _, _, donor_m = render_mask(donor, height, center, 300, os.path.join(renders, "donor_300px.png"))
    replay_mask, _, _, replay_m = render_mask(replay, height, center, 300, os.path.join(renders, "replay_compare_300px.png"))
    return {
        "targets": result,
        "donor_300px": donor_m,
        "replay_300px": replay_m,
        "projected_silhouette_iou_300px": mask_iou(donor_mask, replay_mask),
        "proxy_note": "Macro-edge/faceting values are automatic screen-space proxies; renders remain the visual evidence.",
    }


def export_selection(body: bpy.types.Object, gear: bpy.types.Object, armature: bpy.types.Object, out: str) -> dict[str, str]:
    os.makedirs(out, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in (body, gear, armature):
        obj.hide_viewport = False
        obj.hide_render = False
        obj.select_set(True)
    bpy.context.view_layer.objects.active = armature
    fbx = os.path.join(out, "FlyCat_Chest_Pilot.fbx")
    bpy.ops.export_scene.fbx(
        filepath=fbx,
        use_selection=True,
        add_leaf_bones=False,
        bake_anim=False,
        apply_unit_scale=True,
        use_mesh_modifiers=True,
    )
    blend = os.path.join(out, "FlyCat_Chest_Pilot.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    return {"fbx": fbx, "blend": blend}


def main() -> None:
    args = parse_args()
    input_blend = os.path.abspath(args.get("input-blend", ""))
    out = os.path.abspath(args.get("out", "flycat_replay_out"))
    slot_name = args.get("slot", "GEAR_Chest")
    budget = int(args.get("budget", "5200"))
    if not os.path.isfile(input_blend):
        raise RuntimeError(f"INPUT_BLEND_MISSING {input_blend}")
    os.makedirs(out, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=input_blend)

    donor = bpy.data.objects.get(slot_name)
    if donor is None or donor.type != "MESH":
        raise RuntimeError(f"SLOT_NOT_FOUND {slot_name}")
    body = find_body()
    armature = find_armature()
    bmn, bmx = bbox_world(body)
    height = float(bmx.z - bmn.z)
    if not 1.0 <= height <= 2.5:
        raise RuntimeError(f"BODY_HEIGHT_INVALID {height}")

    replay = donor.copy()
    replay.data = donor.data.copy()
    bpy.context.scene.collection.objects.link(replay)
    replay.name = "FLYCAT_Chest_Pilot"
    replay["flycat_replay_version"] = REPLAY_VERSION
    replay["flycat_source_object"] = donor.name
    replay["flycat_method"] = "explicit_boundary_then_controlled_finish"

    clean = clean_mesh(replay, merge_distance=height * 1e-7)
    finish = controlled_finish(replay, height, budget)
    replay.data.update()
    bpy.context.view_layer.update()

    # Keep source as evidence but never let it contaminate output renders/exports.
    donor.hide_viewport = True
    donor.hide_render = True

    bind_pen = penetration_metrics(replay, body)
    pose_pen = pose_test(replay, body, armature)
    rig = weighted_coverage(replay)
    screen = screen_space_qa(replay, donor, body, out)
    signature = mesh_signature(replay)
    export = export_selection(body, replay, armature, out)

    results = {
        "schema": 1,
        "replay_version": REPLAY_VERSION,
        "status": "MEASURED",
        "input_blend": input_blend,
        "source_slot": slot_name,
        "output_object": replay.name,
        "body_height_m": height,
        "triangle_budget": budget,
        "triangles_source": tri_count(donor),
        "triangles_replay": tri_count(replay),
        "clean": clean,
        "finish": finish,
        "rig": rig,
        "bind_pose_penetration": bind_pen,
        "stress_pose_penetration": pose_pen,
        "screen_space": screen,
        "mesh_signature": signature,
        "exports": export,
        "methodology": {
            "source_command_parity": "not_claimed",
            "geometry_intent": "FlyCat evidence-derived",
            "remesh_used": False,
            "plate_boundaries_preserved": True,
            "modular_slot_preserved": True,
        },
    }
    with open(os.path.join(out, "blender_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    log(f"DONE signature={signature} tris={tri_count(replay)}")


if __name__ == "__main__":
    main()
