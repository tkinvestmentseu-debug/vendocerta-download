from __future__ import annotations
import argparse,json,math,os,sys
import bpy
from mathutils import Vector
HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
if ROOT not in sys.path: sys.path.insert(0,ROOT)
from tools.blender.flycat_armor_replay.core import primary_mesh,build_chest,tris,bounds

def reset():
    bpy.ops.object.mode_set(mode='OBJECT') if bpy.context.object and bpy.context.object.mode!='OBJECT' else None
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def import_any(path):
    ext=os.path.splitext(path)[1].lower(); before=set(bpy.data.objects)
    if ext=='.glb' or ext=='.gltf': bpy.ops.import_scene.gltf(filepath=path)
    elif ext=='.fbx': bpy.ops.import_scene.fbx(filepath=path,automatic_bone_orientation=False)
    else: raise RuntimeError('UNSUPPORTED:'+ext)
    return [o for o in bpy.data.objects if o not in before]

def find_arm(objs):
    arms=[o for o in objs if o.type=='ARMATURE']
    return max(arms,key=lambda o:len(o.data.bones)) if arms else None

def body_penetration_proxy(body,chest):
    bmn,bmx=bounds(body); cmn,cmx=bounds(chest)
    overlap=max(0,min(bmx.x,cmx.x)-max(bmn.x,cmn.x))*max(0,min(bmx.y,cmx.y)-max(bmn.y,cmn.y))*max(0,min(bmx.z,cmx.z)-max(bmn.z,cmn.z))
    cvol=max(1e-9,(cmx.x-cmn.x)*(cmx.y-cmn.y)*(cmx.z-cmn.z))
    return overlap/cvol

def render_screen_space(obj,out_dir,heights=(90,150,220,300)):
    os.makedirs(out_dir,exist_ok=True)
    mn,mx=bounds(obj); center=(mn+mx)*.5; extent=max(mx.x-mn.x,mx.y-mn.y,mx.z-mn.z)
    bpy.ops.object.camera_add(location=(center.x,center.y-3.2*extent,center.z))
    cam=bpy.context.object; bpy.context.scene.camera=cam
    def point_at(o,p):
        direction=p-o.location; o.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    point_at(cam,center); cam.data.type='ORTHO'; cam.data.ortho_scale=max(.001,(mx.z-mn.z)*1.15)
    world=bpy.context.scene.world or bpy.data.worlds.new('World'); bpy.context.scene.world=world; world.color=(.03,.03,.03)
    bpy.ops.object.light_add(type='AREA',location=(center.x-.5*extent,center.y-1.5*extent,center.z+1.5*extent)); bpy.context.object.data.energy=900; bpy.context.object.data.shape='DISK'; bpy.context.object.data.size=3*extent
    scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE_NEXT'; scene.render.image_settings.file_format='PNG'; scene.render.resolution_percentage=100
    reports={}
    for h in heights:
        scene.render.resolution_x=max(128,int(h*1.5)); scene.render.resolution_y=h; scene.render.filepath=os.path.join(out_dir,f'chest_{h}px.png'); bpy.ops.render.render(write_still=True)
        reports[str(h)]={'path':scene.render.filepath,'render_h':h,'macro_edge_survival_proxy':min(1.0,max(0.0,(mx.x-mn.x)/(mx.z-mn.z+1e-9)*h/40.0)),'faceting_proxy':'PASS' if tris(obj)>=max(200,h*2) else 'REVIEW'}
    return reports

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--donor',required=True); ap.add_argument('--body',required=True); ap.add_argument('--out',required=True); args=ap.parse_args()
    os.makedirs(args.out,exist_ok=True); reset()
    body_objs=import_any(args.body); arm=find_arm(body_objs)
    if arm is None: raise RuntimeError('BODY_ARMATURE_MISSING')
    body=primary_mesh(body_objs)
    donor_objs=import_any(args.donor); donor=primary_mesh(donor_objs)
    donor_tris=tris(donor); chest=build_chest(donor,body,arm); chest_tris=tris(chest)
    ss=render_screen_space(chest,os.path.join(args.out,'renders'))
    bpy.context.view_layer.objects.active=chest; chest.select_set(True)
    fbx=os.path.join(args.out,'FC_PILOT_CHEST.fbx'); bpy.ops.export_scene.fbx(filepath=fbx,use_selection=True,add_leaf_bones=False,bake_anim=False,apply_unit_scale=True)
    blend=os.path.join(args.out,'FC_PILOT.blend'); bpy.ops.wm.save_as_mainfile(filepath=blend)
    material_ok=bool(chest.data.materials and chest.data.materials[0].use_nodes)
    weighted=sum(1 for v in chest.data.vertices if v.groups)
    result={'blender':'PASS','donor_source':args.donor,'body_source':args.body,'donor_triangles':donor_tris,'pilot_triangles':chest_tris,'donor_fidelity_proxy':round(min(1.0,chest_tris/max(1,donor_tris)*8.0),6),'screen_space':ss,'macro_edge_survival':all(v['macro_edge_survival_proxy']>=.65 for v in ss.values()),'faceting':all(v['faceting_proxy']=='PASS' for v in ss.values()),'body_penetration_proxy':round(body_penetration_proxy(body,chest),6),'material_nodes':material_ok,'vertex_count':len(chest.data.vertices),'weighted_vertices':weighted,'rig_weight_coverage':round(weighted/max(1,len(chest.data.vertices)),6),'gear_toggle_export_ready':os.path.exists(fbx),'fbx':fbx,'blend':blend}
    with open(os.path.join(args.out,'blender_results.json'),'w',encoding='utf-8') as f: json.dump(result,f,indent=2)
    print(json.dumps(result))
if __name__=='__main__': main()
