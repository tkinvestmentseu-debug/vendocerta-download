import bpy, os, sys, json
from mathutils import Vector

argv=sys.argv
argv=argv[argv.index('--')+1:] if '--' in argv else []
args={}
for i in range(0,len(argv)-1,2):
    if argv[i].startswith('--'): args[argv[i][2:]]=argv[i+1]
out=os.path.abspath(args.get('output','./diag'))
os.makedirs(out,exist_ok=True)

def wb(o):
    pts=[o.matrix_world @ Vector(c) for c in o.bound_box]
    mn=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    mx=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    return mn,mx,mx-mn,(mn+mx)*0.5

def tri(o):
    return sum(max(0,len(p.vertices)-2) for p in o.data.polygons) if o.type=='MESH' else 0

meshes=[o for o in bpy.data.objects if o.type=='MESH' and not o.name.startswith('QA_')]
body=next((o for o in meshes if o.name=='BODY_BASE'),None)
if not body:
    body=max(meshes,key=lambda o:len(o.data.polygons))
bmn,bmx,bdim,bc=wb(body)
H=max(bdim.z,1e-6)

report={'body':{'name':body.name,'dims':list(bdim),'center':list(bc),'height':H},'objects':[],'flags':[]}
for o in meshes:
    mn,mx,d,c=wb(o)
    rec={'name':o.name,'dims':[round(x,6) for x in d],'center':[round(x,6) for x in c],'tris':tri(o),'materials':[m.name for m in o.data.materials if m]}
    report['objects'].append(rec)
    if o!=body:
        if max(d)>H*1.25: report['flags'].append({'name':o.name,'reason':'oversize_dimension','dims':rec['dims']})
        if abs(c.x-bc.x)>H or abs(c.y-bc.y)>H or c.z<bmn.z-H*.2 or c.z>bmx.z+H*.2:
            report['flags'].append({'name':o.name,'reason':'center_outlier','center':rec['center']})

# standardized camera and light
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=640; scene.render.resolution_y=640; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world.color=(0.035,0.035,0.035)

# remove existing cameras/lights
for o in list(bpy.data.objects):
    if o.type in {'CAMERA','LIGHT'}:
        bpy.data.objects.remove(o,do_unlink=True)

ld=bpy.data.lights.new('DiagKey','AREA'); ld.energy=1300; ld.size=4
lo=bpy.data.objects.new('DiagKey',ld); scene.collection.objects.link(lo); lo.location=(bc.x-H*.8,bc.y-H*1.4,bmn.z+H*1.4)
ld2=bpy.data.lights.new('DiagFill','AREA'); ld2.energy=900; ld2.size=3
lo2=bpy.data.objects.new('DiagFill',ld2); scene.collection.objects.link(lo2); lo2.location=(bc.x+H*.8,bc.y-H*.7,bmn.z+H*.9)

def look(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
look(lo,(bc.x,bc.y,bmn.z+H*.55)); look(lo2,(bc.x,bc.y,bmn.z+H*.55))
camd=bpy.data.cameras.new('DiagCam'); cam=bpy.data.objects.new('DiagCam',camd); scene.collection.objects.link(cam); scene.camera=cam; camd.lens=58
cam.location=(bc.x,bc.y-H*2.5,bmn.z+H*.58); look(cam,(bc.x,bc.y,bmn.z+H*.52))

slot_names=sorted({o.name.split('_')[1] for o in meshes if o.name.startswith('GEAR_') and len(o.name.split('_'))>=3})
# body-only
for o in meshes: o.hide_render=(o!=body)
scene.render.filepath=os.path.join(out,'00_BODY_ONLY.png'); bpy.ops.render.render(write_still=True)

for slot in slot_names:
    for o in meshes:
        o.hide_render = not (o==body or o.name.startswith('GEAR_'+slot+'_'))
    scene.render.filepath=os.path.join(out,f'slot_{slot}.png')
    bpy.ops.render.render(write_still=True)

# full
for o in meshes: o.hide_render=False
scene.render.filepath=os.path.join(out,'99_FULL.png'); bpy.ops.render.render(write_still=True)

with open(os.path.join(out,'visual_diag.json'),'w',encoding='utf8') as f: json.dump(report,f,indent=2)
print('VISUAL_DIAG_DONE')
for x in report['flags']: print('FLAG',x)
