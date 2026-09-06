import bpy, sys, os, json, math, bmesh
from mathutils import Vector

argv=sys.argv
argv=argv[argv.index('--')+1:] if '--' in argv else []
args={}
for i in range(0,len(argv)-1,2):
    if argv[i].startswith('--'): args[argv[i][2:]]=argv[i+1]
MASTER=os.path.abspath(args.get('master','.'))
BODY_PATH=os.path.abspath(args.get('body',''))
OUT=os.path.abspath(args.get('out','./out'))
os.makedirs(OUT,exist_ok=True); os.makedirs(os.path.join(OUT,'renders'),exist_ok=True); os.makedirs(os.path.join(OUT,'reports'),exist_ok=True)

SLOTS=['Helmet','Chest','Shoulders','Gloves','Belt','Legs','Boots','Cloak','Sword','Shield','ClassRelic']

def log(x): print('[RW-V3-STATIC-REPAIR-V4]',x,flush=True)
def clear(): bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def import_glb(path):
    before=set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]
def meshes(obs): return [o for o in obs if o.type=='MESH']
def largest_mesh(obs):
    ms=meshes(obs); return max(ms,key=lambda o:len(o.data.polygons)) if ms else None
def find_arm(obs):
    ar=[o for o in obs if o.type=='ARMATURE']; return max(ar,key=lambda o:len(o.data.bones)) if ar else None
def bbox(obs):
    pts=[]
    for o in obs:
        if o.type!='MESH': continue
        pts.extend([o.matrix_world @ Vector(c) for c in o.bound_box])
    if not pts: return Vector((0,0,0)),Vector((1,1,1))
    mn=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    mx=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    return mn,mx
def center(obs):
    a,b=bbox(obs); return (a+b)*0.5
def dims(obs):
    a,b=bbox(obs); return b-a
def apply_uniform(obs,s):
    c=center(obs)
    for o in obs:
        if o.type!='MESH': continue
        rel=o.location-c; o.location=c+rel*s; o.scale*=s
    bpy.context.view_layer.update()
def move_center(obs,target):
    d=Vector(target)-center(obs)
    for o in obs:
        if o.type=='MESH': o.location+=d
    bpy.context.view_layer.update()
def fit_height(obs,target_center,target_h):
    cur=max(dims(obs).z,1e-6); s=target_h/cur
    if not 0.02<=s<=20: raise RuntimeError(f'unsafe uniform scale {s}')
    apply_uniform(obs,s); move_center(obs,target_center); return s
def fit_height_min_width(obs,target_center,target_h,min_w):
    s=fit_height(obs,target_center,target_h)
    w=max(dims(obs).x,1e-6)
    if w < min_w:
        extra=min_w/w
        if extra>1.45: extra=1.45
        apply_uniform(obs,extra); move_center(obs,target_center); s*=extra
    return s
def rename(obs,slot,side=''):
    i=0
    for o in obs:
        if o.type=='MESH': o.name=f'GEAR_{slot}{side}_{i:02d}'; i+=1
def mirror_group(obs,cx,suffix):
    out=[]
    for o in obs:
        if o.type!='MESH': continue
        d=o.copy(); d.data=o.data.copy(); bpy.context.scene.collection.objects.link(d)
        d.name=o.name+suffix; d.location.x=2*cx-o.location.x; d.scale.x*=-1; out.append(d)
    bpy.context.view_layer.update(); return out
def tri(o): return sum(max(0,len(p.vertices)-2) for p in o.data.polygons) if o.type=='MESH' else 0
def slot_path(slot): return os.path.join(MASTER,'models',slot,f'{slot}_source.glb')
def bone_find(arm,*tokens):
    if not arm:return None
    for t in tokens:
        tt=t.lower().replace('_','').replace('.','')
        for b in arm.data.bones:
            n=b.name.lower().replace('_','').replace('.','')
            if tt in n:return b.name
    return None
def bone_pos(arm,name):
    if not arm or not name:return None
    p=arm.pose.bones.get(name); return arm.matrix_world @ p.head if p else None
def make_underarmor(body,mn,mx,H):
    under=body.copy(); under.data=body.data.copy(); bpy.context.scene.collection.objects.link(under); under.name='BODY_UNDERARMOR_STATIC'
    bm=bmesh.new(); bm.from_mesh(under.data)
    kill=[]
    for f in bm.faces:
        wc=[under.matrix_world @ v.co for v in f.verts]
        c=sum(wc,Vector())/max(1,len(wc))
        zn=(c.z-mn.z)/H
        if zn>0.845: kill.append(f)
    if kill: bmesh.ops.delete(bm,geom=kill,context='FACES')
    bm.to_mesh(under.data); bm.free(); under.data.update()
    mat=bpy.data.materials.new('MAT_Underarmor_Dark'); mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value=(0.008,0.010,0.012,1)
        bsdf.inputs['Roughness'].default_value=.80
        bsdf.inputs['Metallic'].default_value=.01
    under.data.materials.clear(); under.data.materials.append(mat)
    for p in under.data.polygons: p.material_index=0
    disp=under.modifiers.new('AQ_UnderarmorOffset','DISPLACE'); disp.strength=.0025; disp.direction='NORMAL'
    bpy.context.view_layer.objects.active=under; under.select_set(True)
    try: bpy.ops.object.modifier_apply(modifier=disp.name)
    except Exception as e: log(f'underarmor offset warning {e}')
    under.select_set(False)
    return under
def look_at(o,t): o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()

if not os.path.isfile(BODY_PATH): raise RuntimeError('Body_Rigged.glb missing')
for s in SLOTS:
    p=slot_path(s)
    if not os.path.isfile(p): raise RuntimeError(f'Missing V3 slot: {p}')
    if 'SmokeTest' in p: raise RuntimeError(f'SMOKETEST_REJECTED {p}')

clear(); body_obs=import_glb(BODY_PATH); arm=find_arm(body_obs); body=largest_mesh(body_obs)
if not arm or not body: raise RuntimeError('Rigged body import invalid')
if len(arm.data.bones)<15: raise RuntimeError(f'Skeleton too small: {len(arm.data.bones)}')
arm.name='ARMATURE_AETHERQOR_HUMANOID'; body.name='BODY_BASE'
mn,mx=bbox([body]); H=mx.z-mn.z; cx=(mn.x+mx.x)*.5; cy=(mn.y+mx.y)*.5
if H<0.5: raise RuntimeError(f'Body height invalid {H}')
rhand=bone_find(arm,'righthand','handr','hand.r','hand_r'); lhand=bone_find(arm,'lefthand','handl','hand.l','hand_l')
rp=bone_pos(arm,rhand); lp=bone_pos(arm,lhand)
if rp is None: rp=Vector((cx+H*.30,cy,mn.z+H*.56))
if lp is None: lp=Vector((cx-H*.30,cy,mn.z+H*.56))
underarmor=make_underarmor(body,mn,mx,H)

# Existing meshes only. Front is -Y in the QA camera. Push wearable shells slightly toward -Y
# so they sit outside the body instead of disappearing inside it. Uniform scaling only.
config={
 'Helmet':      (Vector((cx,cy-H*.010,mn.z+H*.915)), H*.175),
 'Chest':       (Vector((cx,cy-H*.070,mn.z+H*.690)), H*.370),
 'Belt':        (Vector((cx,cy-H*.030,mn.z+H*.500)), H*.300),
 'Cloak':       (Vector((cx,cy+H*.060,mn.z+H*.515)), H*.590),
 'Sword':       (Vector((rp.x,rp.y-H*.010,mn.z+H*.390)), H*.735),
 'Shield':      (Vector((lp.x,lp.y-H*.005,mn.z+H*.555)), H*.440),
 'ClassRelic':  (Vector((cx,cy-H*.125,mn.z+H*.670)), H*.105),
 'Shoulders_R': (Vector((cx+H*.170,cy-H*.040,mn.z+H*.755)), H*.165),
 'Gloves_R':    (Vector((rp.x,cy-H*.035,rp.z-H*.070)), H*.220),
 'Legs_R':      (Vector((cx+H*.085,cy-H*.030,mn.z+H*.325)), H*.420),
 'Boots_R':     (Vector((cx+H*.085,cy-H*.045,mn.z+H*.115)), H*.240),
}
slot_objs={}; scales={}
for s in ['Helmet','Belt','Cloak','Sword','Shield','ClassRelic']:
    obs=meshes(import_glb(slot_path(s))); rename(obs,s); scales[s]=fit_height(obs,*config[s]); slot_objs[s]=obs
obs=meshes(import_glb(slot_path('Chest'))); rename(obs,'Chest'); scales['Chest']=fit_height_min_width(obs,config['Chest'][0],config['Chest'][1],H*.230); slot_objs['Chest']=obs
for s,key in [('Shoulders','Shoulders_R'),('Gloves','Gloves_R'),('Legs','Legs_R'),('Boots','Boots_R')]:
    obs=meshes(import_glb(slot_path(s))); rename(obs,s,'_R'); scales[s]=fit_height(obs,*config[key]); left=mirror_group(obs,cx,'_L'); slot_objs[s]=obs+left

qa={'status':'STATIC_VISUAL_GATE_REQUIRED','meshy_calls':0,'body_height':H,'bones':len(arm.data.bones),'method':'existing V3 meshes only; uniform scaling; outward -Y offsets; fuller underarmor; exact bilateral mirror; NO Meshy; NO donor slicing; NO SmokeTest; NO rigging before visual PASS','scales':scales,'slots':{},'underarmor':{'tris':tri(underarmor),'verts':len(underarmor.data.vertices)}}
for s,obs in slot_objs.items():
    a,b=bbox(obs); d=b-a
    qa['slots'][s]={'objects':len(obs),'tris':sum(tri(o) for o in obs),'verts':sum(len(o.data.vertices) for o in obs),'bbox_dims':[d.x,d.y,d.z],'center':list(center(obs))}
qa['total_tris']=sum(tri(o) for o in bpy.data.objects if o.type=='MESH')
with open(os.path.join(OUT,'reports','assembly_v3_qa.json'),'w',encoding='utf8') as f: json.dump(qa,f,indent=2)

scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=900; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.world.color=(0.006,0.006,0.006)
try: scene.view_settings.look='AgX - Medium High Contrast'
except: pass
bpy.ops.mesh.primitive_plane_add(size=8,location=(cx,cy,mn.z-.012)); floor=bpy.context.object; floor.name='QA_Floor'
fm=bpy.data.materials.new('QA_Floor_Mat'); fm.use_nodes=True
fbsdf=fm.node_tree.nodes.get('Principled BSDF')
if fbsdf: fbsdf.inputs['Base Color'].default_value=(0.018,0.018,0.018,1); fbsdf.inputs['Roughness'].default_value=.82
floor.data.materials.append(fm)
for loc,en,size in [((cx-H*.75,cy-H*1.05,mn.z+H*1.30),650,3.2),((cx+H*.95,cy-H*.30,mn.z+H*.90),450,2.8),((cx,cy+H*.95,mn.z+H*1.05),550,3.0)]:
    ld=bpy.data.lights.new('QA_Area','AREA'); ld.energy=en; ld.shape='DISK'; ld.size=size
    lo=bpy.data.objects.new('QA_Area',ld); bpy.context.scene.collection.objects.link(lo); lo.location=loc
camd=bpy.data.cameras.new('QA_Camera'); cam=bpy.data.objects.new('QA_Camera',camd); bpy.context.scene.collection.objects.link(cam); scene.camera=cam; camd.lens=60
target=Vector((cx,cy,mn.z+H*.52))
views={'front':Vector((cx,cy-H*2.75,mn.z+H*.58)),'three_quarter':Vector((cx+H*1.55,cy-H*2.20,mn.z+H*.60)),'side':Vector((cx+H*2.75,cy,mn.z+H*.58)),'back':Vector((cx,cy+H*2.75,mn.z+H*.58))}
for name,loc in views.items(): cam.location=loc; look_at(cam,target); scene.render.filepath=os.path.join(OUT,'renders',f'{name}.png'); bpy.ops.render.render(write_still=True)
for o in list(bpy.data.objects):
    if o.name.startswith('QA_'): bpy.data.objects.remove(o,do_unlink=True)
blend=os.path.join(OUT,'AETHERQOR_RUNIC_WARDEN_FULL_MALE_V3_QUARANTINE.blend'); bpy.ops.wm.save_as_mainfile(filepath=blend)
exportables=[o for o in bpy.data.objects if o.type in {'MESH','ARMATURE','EMPTY'}]
bpy.ops.object.select_all(action='DESELECT')
for o in exportables:o.select_set(True)
bpy.context.view_layer.objects.active=arm
fbx=os.path.join(OUT,'AETHERQOR_RUNIC_WARDEN_FULL_MALE_V3_QUARANTINE.fbx'); bpy.ops.export_scene.fbx(filepath=fbx,use_selection=True,add_leaf_bones=False,bake_anim=False,apply_unit_scale=True)
glb=os.path.join(OUT,'AETHERQOR_RUNIC_WARDEN_FULL_MALE_V3_QUARANTINE.glb'); bpy.ops.export_scene.gltf(filepath=glb,export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
manifest={'character':'AETHERQOR_RUNIC_WARDEN_FULL_MALE_V3','status':'STATIC_FIT_QUARANTINE_VISUAL_GATE','meshy_calls':0,'body':BODY_PATH,'master':MASTER,'slots':SLOTS,'files':[os.path.basename(blend),os.path.basename(fbx),os.path.basename(glb)],'note':'Do not promote. Existing-mesh static fit only. Rig/weight transfer begins only after visual PASS_STRONG.'}
with open(os.path.join(OUT,'AETHERQOR_RUNIC_WARDEN_FULL_MALE_V3_MANIFEST.json'),'w',encoding='utf8') as f: json.dump(manifest,f,indent=2)
log(f'DONE static repair V4 H={H:.4f} tris={qa["total_tris"]} Meshy=0')
