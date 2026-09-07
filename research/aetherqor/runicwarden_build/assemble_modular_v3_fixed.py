import bpy, sys, os, json, bmesh
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

def log(x): print('[RW-V3-STATIC-REPAIR-V6]',x,flush=True)
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
        if o.type=='MESH': pts.extend([o.matrix_world @ Vector(c) for c in o.bound_box])
    if not pts: return Vector((0,0,0)),Vector((1,1,1))
    return Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts))), Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
def center(obs):
    a,b=bbox(obs); return (a+b)*0.5
def dims(obs):
    a,b=bbox(obs); return b-a
def apply_uniform(obs,s):
    c=center(obs)
    for o in obs:
        if o.type=='MESH':
            o.location=c+(o.location-c)*s; o.scale*=s
    bpy.context.view_layer.update()
def move_center(obs,target):
    d=Vector(target)-center(obs)
    for o in obs:
        if o.type=='MESH': o.location+=d
    bpy.context.view_layer.update()
def fit_height(obs,target,h):
    s=h/max(dims(obs).z,1e-6)
    if not .02<=s<=20: raise RuntimeError(f'unsafe scale {s}')
    apply_uniform(obs,s); move_center(obs,target); return s
def fit_height_min_width(obs,target,h,min_w):
    s=fit_height(obs,target,h); w=max(dims(obs).x,1e-6)
    if w<min_w:
        e=min(min_w/w,1.30); apply_uniform(obs,e); move_center(obs,target); s*=e
    return s
def rename(obs,slot,suffix=''):
    n=0
    for o in obs:
        if o.type=='MESH': o.name=f'GEAR_{slot}{suffix}_{n:02d}'; n+=1
def mirror_x(obs,cx,suffix='_L'):
    out=[]
    for o in obs:
        if o.type!='MESH': continue
        d=o.copy(); d.data=o.data.copy(); bpy.context.scene.collection.objects.link(d)
        d.name=o.name+suffix; d.location.x=2*cx-o.location.x; d.scale.x*=-1; out.append(d)
    bpy.context.view_layer.update(); return out
def mirror_y(obs,cy,suffix='_BACK'):
    out=[]
    for o in obs:
        if o.type!='MESH': continue
        d=o.copy(); d.data=o.data.copy(); bpy.context.scene.collection.objects.link(d)
        d.name=o.name+suffix; d.location.y=2*cy-o.location.y; d.scale.y*=-1; out.append(d)
    bpy.context.view_layer.update(); return out
def tri(o): return sum(max(0,len(p.vertices)-2) for p in o.data.polygons) if o.type=='MESH' else 0
def slot_path(s): return os.path.join(MASTER,'models',s,f'{s}_source.glb')
def bone_find(arm,*tokens):
    if not arm:return None
    for t in tokens:
        tt=t.lower().replace('_','').replace('.','')
        for b in arm.data.bones:
            if tt in b.name.lower().replace('_','').replace('.',''): return b.name
    return None
def bone_pos(arm,name):
    p=arm.pose.bones.get(name) if arm and name else None
    return arm.matrix_world @ p.head if p else None
def look_at(o,t): o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()

def make_underarmor(body,mn,mx,H,cx):
    under=body.copy(); under.data=body.data.copy(); bpy.context.scene.collection.objects.link(under); under.name='BODY_UNDERARMOR_STATIC'
    bm=bmesh.new(); bm.from_mesh(under.data); kill=[]
    for f in bm.faces:
        wc=[under.matrix_world @ v.co for v in f.verts]; c=sum(wc,Vector())/len(wc)
        zn=(c.z-mn.z)/H; xn=abs(c.x-cx)/H
        # No head or bare feet in geared render. Keep cloth at arms/joints and behind armor.
        if zn>.905 or zn<.135: kill.append(f)
        elif zn<.205 and xn<.18: kill.append(f)
    if kill: bmesh.ops.delete(bm,geom=kill,context='FACES')
    bm.to_mesh(under.data); bm.free(); under.data.update()
    mat=bpy.data.materials.new('MAT_Underarmor_Black'); mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value=(0.0018,0.0021,0.0025,1)
        bsdf.inputs['Roughness'].default_value=.94; bsdf.inputs['Metallic'].default_value=0
    under.data.materials.clear(); under.data.materials.append(mat)
    for p in under.data.polygons: p.material_index=0
    return under

if not os.path.isfile(BODY_PATH): raise RuntimeError('Body_Rigged.glb missing')
for s in SLOTS:
    p=slot_path(s)
    if not os.path.isfile(p): raise RuntimeError(f'Missing V3 slot {p}')
    if 'SmokeTest' in p: raise RuntimeError(f'SMOKETEST_REJECTED {p}')

clear(); body_obs=import_glb(BODY_PATH); arm=find_arm(body_obs); body=largest_mesh(body_obs)
if not arm or not body: raise RuntimeError('invalid rigged body')
arm.name='ARMATURE_AETHERQOR_HUMANOID'; body.name='BODY_BASE'
mn,mx=bbox([body]); H=mx.z-mn.z; cx=(mn.x+mx.x)*.5; cy=(mn.y+mx.y)*.5
if H<.5: raise RuntimeError(f'invalid body height {H}')
rp=bone_pos(arm,bone_find(arm,'righthand','handr','hand.r','hand_r')) or Vector((cx+H*.30,cy,mn.z+H*.56))
lp=bone_pos(arm,bone_find(arm,'lefthand','handl','hand.l','hand_l')) or Vector((cx-H*.30,cy,mn.z+H*.56))
under=make_underarmor(body,mn,mx,H,cx)

# Existing meshes only. Front is -Y. V6 closes front-only generated shells by exact Y reflection,
# while preserving the approved source proportions. No Meshy, no donor slicing, no retopo yet.
config={
 'Helmet':(Vector((cx,cy-H*.010,mn.z+H*.915)),H*.175),
 'Chest':(Vector((cx,cy-H*.070,mn.z+H*.695)),H*.365),
 'Belt':(Vector((cx,cy-H*.030,mn.z+H*.505)),H*.295),
 'Cloak':(Vector((cx,cy+H*.060,mn.z+H*.570)),H*.720),
 'Sword':(Vector((rp.x,rp.y-H*.012,mn.z+H*.405)),H*.735),
 'Shield':(Vector((lp.x,lp.y-H*.006,mn.z+H*.555)),H*.440),
 'ClassRelic':(Vector((cx,cy-H*.125,mn.z+H*.670)),H*.105),
 'Shoulders_R':(Vector((cx+H*.158,cy-H*.030,mn.z+H*.757)),H*.155),
 'Gloves_R':(Vector((rp.x,cy-H*.024,rp.z-H*.050)),H*.225),
 'Legs_R':(Vector((cx+H*.083,cy-H*.024,mn.z+H*.330)),H*.440),
 'Boots_R':(Vector((cx+H*.083,cy-H*.030,mn.z+H*.118)),H*.275),
}
slot_objs={}; scales={}; mirrored_back=[]
for s in ['Helmet','Cloak','Sword','Shield','ClassRelic']:
    obs=meshes(import_glb(slot_path(s))); rename(obs,s); scales[s]=fit_height(obs,*config[s]); slot_objs[s]=obs

obs=meshes(import_glb(slot_path('Chest'))); rename(obs,'Chest'); scales['Chest']=fit_height_min_width(obs,config['Chest'][0],config['Chest'][1],H*.225)
back=mirror_y(obs,cy); slot_objs['Chest']=obs+back; mirrored_back.append('Chest')
obs=meshes(import_glb(slot_path('Belt'))); rename(obs,'Belt'); scales['Belt']=fit_height(obs,*config['Belt']); back=mirror_y(obs,cy); slot_objs['Belt']=obs+back; mirrored_back.append('Belt')

for s,key in [('Shoulders','Shoulders_R'),('Gloves','Gloves_R'),('Legs','Legs_R'),('Boots','Boots_R')]:
    right=meshes(import_glb(slot_path(s))); rename(right,s,'_R'); scales[s]=fit_height(right,*config[key])
    left=mirror_x(right,cx); bilateral=right+left
    back=mirror_y(bilateral,cy); slot_objs[s]=bilateral+back; mirrored_back.append(s)

qa={'status':'STATIC_VISUAL_GATE_REQUIRED','meshy_calls':0,'body_height':H,'bones':len(arm.data.bones),'method':'existing V3 meshes only; uniform scaling; exact X bilateral mirror; exact Y back-shell closure for front-only wearables; enlarged cloak; black underarmor proxy; NO Meshy; NO SmokeTest; NO rigging/retopo before visual pass','mirrored_back':mirrored_back,'scales':scales,'slots':{},'underarmor':{'tris':tri(under),'verts':len(under.data.vertices)}}
for s,obs in slot_objs.items():
    d=dims(obs); qa['slots'][s]={'objects':len(obs),'tris':sum(tri(o) for o in obs),'verts':sum(len(o.data.vertices) for o in obs),'bbox_dims':[d.x,d.y,d.z],'center':list(center(obs))}
qa['total_tris']=sum(tri(o) for o in bpy.data.objects if o.type=='MESH')
with open(os.path.join(OUT,'reports','assembly_v3_qa.json'),'w',encoding='utf8') as f: json.dump(qa,f,indent=2)

scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=900; scene.render.resolution_y=1100; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.world.color=(.006,.006,.006)
try: scene.view_settings.look='AgX - Medium High Contrast'
except: pass
bpy.ops.mesh.primitive_plane_add(size=8,location=(cx,cy,mn.z-.012)); floor=bpy.context.object; floor.name='QA_Floor'
fm=bpy.data.materials.new('QA_Floor_Mat'); fm.use_nodes=True; fbsdf=fm.node_tree.nodes.get('Principled BSDF')
if fbsdf: fbsdf.inputs['Base Color'].default_value=(.018,.018,.018,1); fbsdf.inputs['Roughness'].default_value=.82
floor.data.materials.append(fm)
for loc,en,size in [((cx-H*.75,cy-H*1.05,mn.z+H*1.30),650,3.2),((cx+H*.95,cy-H*.30,mn.z+H*.90),450,2.8),((cx,cy+H*.95,mn.z+H*1.05),550,3.0)]:
    ld=bpy.data.lights.new('QA_Area','AREA'); ld.energy=en; ld.shape='DISK'; ld.size=size; lo=bpy.data.objects.new('QA_Area',ld); bpy.context.scene.collection.objects.link(lo); lo.location=loc
camd=bpy.data.cameras.new('QA_Camera'); cam=bpy.data.objects.new('QA_Camera',camd); bpy.context.scene.collection.objects.link(cam); scene.camera=cam; camd.lens=60
target=Vector((cx,cy,mn.z+H*.52)); views={'front':Vector((cx,cy-H*2.75,mn.z+H*.58)),'three_quarter':Vector((cx+H*1.55,cy-H*2.20,mn.z+H*.60)),'side':Vector((cx+H*2.75,cy,mn.z+H*.58)),'back':Vector((cx,cy+H*2.75,mn.z+H*.58))}
body.hide_render=True
for name,loc in views.items(): cam.location=loc; look_at(cam,target); scene.render.filepath=os.path.join(OUT,'renders',name+'.png'); bpy.ops.render.render(write_still=True)
body.hide_render=False
manifest={'character':'AETHERQOR_RUNIC_WARDEN_FULL_MALE_V3','status':'STATIC_FIT_QUARANTINE_VISUAL_GATE_V6','meshy_calls':0,'body':BODY_PATH,'master':MASTER,'slots':SLOTS,'files':[],'note':'Existing-mesh repair only. Do not promote until visual PASS_STRONG. Retopo/rigging comes after static fit.'}
with open(os.path.join(OUT,'AETHERQOR_RUNIC_WARDEN_FULL_MALE_V3_MANIFEST.json'),'w',encoding='utf8') as f: json.dump(manifest,f,indent=2)
log(f'DONE V6 H={H:.4f} tris={qa["total_tris"]} Meshy=0')
