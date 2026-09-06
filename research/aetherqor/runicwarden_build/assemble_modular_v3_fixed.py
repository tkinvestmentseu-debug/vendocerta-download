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

def log(x): print('[RW-V3-FIXED]',x,flush=True)
def clear(): bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def import_glb(path):
    before=set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]
def meshes(obs): return [o for o in obs if o.type=='MESH']
def bbox(obs):
    pts=[]
    for o in obs:
        if o.type!='MESH': continue
        pts.extend([o.matrix_world @ Vector(c) for c in o.bound_box])
    if not pts: return Vector((0,0,0)),Vector((1,1,1))
    mn=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    mx=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    return mn,mx
def dims(obs):
    a,b=bbox(obs); return b-a
def center(obs):
    a,b=bbox(obs); return (a+b)*0.5
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
def uniform_fit(obs,target_center,target_measure,axis='z'):
    d=dims(obs); idx={'x':0,'y':1,'z':2}[axis]; cur=max(d[idx],1e-6); s=target_measure/cur
    if not (0.02<=s<=50): raise RuntimeError(f'unsafe scale {s} axis={axis}')
    apply_uniform(obs,s); move_center(obs,target_center); return s
def largest_mesh(obs):
    ms=meshes(obs); return max(ms,key=lambda o:len(o.data.polygons)) if ms else None
def find_arm(obs):
    ar=[o for o in obs if o.type=='ARMATURE']; return max(ar,key=lambda o:len(o.data.bones)) if ar else None
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
def parent_keep(obj,parent,bone=None):
    mw=obj.matrix_world.copy(); obj.parent=parent
    if bone: obj.parent_type='BONE'; obj.parent_bone=bone
    else: obj.parent_type='OBJECT'; obj.parent_bone=''
    obj.matrix_world=mw
def weight_transfer(obj,body,arm):
    if obj.type!='MESH':return
    for vg in list(obj.vertex_groups): obj.vertex_groups.remove(vg)
    for vg in body.vertex_groups: obj.vertex_groups.new(name=vg.name)
    mod=obj.modifiers.new('AQ_V3_WeightTransfer','DATA_TRANSFER'); mod.object=body
    mod.use_vert_data=True; mod.data_types_verts={'VGROUP_WEIGHTS'}; mod.vert_mapping='POLYINTERP_NEAREST'
    bpy.context.view_layer.objects.active=obj; obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name); obj.select_set(False)
    am=obj.modifiers.new('AQ_V3_Armature','ARMATURE'); am.object=arm; parent_keep(obj,arm)
def mirror_group(obs,cx,suffix):
    out=[]
    for o in obs:
        if o.type!='MESH': continue
        d=o.copy(); d.data=o.data.copy(); bpy.context.scene.collection.objects.link(d)
        d.name=o.name+suffix; d.location.x=2*cx-o.location.x; d.scale.x*=-1; out.append(d)
    bpy.context.view_layer.update(); return out
def tri(o): return sum(max(0,len(p.vertices)-2) for p in o.data.polygons) if o.type=='MESH' else 0
def weighted_count(o):
    if o.type!='MESH':return 0
    return sum(1 for v in o.data.vertices if any(g.weight>1e-8 for g in v.groups))
def slot_path(slot): return os.path.join(MASTER,'models',slot,f'{slot}_source.glb')
def rename(obs,slot,side=''):
    i=0
    for o in obs:
        if o.type=='MESH': o.name=f'GEAR_{slot}{side}_{i:02d}'; i+=1
def create_socket(arm,name,bone):
    e=bpy.data.objects.new(name,None); bpy.context.scene.collection.objects.link(e); e.empty_display_type='PLAIN_AXES'; e.empty_display_size=.055
    if bone: parent_keep(e,arm,bone)
    return e
def world_vertices(obj): return [obj.matrix_world @ v.co for v in obj.data.vertices]
def slice_dims(body,mn,H,z0,z1):
    pts=[p for p in world_vertices(body) if z0 <= (p.z-mn.z)/max(H,1e-6) <= z1]
    if not pts: return H*.25,H*.15
    return max(p.x for p in pts)-min(p.x for p in pts), max(p.y for p in pts)-min(p.y for p in pts)
def create_underarmor(body,arm,mn,H):
    under=body.copy(); under.data=body.data.copy(); bpy.context.scene.collection.objects.link(under); under.name='BODY_UNDERARMOR'
    bm=bmesh.new(); bm.from_mesh(under.data)
    cutoff=mn.z+H*.845
    kill=[]
    for f in bm.faces:
        z=sum((under.matrix_world @ v.co).z for v in f.verts)/max(1,len(f.verts))
        if z>cutoff: kill.append(f)
    if kill: bmesh.ops.delete(bm,geom=kill,context='FACES')
    bm.to_mesh(under.data); bm.free(); under.data.update()
    mat=bpy.data.materials.new('MAT_Underarmor_Dark'); mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value=(0.018,0.020,0.022,1)
        bsdf.inputs['Roughness'].default_value=.72
        bsdf.inputs['Metallic'].default_value=.05
    under.data.materials.clear(); under.data.materials.append(mat)
    for p in under.data.polygons:p.material_index=0
    disp=under.modifiers.new('AQ_UnderarmorOffset','DISPLACE'); disp.strength=.0035; disp.direction='NORMAL'
    bpy.context.view_layer.objects.active=under; under.select_set(True)
    try: bpy.ops.object.modifier_apply(modifier=disp.name)
    except Exception as e: log(f'underarmor offset apply warning: {e}')
    under.select_set(False)
    return under

if not os.path.isfile(BODY_PATH): raise RuntimeError('Body_Rigged.glb missing')
slots=['Helmet','Chest','Shoulders','Gloves','Belt','Legs','Boots','Cloak','Sword','Shield','ClassRelic']
for s in slots:
    p=slot_path(s)
    if not os.path.isfile(p): raise RuntimeError(f'Missing V3 slot: {p}')
    if 'SmokeTest' in p: raise RuntimeError(f'SMOKETEST_REJECTED {p}')

clear(); body_obs=import_glb(BODY_PATH); arm=find_arm(body_obs); body=largest_mesh(body_obs)
if not arm or not body: raise RuntimeError('Rigged body import invalid')
if len(arm.data.bones)<15: raise RuntimeError(f'Skeleton too small: {len(arm.data.bones)}')
arm.name='ARMATURE_AETHERQOR_HUMANOID'; body.name='BODY_BASE'
mn,mx=bbox([body]); H=mx.z-mn.z; cx=(mn.x+mx.x)/2; cy=(mn.y+mx.y)/2
if H<0.5: raise RuntimeError(f'Body height invalid {H}')
torsoW,torsoD=slice_dims(body,mn,H,.56,.78); waistW,waistD=slice_dims(body,mn,H,.43,.56); headW,headD=slice_dims(body,mn,H,.84,.99)

rhand=bone_find(arm,'righthand','handr','hand.r','hand_r'); lhand=bone_find(arm,'lefthand','handl','hand.l','hand_l')
headb=bone_find(arm,'head'); spine=bone_find(arm,'spine2','spine02','chest','spine1','spine01','spine'); hips=bone_find(arm,'hips','pelvis','root')
if not rhand or not lhand: raise RuntimeError(f'Hand bones unresolved right={rhand} left={lhand}')
rp=bone_pos(arm,rhand); lp=bone_pos(arm,lhand)
if rp is None: rp=Vector((cx+H*.34,cy,mn.z+H*.55))
if lp is None: lp=Vector((cx-H*.34,cy,mn.z+H*.55))

underarmor=create_underarmor(body,arm,mn,H)

# Uniform scaling only. Targets now use real body width/depth to keep armor outside the body.
targets={
 'Helmet':(Vector((cx,cy,mn.z+H*.915)),H*.165,'z'),
 'Chest':(Vector((cx,cy-torsoD*.04,mn.z+H*.675)),torsoW*1.12,'x'),
 'Belt':(Vector((cx,cy,mn.z+H*.505)),waistW*1.16,'x'),
 'Cloak':(Vector((cx,cy+torsoD*.56,mn.z+H*.55)),H*.58,'z'),
 'Sword':(Vector((rp.x,rp.y,mn.z+H*.38)),H*.78,'z'),
 'Shield':(Vector((lp.x,lp.y,mn.z+H*.56)),H*.47,'z'),
 'ClassRelic':(Vector((cx,cy-torsoD*.60,mn.z+H*.64)),H*.15,'z'),
}
slot_objs={}; scales={}
for s in ['Helmet','Chest','Belt','Cloak','Sword','Shield','ClassRelic']:
    obs=meshes(import_glb(slot_path(s))); rename(obs,s)
    tc,measure,axis=targets[s]; scales[s]=uniform_fit(obs,tc,measure,axis); slot_objs[s]=obs

# Bilateral modules are one approved source mirrored exactly.
obs=meshes(import_glb(slot_path('Shoulders'))); rename(obs,'Shoulders','_R')
scales['Shoulders']=uniform_fit(obs,Vector((cx+torsoW*.54,cy-torsoD*.02,mn.z+H*.745)),H*.155,'z'); left=mirror_group(obs,cx,'_L'); slot_objs['Shoulders']=obs+left
obs=meshes(import_glb(slot_path('Gloves'))); rename(obs,'Gloves','_R')
scales['Gloves']=uniform_fit(obs,Vector((rp.x,rp.y-torsoD*.015,rp.z-H*.075)),H*.235,'z'); left=mirror_group(obs,cx,'_L'); slot_objs['Gloves']=obs+left
obs=meshes(import_glb(slot_path('Legs'))); rename(obs,'Legs','_R')
scales['Legs']=uniform_fit(obs,Vector((cx+H*.102,cy-torsoD*.035,mn.z+H*.355)),H*.44,'z'); left=mirror_group(obs,cx,'_L'); slot_objs['Legs']=obs+left
obs=meshes(import_glb(slot_path('Boots'))); rename(obs,'Boots','_R')
scales['Boots']=uniform_fit(obs,Vector((cx+H*.098,cy-torsoD*.045,mn.z+H*.105)),H*.235,'z'); left=mirror_group(obs,cx,'_L'); slot_objs['Boots']=obs+left

for o in slot_objs['Helmet']: parent_keep(o,arm,headb) if headb else weight_transfer(o,body,arm)
for s in ['Chest','Shoulders','Gloves','Belt','Legs','Boots','Cloak']:
    for o in slot_objs[s]: weight_transfer(o,body,arm)
for o in slot_objs['ClassRelic']: parent_keep(o,arm,spine) if spine else weight_transfer(o,body,arm)

sockets={
 'Socket_RightHand':create_socket(arm,'Socket_RightHand',rhand),
 'Socket_LeftHand':create_socket(arm,'Socket_LeftHand',lhand),
 'Socket_BackWeapon':create_socket(arm,'Socket_BackWeapon',spine),
 'Socket_BackShield':create_socket(arm,'Socket_BackShield',spine),
 'Socket_Head':create_socket(arm,'Socket_Head',headb),
 'Socket_Hips':create_socket(arm,'Socket_Hips',hips),
}
for o in slot_objs['Sword']: parent_keep(o,sockets['Socket_RightHand'])
for o in slot_objs['Shield']: parent_keep(o,sockets['Socket_LeftHand'])

qa={'status':'STATIC_VISUAL_GATE_REQUIRED','body_height':H,'bones':len(arm.data.bones),'torso_width':torsoW,'torso_depth':torsoD,'scales':scales,'slots':{},'missing':[],'method':'body-measured semantic anchors + uniform scaling + underarmor + exact bilateral mirroring; NO donor slicing; NO nonuniform bbox fit; NO SmokeTest'}
for s,obs in slot_objs.items(): qa['slots'][s]={'objects':len(obs),'tris':sum(tri(o) for o in obs),'verts':sum(len(o.data.vertices) for o in obs),'weighted_verts':sum(weighted_count(o) for o in obs)}
qa['underarmor']={'tris':tri(underarmor),'verts':len(underarmor.data.vertices)}
qa['total_tris']=sum(tri(o) for o in bpy.data.objects if o.type=='MESH')
with open(os.path.join(OUT,'reports','assembly_v3_qa.json'),'w',encoding='utf8') as f: json.dump(qa,f,indent=2)

scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=900; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.world.color=(0.008,0.008,0.008)
try: scene.view_settings.look='AgX - Medium High Contrast'
except: pass
bpy.ops.mesh.primitive_plane_add(size=8,location=(cx,cy,mn.z-.01)); floor=bpy.context.object; floor.name='QA_Floor'
fm=bpy.data.materials.new('QA_Floor_Mat'); fm.diffuse_color=(0.025,0.025,0.025,1); floor.data.materials.append(fm)
for loc,en,size in [((cx-H*.8,cy-H*1.0,mn.z+H*1.3),700,3.5),((cx+H*.9,cy-H*.4,mn.z+H*.9),500,3.0),((cx,cy+H*.9,mn.z+H*1.05),650,3.0)]:
    ld=bpy.data.lights.new('QA_Area','AREA'); ld.energy=en; ld.shape='DISK'; ld.size=size
    lo=bpy.data.objects.new('QA_Area',ld); bpy.context.scene.collection.objects.link(lo); lo.location=loc

def look_at(o,t): o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('QA_Camera'); cam=bpy.data.objects.new('QA_Camera',camd); bpy.context.scene.collection.objects.link(cam); scene.camera=cam; camd.lens=58
target=(cx,cy,mn.z+H*.53)
views={'front':(cx,cy-H*2.65,mn.z+H*.66),'three_quarter':(cx+H*1.55,cy-H*2.1,mn.z+H*.68),'side':(cx+H*2.7,cy,mn.z+H*.66),'back':(cx,cy+H*2.65,mn.z+H*.66)}
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
manifest={'character':'AETHERQOR_RUNIC_WARDEN_FULL_MALE_V3','status':'QUARANTINE_STATIC_VISUAL_GATE_REQUIRED','body':BODY_PATH,'master':MASTER,'slots':list(slot_objs),'bones':len(arm.data.bones),'underarmor':True,'exports':[os.path.basename(blend),os.path.basename(fbx),os.path.basename(glb)]}
with open(os.path.join(OUT,'AETHERQOR_RUNIC_WARDEN_FULL_MALE_V3_MANIFEST.json'),'w',encoding='utf8') as f: json.dump(manifest,f,indent=2)
log('ASSEMBLY_FIXED_COMPLETE')
