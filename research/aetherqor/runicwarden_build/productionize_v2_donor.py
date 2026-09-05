import bpy, os, sys, json, math, statistics, shutil
from mathutils import Vector
from mathutils.bvhtree import BVHTree

argv=sys.argv
argv=argv[argv.index('--')+1:] if '--' in argv else []
a={}
for i in range(0,len(argv)-1,2):
    if argv[i].startswith('--'): a[argv[i][2:]]=argv[i+1]
DONOR=os.path.abspath(a['donor']); BODY=os.path.abspath(a['body']); OUT=os.path.abspath(a['out'])
SWORD=os.path.abspath(a['sword']) if a.get('sword') else ''
SHIELD=os.path.abspath(a['shield']) if a.get('shield') else ''
os.makedirs(OUT,exist_ok=True); os.makedirs(os.path.join(OUT,'renders'),exist_ok=True); os.makedirs(os.path.join(OUT,'reports'),exist_ok=True)

def log(s): print('[RW-PROD]',s,flush=True)
def clear(): bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def imp(path):
    before=set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=path); return [o for o in bpy.data.objects if o not in before]
def meshes(obs): return [o for o in obs if o.type=='MESH']
def arm(obs):
    aa=[o for o in obs if o.type=='ARMATURE']; return max(aa,key=lambda o:len(o.data.bones)) if aa else None
def bbox(obs):
    pts=[]
    for o in obs:
        if o.type!='MESH': continue
        pts += [o.matrix_world@Vector(c) for c in o.bound_box]
    mn=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts))); mx=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    return mn,mx
def tri(o): return sum(max(0,len(p.vertices)-2) for p in o.data.polygons) if o.type=='MESH' else 0
def center(o): mn,mx=bbox([o]); return (mn+mx)*.5
def dims(o): mn,mx=bbox([o]); return mx-mn
def roots(obs): return [o for o in obs if o.parent is None]
def scale_group(obs,s):
    for o in roots(obs): o.scale*=s
    bpy.context.view_layer.update()
def move_group(obs,d):
    for o in roots(obs): o.location+=d
    bpy.context.view_layer.update()
def bone_name(ar,*tokens):
    if not ar:return None
    names=[b.name for b in ar.data.bones]
    for t in tokens:
        q=t.lower().replace('_','').replace('.','')
        for n in names:
            if q in n.lower().replace('_','').replace('.',''): return n
    return None
def bone_pos(ar,n):
    if not ar or not n:return None
    p=ar.pose.bones.get(n); return ar.matrix_world@p.head if p else None

def parent_bone(o,ar,bn):
    mw=o.matrix_world.copy(); o.parent=ar; o.parent_type='BONE'; o.parent_bone=bn; o.matrix_world=mw

def transfer_weights(o,body,ar):
    for vg in list(o.vertex_groups): o.vertex_groups.remove(vg)
    m=o.modifiers.new('AQ_DataTransfer','DATA_TRANSFER'); m.object=body; m.use_vert_data=True; m.data_types_verts={'VGROUP_WEIGHTS'}; m.vert_mapping='POLYINTERP_NEAREST'
    bpy.context.view_layer.objects.active=o; o.select_set(True)
    try: bpy.ops.object.modifier_apply(modifier=m.name)
    finally: o.select_set(False)
    am=o.modifiers.new('AQ_Armature','ARMATURE'); am.object=ar

def join_slot(obs,name):
    obs=[o for o in obs if o and o.name in bpy.data.objects and o.type=='MESH']
    if not obs:return None
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs:o.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]; bpy.ops.object.join(); o=obs[0]; o.name='GEAR_'+name
    return o

def decimate(o,target):
    cur=tri(o)
    if cur<=target:return cur
    m=o.modifiers.new('AQ_LOD0_DECIMATE','DECIMATE'); m.decimate_type='COLLAPSE'; m.ratio=max(.01,min(1.0,target/cur))
    bpy.context.view_layer.objects.active=o; o.select_set(True)
    try:bpy.ops.object.modifier_apply(modifier=m.name)
    except Exception as e:log(f'decimate fail {o.name}: {e}')
    o.select_set(False); return tri(o)

def sample_distance(o,bvh,maxn=96):
    vs=o.data.vertices
    if not vs:return 999.0
    step=max(1,len(vs)//maxn); ds=[]
    for i in range(0,len(vs),step):
        p=o.matrix_world@vs[i].co; hit=bvh.find_nearest(p)
        if hit and hit[0] is not None: ds.append((p-hit[0]).length)
        if len(ds)>=maxn:break
    return statistics.median(ds) if ds else 999.0

def fit_uniform_to_length(o,target):
    d=dims(o); L=max(d); s=target/max(L,1e-6); o.scale*=s; bpy.context.view_layer.update()

def place_center(o,p):
    c=center(o); o.location += Vector(p)-c; bpy.context.view_layer.update()

def socket(ar,name,bn):
    e=bpy.data.objects.new(name,None); bpy.context.scene.collection.objects.link(e); e.empty_display_type='PLAIN_AXES'; e.empty_display_size=.06
    if bn: parent_bone(e,ar,bn)
    return e

def look_at(o,t): o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()

clear()
body_obs=imp(BODY); ar=arm(body_obs); body=max(meshes(body_obs),key=lambda o:tri(o))
if not ar or len(ar.data.bones)<15: raise RuntimeError('RIG_REQUIRED')
body.name='BODY_BASE'; ar.name='ARMATURE_AETHERQOR_HUMANOID'
bmn,bmx=bbox([body]); H=bmx.z-bmn.z; bc=(bmn+bmx)*.5
if H<1.0 or H>2.5: raise RuntimeError(f'BAD_BODY_HEIGHT {H}')
# body BVH
bpy.context.view_layer.update(); deps=bpy.context.evaluated_depsgraph_get(); bvh=BVHTree.FromObject(body,deps)

donor_obs=imp(DONOR); donor=max(meshes(donor_obs),key=lambda o:tri(o)); donor.name='DONOR_V2_SOURCE'
dmn,dmx=bbox([donor]); DH=dmx.z-dmn.z
scale_group(donor_obs,H/max(DH,1e-6)); dmn,dmx=bbox([donor]); dc=(dmn+dmx)*.5
move_group(donor_obs,Vector((bc.x-dc.x,bc.y-dc.y,bmn.z-dmn.z)))
bpy.context.view_layer.update(); dmn,dmx=bbox([donor]);
log(f'donor tris={tri(donor)} height={dmx.z-dmn.z:.4f}')
# preserve source copy
src=donor.copy(); src.data=donor.data.copy(); bpy.context.scene.collection.objects.link(src); src.name='DONOR_HIGH_ARCHIVE'; src.hide_render=True; src.hide_viewport=True
# split by loose parts in C
bpy.ops.object.select_all(action='DESELECT'); donor.select_set(True); bpy.context.view_layer.objects.active=donor
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.separate(type='LOOSE'); bpy.ops.object.mode_set(mode='OBJECT')
parts=[o for o in bpy.context.selected_objects if o.type=='MESH']
if len(parts)<20: raise RuntimeError(f'DONOR_NOT_MODULAR_ENOUGH loose_parts={len(parts)}')
log(f'loose_parts={len(parts)}')

slots={k:[] for k in ['Helmet','Chest','Shoulders','Gloves','Belt','Legs','Boots','Cloak']}; dropped=[]; unknown=[]; stats=[]
for i,o in enumerate(parts):
    t=tri(o); mn,mx=bbox([o]); c=(mn+mx)*.5; d=mx-mn
    nz=(c.z-bmn.z)/H; nx=abs(c.x-bc.x)/H; ny=(c.y-bc.y)/H; dz=d.z/H
    md=sample_distance(o,bvh)
    bodylike=(md<0.010 and t>30)
    rec={'name':o.name,'tris':t,'nz':nz,'nx':nx,'ny':ny,'dz':dz,'median_body_dist':md,'bodylike':bodylike}
    slot=None
    if t<8: dropped.append(o); rec['slot']='DROP_TINY'
    elif bodylike: dropped.append(o); rec['slot']='DROP_BODYLIKE'
    else:
        # back mantle before torso classification
        if .28<nz<.78 and ny>.055 and dz>.16 and nx<.34: slot='Cloak'
        elif nz>.82 and nx<.20: slot='Helmet'
        elif nz<.19: slot='Boots'
        elif .15<nz<.48 and nx<.29: slot='Legs'
        elif .42<nz<.72 and nx>.24: slot='Gloves'
        elif .63<nz<.84 and nx>.13: slot='Shoulders'
        elif .48<nz<.79 and nx<.30: slot='Chest'
        elif .36<nz<.55 and nx<.30: slot='Belt'
        elif .18<nz<.48 and nx<.36: slot='Legs'
        elif .45<nz<.82 and nx<.36: slot='Chest'
        else: unknown.append(o)
        rec['slot']=slot or 'UNKNOWN'
        if slot: slots[slot].append(o)
    stats.append(rec)

for o in dropped+unknown:
    if o.name in bpy.data.objects: bpy.data.objects.remove(o,do_unlink=True)

budgets={'Helmet':2200,'Chest':5200,'Shoulders':3000,'Gloves':2200,'Belt':1400,'Legs':4200,'Boots':2200,'Cloak':3000}
slotobj={}
for s,obs in slots.items():
    o=join_slot(obs,s)
    if not o: continue
    before=tri(o); after=decimate(o,budgets[s]); slotobj[s]=o
    log(f'{s}: {before}->{after} tris')

required=['Helmet','Chest','Shoulders','Gloves','Belt','Legs','Boots','Cloak']
missing=[s for s in required if s not in slotobj]
if missing: raise RuntimeError('MISSING_SEGMENTED_SLOTS '+','.join(missing))
# weight/parent
head=bone_name(ar,'head'); rh=bone_name(ar,'righthand','hand.r','hand_r','rhand'); lh=bone_name(ar,'lefthand','hand.l','hand_l','lhand'); spine=bone_name(ar,'spine2','chest','spine1','spine'); hips=bone_name(ar,'hips','pelvis')
if not rh or not lh or not head: raise RuntimeError('HAND_OR_HEAD_BONES_MISSING')
for s,o in slotobj.items():
    if s=='Helmet': parent_bone(o,ar,head)
    else: transfer_weights(o,body,ar)
# sockets
sockR=socket(ar,'Socket_RightHand',rh); sockL=socket(ar,'Socket_LeftHand',lh); socket(ar,'Socket_BackWeapon',spine); socket(ar,'Socket_BackShield',spine)
# weapon / shield reuse, no generation here
weapons={}
for name,path,bn,target in [('Sword',SWORD,rh,H*.62),('Shield',SHIELD,lh,H*.40)]:
    if not path or not os.path.isfile(path): raise RuntimeError(f'MISSING_REUSED_{name.upper()}')
    oo=imp(path); mm=meshes(oo); o=join_slot(mm,name)
    fit_uniform_to_length(o,target); bp=bone_pos(ar,bn); place_center(o,bp)
    # visual rest pose: blade vertical, shield broad plane along YZ
    if name=='Sword': o.rotation_euler=(0,0,0)
    parent_bone(o,ar,bn); weapons[name]=o
# render setup
floor_z=bmn.z-.005; bpy.ops.mesh.primitive_plane_add(size=6,location=(bc.x,bc.y,floor_z)); fl=bpy.context.object; fl.name='QA_Floor'
mat=bpy.data.materials.new('QA_Floor'); mat.diffuse_color=(.03,.03,.03,1); fl.data.materials.append(mat)
for loc,en,size in [((bc.x-H*.8,bc.y-H*1.2,bmn.z+H*1.3),1100,4),((bc.x+H*.9,bc.y-H*.5,bmn.z+H*.9),750,3),((bc.x,bc.y+H*.9,bmn.z+H*1.15),900,3)]:
    ld=bpy.data.lights.new('QA','AREA'); ld.energy=en; ld.shape='DISK'; ld.size=size; lo=bpy.data.objects.new('QA',ld); bpy.context.scene.collection.objects.link(lo); lo.location=loc; look_at(lo,(bc.x,bc.y,bmn.z+H*.55))
camd=bpy.data.cameras.new('QA_Camera'); cam=bpy.data.objects.new('QA_Camera',camd); bpy.context.scene.collection.objects.link(cam); bpy.context.scene.camera=cam; camd.lens=65
sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE'; sc.render.resolution_x=1024; sc.render.resolution_y=1024; sc.render.resolution_percentage=100; sc.render.image_settings.file_format='PNG'; sc.world.color=(.015,.015,.015)
for nm,loc in [('front',(bc.x,bc.y-H*2.4,bmn.z+H*.58)),('three_quarter',(bc.x+H*1.45,bc.y-H*1.9,bmn.z+H*.62)),('back',(bc.x,bc.y+H*2.4,bmn.z+H*.58))]:
    cam.location=loc; look_at(cam,(bc.x,bc.y,bmn.z+H*.54)); sc.render.filepath=os.path.join(OUT,'renders',nm+'.png'); bpy.ops.render.render(write_still=True)
# QA / save
qa={'status':'PRODUCTION_QUARANTINE','body_height_m':H,'bones':len(ar.data.bones),'donor_loose_parts':len(parts),'unknown_deleted':len(unknown),'bodylike_deleted':sum(1 for r in stats if r['bodylike']),'slots':{s:{'tris':tri(o),'verts':len(o.data.vertices)} for s,o in slotobj.items()},'weapons':{s:{'tris':tri(o)} for s,o in weapons.items()},'total_gameplay_tris':sum(tri(o) for o in list(slotobj.values())+list(weapons.values())),'missing':missing,'jewelry':False}
json.dump(qa,open(os.path.join(OUT,'reports','production_qa.json'),'w',encoding='utf8'),indent=2)
json.dump(stats,open(os.path.join(OUT,'reports','component_classification.json'),'w',encoding='utf8'),indent=2)
manifest={'character':'RunicWarden','version':'AAA_V2_PRODUCTION_QUARANTINE','body':BODY,'donor':DONOR,'slots':list(slotobj),'weapon_source':SWORD,'shield_source':SHIELD,'armature':ar.name,'sockets':['Socket_RightHand','Socket_LeftHand','Socket_BackWeapon','Socket_BackShield']}
json.dump(manifest,open(os.path.join(OUT,'MANIFEST.json'),'w',encoding='utf8'),indent=2)
# hide QA helpers before export
for o in [fl,cam]+[o for o in bpy.data.objects if o.name=='QA']: o.hide_render=True
blend=os.path.join(OUT,'AETHERQOR_RUNIC_WARDEN_AAA_V2_PRODUCTION.blend'); bpy.ops.wm.save_as_mainfile(filepath=blend)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,'AETHERQOR_RUNIC_WARDEN_AAA_V2_PRODUCTION.glb'),export_format='GLB',export_apply=True,export_animations=True)
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT,'AETHERQOR_RUNIC_WARDEN_AAA_V2_PRODUCTION.fbx'),use_selection=False,add_leaf_bones=False,bake_anim=True)
log('PRODUCTIONIZE_DONE')