from __future__ import annotations
import math,bmesh,bpy
from dataclasses import dataclass
from mathutils import Vector
@dataclass(frozen=True)
class PlateSpec:
    thickness:float=.008; bevel_width:float=.003; bevel_segments:int=2

def tris(obj):
    dg=bpy.context.evaluated_depsgraph_get(); eo=obj.evaluated_get(dg); me=eo.to_mesh()
    try: me.calc_loop_triangles(); return len(me.loop_triangles)
    finally: eo.to_mesh_clear()

def bounds(obj):
    p=[obj.matrix_world@Vector(c) for c in obj.bound_box]
    return Vector((min(x.x for x in p),min(x.y for x in p),min(x.z for x in p))),Vector((max(x.x for x in p),max(x.y for x in p),max(x.z for x in p)))

def duplicate(src,name):
    o=src.copy(); o.data=src.data.copy(); o.animation_data_clear(); o.name=name; bpy.context.collection.objects.link(o); return o

def crop_box(obj,mn,mx):
    bm=bmesh.new(); bm.from_mesh(obj.data); mw=obj.matrix_world
    kill=[v for v in bm.verts if not (mn.x<=(mw@v.co).x<=mx.x and mn.y<=(mw@v.co).y<=mx.y and mn.z<=(mw@v.co).z<=mx.z)]
    bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(obj.data); bm.free(); obj.data.update()

def largest_component(obj):
    bm=bmesh.new(); bm.from_mesh(obj.data)
    seen=set(); comps=[]
    for seed in bm.verts:
        if seed in seen: continue
        st=[seed]; comp=set()
        while st:
            v=st.pop()
            if v in seen: continue
            seen.add(v); comp.add(v)
            st.extend(e.other_vert(v) for e in v.link_edges if e.other_vert(v) not in seen)
        comps.append(comp)
    if comps:
        keep=max(comps,key=len); bmesh.ops.delete(bm,geom=[v for v in bm.verts if v not in keep],context='VERTS')
    bm.to_mesh(obj.data); bm.free(); obj.data.update()

def offset_normals(obj,d):
    bm=bmesh.new(); bm.from_mesh(obj.data); bm.normal_update()
    for v in bm.verts:
        if v.normal.length_squared: v.co+=v.normal.normalized()*d
    bm.to_mesh(obj.data); bm.free(); obj.data.update()

def plate_stack(obj,spec=PlateSpec()):
    s=obj.modifiers.new('FC_Thickness','SOLIDIFY'); s.thickness=spec.thickness; s.offset=0; s.use_even_offset=True
    b=obj.modifiers.new('FC_EdgeControl','BEVEL'); b.width=spec.bevel_width; b.segments=spec.bevel_segments; b.limit_method='ANGLE'; b.angle_limit=math.radians(35)

def metal():
    m=bpy.data.materials.get('FC_Pilot_Metal') or bpy.data.materials.new('FC_Pilot_Metal'); m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF'); n.inputs['Base Color'].default_value=(.15,.12,.08,1); n.inputs['Metallic'].default_value=.82; n.inputs['Roughness'].default_value=.31
    return m

def rigid_bind(obj,arm,candidates):
    bone=next((x for x in candidates if x in arm.data.bones),None)
    if bone is None:
        ds=[b.name for b in arm.data.bones if b.use_deform]
        if not ds: raise RuntimeError('NO_DEFORM_BONE')
        bone=ds[len(ds)//2]
    for g in list(obj.vertex_groups): obj.vertex_groups.remove(g)
    g=obj.vertex_groups.new(name=bone); g.add([v.index for v in obj.data.vertices],1.0,'REPLACE')
    a=obj.modifiers.new('FC_Armature','ARMATURE'); a.object=arm
    mw=obj.matrix_world.copy(); obj.parent=arm; obj.matrix_parent_inverse=arm.matrix_world.inverted(); obj.matrix_world=mw
    return bone

def primary_mesh(objs):
    ms=[o for o in objs if o.type=='MESH' and len(o.data.vertices)>100]
    if not ms: raise RuntimeError('NO_PRIMARY_MESH')
    return max(ms,key=lambda o:len(o.data.vertices))

def build_chest(donor,body,arm):
    mn,mx=bounds(body); h=mx.z-mn.z; w=mx.x-mn.x; d=mx.y-mn.y
    c=duplicate(donor,'FC_PILOT_CHEST')
    crop_box(c,Vector((mn.x-.08*w,mn.y-.30*d,mn.z+.47*h)),Vector((mx.x+.08*w,mx.y+.45*d,mn.z+.80*h)))
    largest_component(c)
    if len(c.data.vertices)<32: raise RuntimeError(f'CHEST_CROP_TOO_SMALL:{len(c.data.vertices)}')
    offset_normals(c,.003); plate_stack(c)
    c.data.materials.clear(); c.data.materials.append(metal())
    bone=rigid_bind(c,arm,('mixamorig:Spine2','mixamorig:Spine1','Chest','chest','spine_03'))
    c['flycat_slot']='Chest'; c['flycat_rigid_bone']=bone; c['flycat_replay_version']='0.2'
    return c
