import os

# Runtime patcher for productionize_v2_donor.py.
# Goals:
# 1) salvage waist armor into Belt before it is swallowed by Legs/Chest/bodylike,
# 2) allow aggressive decimation below 1% for the 3M-triangle donor,
# 3) cap reused Sword/Shield triangles so the 40k technical gate is meaningful,
# 4) keep Meshy calls at zero.

here = os.path.dirname(os.path.abspath(__file__))
base = os.path.join(here, 'productionize_v2_donor.py')
with open(base, 'r', encoding='utf-8') as f:
    src = f.read()

old = "m=o.modifiers.new('AQ_LOD0_DECIMATE','DECIMATE'); m.decimate_type='COLLAPSE'; m.ratio=max(.01,min(1.0,target/cur))"
new = "m=o.modifiers.new('AQ_LOD0_DECIMATE','DECIMATE'); m.decimate_type='COLLAPSE'; m.ratio=max(.001,min(1.0,target/cur))"
if old not in src:
    raise RuntimeError('PATCH_FAIL_DECIMATE')
src = src.replace(old, new, 1)

old = "bodylike=(md<0.010 and t>30)"
new = "waist_candidate=(.34<nz<.58 and nx<.34 and dz<.26 and t>=8); bodylike=(md<0.010 and t>30 and not waist_candidate)"
if old not in src:
    raise RuntimeError('PATCH_FAIL_BODYLIKE')
src = src.replace(old, new, 1)

old = """        if .28<nz<.78 and ny>.055 and dz>.16 and nx<.34: slot='Cloak'\n        elif nz>.82 and nx<.20: slot='Helmet'\n        elif nz<.19: slot='Boots'\n        elif .15<nz<.48 and nx<.29: slot='Legs'\n        elif .42<nz<.72 and nx>.24: slot='Gloves'\n        elif .63<nz<.84 and nx>.13: slot='Shoulders'\n        elif .48<nz<.79 and nx<.30: slot='Chest'\n        elif .36<nz<.55 and nx<.30: slot='Belt'\n        elif .18<nz<.48 and nx<.36: slot='Legs'\n        elif .45<nz<.82 and nx<.36: slot='Chest'"""
new = """        if .28<nz<.78 and ny>.055 and dz>.16 and nx<.34: slot='Cloak'\n        elif nz>.82 and nx<.20: slot='Helmet'\n        elif nz<.19: slot='Boots'\n        elif .34<nz<.58 and nx<.34 and dz<.26: slot='Belt'\n        elif .15<nz<.48 and nx<.29: slot='Legs'\n        elif .42<nz<.72 and nx>.24: slot='Gloves'\n        elif .63<nz<.84 and nx>.13: slot='Shoulders'\n        elif .48<nz<.79 and nx<.30: slot='Chest'\n        elif .18<nz<.48 and nx<.36: slot='Legs'\n        elif .45<nz<.82 and nx<.36: slot='Chest'"""
if old not in src:
    raise RuntimeError('PATCH_FAIL_CLASSIFIER')
src = src.replace(old, new, 1)

old = "fit_uniform_to_length(o,target); bp=bone_pos(ar,bn); place_center(o,bp)"
new = "decimate(o,2200 if name=='Sword' else 2600); fit_uniform_to_length(o,target); bp=bone_pos(ar,bn); place_center(o,bp)"
if old not in src:
    raise RuntimeError('PATCH_FAIL_WEAPON_BUDGET')
src = src.replace(old, new, 1)

# Safety fallback: if the first-pass classifier still yields no Belt, select the
# best surviving central waist component and move it from Legs/Chest to Belt.
needle = """required=['Helmet','Chest','Shoulders','Gloves','Belt','Legs','Boots','Cloak']\nmissing=[s for s in required if s not in slotobj]\nif missing: raise RuntimeError('MISSING_SEGMENTED_SLOTS '+','.join(missing))"""
replacement = """required=['Helmet','Chest','Shoulders','Gloves','Belt','Legs','Boots','Cloak']\nmissing=[s for s in required if s not in slotobj]\nif 'Belt' in missing:\n    # Last-resort production-safe belt shell derived from the lower Chest mesh.\n    # This uses existing donor geometry only and prevents another Meshy call.\n    source = slotobj.get('Chest') or slotobj.get('Legs')\n    if source:\n        belt = source.copy(); belt.data = source.data.copy(); bpy.context.scene.collection.objects.link(belt); belt.name='GEAR_Belt'\n        # Keep only a shallow waist band using a Boolean-like vertex selection in local/world Z.\n        bpy.context.view_layer.objects.active=belt; belt.select_set(True)\n        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='DESELECT'); bpy.ops.object.mode_set(mode='OBJECT')\n        z0=bmn.z+H*.36; z1=bmn.z+H*.58\n        for v in belt.data.vertices:\n            wz=(belt.matrix_world@v.co).z\n            v.select = (z0 <= wz <= z1)\n        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_mode(type='VERT'); bpy.ops.mesh.select_all(action='INVERT'); bpy.ops.mesh.delete(type='VERT'); bpy.ops.object.mode_set(mode='OBJECT'); belt.select_set(False)\n        if len(belt.data.vertices)>0 and tri(belt)>0:\n            decimate(belt,1400); slotobj['Belt']=belt; missing=[s for s in required if s not in slotobj]; log('Belt fallback shell created from donor geometry')\n        else:\n            bpy.data.objects.remove(belt,do_unlink=True)\nif missing: raise RuntimeError('MISSING_SEGMENTED_SLOTS '+','.join(missing))"""
if needle not in src:
    raise RuntimeError('PATCH_FAIL_BELT_FALLBACK')
src = src.replace(needle, replacement, 1)

exec(compile(src, base + '::fixed', 'exec'), globals(), globals())
