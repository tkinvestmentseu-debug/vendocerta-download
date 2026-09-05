import bpy, sys, os, json, math
from mathutils import Vector, Matrix

# ---------- args ----------
argv = sys.argv
argv = argv[argv.index('--')+1:] if '--' in argv else []
args = {}
for i in range(0, len(argv)-1, 2):
    if argv[i].startswith('--'): args[argv[i][2:]] = argv[i+1]
INPUT = os.path.abspath(args.get('input', '.'))
OUTPUT = os.path.abspath(args.get('output', './out'))
os.makedirs(OUTPUT, exist_ok=True)
os.makedirs(os.path.join(OUTPUT,'renders'), exist_ok=True)
os.makedirs(os.path.join(OUTPUT,'reports'), exist_ok=True)

# ---------- utils ----------
def log(s):
    print('[RW-ASSEMBLY]', s, flush=True)

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.armatures, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        pass

def import_glb(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    after = [o for o in bpy.data.objects if o not in before]
    return after

def meshes(objs): return [o for o in objs if o.type == 'MESH']

def world_bbox(objs):
    pts=[]
    for o in objs:
        if o.type!='MESH': continue
        for c in o.bound_box: pts.append(o.matrix_world @ Vector(c))
    if not pts: return Vector((0,0,0)),Vector((1,1,1))
    mn=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    mx=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    return mn,mx

def bbox_dims(objs):
    mn,mx=world_bbox(objs); return mx-mn

def bbox_center(objs):
    mn,mx=world_bbox(objs); return (mn+mx)*0.5

def transform_group(objs, scale=(1,1,1), delta=(0,0,0)):
    c=bbox_center(objs)
    sx,sy,sz=scale
    for o in objs:
        if o.type not in {'MESH','EMPTY'}: continue
        mw=o.matrix_world.copy()
        loc=mw.translation
        rel=loc-c
        rel=Vector((rel.x*sx,rel.y*sy,rel.z*sz))
        o.scale.x*=sx; o.scale.y*=sy; o.scale.z*=sz
        o.location = c + rel + Vector(delta)

def fit_group_to_box(objs, center, dims, uniform=False, max_scale=100):
    cur=bbox_dims(objs)
    eps=1e-5
    scales=[dims[i]/max(cur[i],eps) for i in range(3)]
    if uniform:
        s=min(scales); scales=[s,s,s]
    scales=[min(max(s,0.001),max_scale) for s in scales]
    transform_group(objs, scales, (0,0,0))
    newc=bbox_center(objs)
    d=Vector(center)-newc
    for o in objs: o.location += d

def largest_body_mesh(objs):
    ms=meshes(objs)
    if not ms: return None
    return max(ms,key=lambda o: len(o.data.polygons))

def find_armature(objs):
    arms=[o for o in objs if o.type=='ARMATURE']
    return max(arms,key=lambda o:len(o.data.bones)) if arms else None

def all_world_vertices(obj):
    if obj.type!='MESH': return []
    return [obj.matrix_world @ v.co for v in obj.data.vertices]

def slice_dims(body,z0,z1,x_limit=None):
    vs=all_world_vertices(body)
    mn,mx=world_bbox([body]); H=mx.z-mn.z; cx=(mn.x+mx.x)/2
    pts=[]
    for p in vs:
        nz=(p.z-mn.z)/max(H,1e-6)
        if z0<=nz<=z1 and (x_limit is None or abs(p.x-cx)<=x_limit*H): pts.append(p)
    if not pts: return (max((mx.x-mn.x)*.25,.1), max((mx.y-mn.y),.08))
    return (max(p.x for p in pts)-min(p.x for p in pts), max(p.y for p in pts)-min(p.y for p in pts))

def bone_name(arm,*tokens):
    if not arm: return None
    names=[b.name for b in arm.data.bones]
    low={n:n.lower().replace('_','').replace('.','') for n in names}
    for t in tokens:
        tt=t.lower().replace('_','').replace('.','')
        for n,s in low.items():
            if tt in s: return n
    return None

def bone_pos(arm,name):
    if not arm or not name: return None
    b=arm.pose.bones.get(name)
    if not b:return None
    return arm.matrix_world @ b.head

def parent_keep_world(obj,parent,bone=None):
    mw=obj.matrix_world.copy()
    obj.parent=parent
    if bone:
        obj.parent_type='BONE'; obj.parent_bone=bone
    obj.matrix_world=mw

def weight_transfer(obj,body,arm):
    if obj.type!='MESH' or body is None or arm is None:return False
    try:
        for vg in list(obj.vertex_groups): obj.vertex_groups.remove(vg)
        mod=obj.modifiers.new('AQ_WeightTransfer','DATA_TRANSFER')
        mod.object=body
        mod.use_vert_data=True
        mod.data_types_verts={'VGROUP_WEIGHTS'}
        mod.vert_mapping='POLYINTERP_NEAREST'
        bpy.context.view_layer.objects.active=obj; obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier=mod.name)
        obj.select_set(False)
        am=obj.modifiers.new('AQ_Armature','ARMATURE'); am.object=arm
        return True
    except Exception as e:
        log(f'weight transfer failed {obj.name}: {e}')
        return False

def set_slot_names(objs,slot):
    idx=0
    for o in objs:
        if o.type=='MESH':
            o.name=f'GEAR_{slot}_{idx:02d}'; idx+=1

def create_socket(arm,name,bone):
    e=bpy.data.objects.new(name,None); bpy.context.scene.collection.objects.link(e)
    e.empty_display_type='PLAIN_AXES'; e.empty_display_size=.06
    if arm and bone: parent_keep_world(e,arm,bone)
    return e

def get_existing_glb(name):
    p=os.path.join(INPUT,name+'.glb')
    return p if os.path.isfile(p) else None

# ---------- body / RIG HARD GATE ----------
clear_scene()
body_path=get_existing_glb('Body_Rigged')
if not body_path:
    raise RuntimeError('RIG_REQUIRED: Body_Rigged.glb missing. Refusing to build an unrigged final character.')
body_objs=import_glb(body_path)
arm=find_armature(body_objs); body=largest_body_mesh(body_objs)
if body is None: raise RuntimeError('No body mesh imported')
if arm is None: raise RuntimeError('RIG_REQUIRED: no Armature object in Body_Rigged.glb')
if len(arm.data.bones) < 15: raise RuntimeError(f'RIG_REQUIRED: suspiciously small skeleton ({len(arm.data.bones)} bones)')
body.name='BODY_BASE'
arm.name='ARMATURE_AETHERQOR_HUMANOID'
mn,mx=world_bbox([body]); H=mx.z-mn.z; cx=(mn.x+mx.x)/2; cy=(mn.y+mx.y)/2
if H<=0: raise RuntimeError('Invalid body height')
scale=1.78/H
if abs(scale-1)>0.01:
    roots=[o for o in body_objs if o.parent is None]
    for o in roots: o.scale*=scale
    bpy.context.view_layer.update(); mn,mx=world_bbox([body]); H=mx.z-mn.z; cx=(mn.x+mx.x)/2; cy=(mn.y+mx.y)/2

torsoW,torsoD=slice_dims(body,.55,.76,.23)
waistW,waistD=slice_dims(body,.45,.58,.20)
headW,headD=slice_dims(body,.84,.99,.15)
pelvisW,pelvisD=slice_dims(body,.38,.52,.20)
footW,footD=slice_dims(body,.0,.13,.22)

# rig heuristics
rhand=bone_name(arm,'righthand','handr','rhand','hand.r','hand_r')
lhand=bone_name(arm,'lefthand','handl','lhand','hand.l','hand_l')
headbone=bone_name(arm,'head')
neckbone=bone_name(arm,'neck')
spinebone=bone_name(arm,'spine2','spine02','spine1','spine01','chest','spine')
hipbone=bone_name(arm,'hips','pelvis','root')
rp=bone_pos(arm,rhand); lp=bone_pos(arm,lhand)
if rp is None: rp=Vector((cx+H*.34,cy,mn.z+H*.54))
if lp is None: lp=Vector((cx-H*.34,cy,mn.z+H*.54))

# ---------- gameplay gear targets ----------
T={
 'Helmet':((cx,cy,mn.z+H*.91),(headW*1.35,headD*1.45,H*.16),'skin'),
 'ChestArmor':((cx,cy,mn.z+H*.66),(torsoW*1.16,torsoD*1.55,H*.27),'skin'),
 'Shoulders':((cx,cy,mn.z+H*.74),(torsoW*1.55,torsoD*1.42,H*.13),'skin'),
 'Gloves':(((rp+lp)*.5),(abs(rp.x-lp.x)+H*.16,H*.12,H*.16),'skin'),
 'Belt':((cx,cy,mn.z+H*.50),(waistW*1.23,waistD*1.45,H*.07),'skin'),
 'Legs':((cx,cy,mn.z+H*.36),(pelvisW*1.20,pelvisD*1.45,H*.30),'skin'),
 'Boots':((cx,cy,mn.z+H*.10),(max(footW*1.25,H*.26),max(footD*1.35,H*.14),H*.20),'skin'),
 'Cloak':((cx,cy+torsoD*.82,mn.z+H*.54),(torsoW*1.25,H*.055,H*.56),'skin'),
 'Sword':((rp.x,rp.y,mn.z+H*.43),(H*.07,H*.055,H*.76),'rhand'),
 'Shield':((lp.x,lp.y,mn.z+H*.57),(H*.31,H*.08,H*.44),'lhand'),
 'ClassRelic':((cx,cy-torsoD*.82,mn.z+H*.67),(H*.09,H*.035,H*.12),'spine')
}

slot_objects={}
for slot,(center,dims,mode) in T.items():
    p=get_existing_glb(slot)
    if not p:
        log(f'MISSING {slot}.glb'); continue
    added=import_glb(p); ms=meshes(added)
    if not ms:
        log(f'NO MESH {slot}'); continue
    set_slot_names(ms,slot)
    fit_group_to_box(ms,Vector(center),Vector(dims),uniform=False)
    bpy.context.view_layer.update()
    if mode=='skin':
        for o in ms: weight_transfer(o,body,arm)
    else:
        b={'rhand':rhand,'lhand':lhand,'spine':spinebone}.get(mode)
        for o in ms:
            if arm and b: parent_keep_world(o,arm,b)
    slot_objects[slot]=ms

# sockets
sockets={}
for nm,b in [('Socket_RightHand',rhand),('Socket_LeftHand',lhand),('Socket_BackWeapon',spinebone),('Socket_BackShield',spinebone),('Socket_Head',headbone),('Socket_Neck',neckbone),('Socket_Hips',hipbone)]:
    sockets[nm]=create_socket(arm,nm,b)

# attach weapon/shield under explicit sockets
for slot,sock in [('Sword','Socket_RightHand'),('Shield','Socket_LeftHand')]:
    for o in slot_objects.get(slot,[]): parent_keep_world(o,sockets[sock])

# Collections
for name in ['BODY','GEAR','WEAPONS','SOCKETS']:
    if name not in bpy.data.collections:
        c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)

def move_to_collection(obj,cname):
    c=bpy.data.collections[cname]
    for oc in list(obj.users_collection): oc.objects.unlink(obj)
    c.objects.link(obj)
for o in body_objs:
    if o.name in bpy.data.objects: move_to_collection(o,'BODY')
for slot,obs in slot_objects.items():
    cname='WEAPONS' if slot in ('Sword','Shield') else 'GEAR'
    for o in obs: move_to_collection(o,cname)
for o in sockets.values(): move_to_collection(o,'SOCKETS')

# ---------- QA ----------
def tri_count_obj(o):
    if o.type!='MESH': return 0
    return sum(max(0,len(p.vertices)-2) for p in o.data.polygons)
qa={
 'body_height_m':H,
 'rig_required':True,
 'rig_present':arm is not None,
 'armature':arm.name if arm else None,
 'bones':len(arm.data.bones) if arm else 0,
 'body_vertices':len(body.data.vertices),
 'body_triangles':tri_count_obj(body),
 'slots':{},
 'sockets':list(sockets),
 'materials':len({m.name for o in bpy.data.objects if o.type=='MESH' for m in o.data.materials if m}),
 'jewelry_generated_or_expected':False,
}
for slot,obs in slot_objects.items():
    qa['slots'][slot]={'objects':len(obs),'triangles':sum(tri_count_obj(o) for o in obs),'vertices':sum(len(o.data.vertices) for o in obs)}
qa['total_triangles']=sum(tri_count_obj(o) for o in bpy.data.objects if o.type=='MESH')
qa['missing_slots']=[s for s in T if s not in slot_objects]
with open(os.path.join(OUTPUT,'reports','assembly_qa.json'),'w',encoding='utf8') as f: json.dump(qa,f,indent=2,ensure_ascii=False)

manifest={'character':'AETHERQOR_RUNIC_WARDEN_FULL_MALE_V1','requirement':'RIGGED_CHARACTER_WITH_MODULAR_GAMEPLAY_GEAR','input_dir':INPUT,'slots':list(slot_objects),'missing':qa['missing_slots'],'sockets':list(sockets),'armature':arm.name,'bones':len(arm.data.bones),'blender':bpy.app.version_string}
with open(os.path.join(OUTPUT,'AETHERQOR_RUNIC_WARDEN_FULL_MALE_V1_MANIFEST.json'),'w',encoding='utf8') as f: json.dump(manifest,f,indent=2)

# ---------- render ----------
def look_at(obj, target):
    direction=Vector(target)-obj.location
    obj.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()

bpy.ops.mesh.primitive_plane_add(size=8, location=(cx,cy,mn.z-.005)); floor=bpy.context.object; floor.name='QA_Floor'
mat=bpy.data.materials.new('QA_Floor_Mat'); mat.diffuse_color=(0.035,0.035,0.035,1); floor.data.materials.append(mat)
for loc,energy,size in [((cx-H*.8,cy-H*1.1,mn.z+H*1.25),1300,4),((cx+H*.8,cy-H*.6,mn.z+H*.9),900,3),((cx,cy+H*.8,mn.z+H*1.1),1100,3)]:
    ld=bpy.data.lights.new('QA_Area','AREA'); ld.energy=energy; ld.shape='DISK'; ld.size=size
    lo=bpy.data.objects.new('QA_Area',ld); bpy.context.scene.collection.objects.link(lo); lo.location=loc; look_at(lo,(cx,cy,mn.z+H*.55))
camd=bpy.data.cameras.new('QA_Camera'); cam=bpy.data.objects.new('QA_Camera',camd); bpy.context.scene.collection.objects.link(cam); bpy.context.scene.camera=cam
camd.lens=58
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE_NEXT'; scene.render.resolution_x=1024; scene.render.resolution_y=1024; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.world.color=(0.018,0.018,0.018)
for name,loc in [('front',(cx,cy-H*2.35,mn.z+H*.57)),('three_quarter',(cx+H*1.45,cy-H*1.85,mn.z+H*.62)),('back',(cx,cy+H*2.35,mn.z+H*.57))]:
    cam.location=loc; look_at(cam,(cx,cy,mn.z+H*.53)); scene.render.filepath=os.path.join(OUTPUT,'renders',name+'.png')
    try: bpy.ops.render.render(write_still=True)
    except Exception as e: log(f'render {name} failed: {e}')

for o in [floor,cam]+[o for o in bpy.data.objects if o.name.startswith('QA_Area')]: o.hide_render=True

# ---------- save/export ----------
blend=os.path.join(OUTPUT,'AETHERQOR_RUNIC_WARDEN_FULL_MALE_V1.blend')
bpy.ops.wm.save_as_mainfile(filepath=blend)

def export_pair(suffix):
    glb=os.path.join(OUTPUT,f'AETHERQOR_RUNIC_WARDEN_FULL_MALE_V1_{suffix}.glb')
    fbx=os.path.join(OUTPUT,f'AETHERQOR_RUNIC_WARDEN_FULL_MALE_V1_{suffix}.fbx')
    bpy.ops.export_scene.gltf(filepath=glb,export_format='GLB',export_apply=True,export_animations=True)
    bpy.ops.export_scene.fbx(filepath=fbx,use_selection=False,add_leaf_bones=False,bake_anim=True,apply_scale_options='FBX_SCALE_ALL')

export_pair('LOD0')
for ratio,label in [(0.58,'LOD1'),(0.52,'LOD2')]:
    for o in [x for x in bpy.data.objects if x.type=='MESH' and not x.name.startswith('QA_')]:
        if len(o.data.polygons)<100: continue
        mod=o.modifiers.new(f'AQ_Decimate_{label}','DECIMATE'); mod.ratio=ratio
        try:
            bpy.context.view_layer.objects.active=o; o.select_set(True); bpy.ops.object.modifier_apply(modifier=mod.name); o.select_set(False)
        except Exception as e: log(f'decimate failed {o.name}: {e}')
    export_pair(label)

import shutil
shutil.copy2(os.path.join(OUTPUT,'AETHERQOR_RUNIC_WARDEN_FULL_MALE_V1_LOD0.glb'),os.path.join(OUTPUT,'AETHERQOR_RUNIC_WARDEN_FULL_MALE_V1.glb'))
shutil.copy2(os.path.join(OUTPUT,'AETHERQOR_RUNIC_WARDEN_FULL_MALE_V1_LOD0.fbx'),os.path.join(OUTPUT,'AETHERQOR_RUNIC_WARDEN_FULL_MALE_V1.fbx'))
log('ASSEMBLY_DONE_RIGGED')
