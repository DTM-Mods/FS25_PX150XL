import bpy,bmesh,pathlib,math
from mathutils import Vector
p=pathlib.Path.cwd()/'previews/hd50f_adapter_v1'
bpy.ops.wm.open_mainfile(filepath=str(p/'grouped_source.blend'))
def mat(name,color,metal=.0,texture=None,alpha=False):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;s=n.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Metallic'].default_value=metal;s.inputs['Roughness'].default_value=.37
 if texture:
  t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(p/'render_textures'/texture))
  if alpha:
   tr=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');l.new(t.outputs['Alpha'],mix.inputs[0]);l.new(tr.outputs[0],mix.inputs[1]);l.new(s.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],n.get('Material Output').inputs['Surface'])
  else:l.new(t.outputs['Color'],s.inputs['Base Color'])
 return m
green=mat('John Deere painted green',(.0236,.2133,.027),.25);black=mat('Black painted steel',(.012,.012,.012),.35);rubber=mat('Rubber',(.015,.018,.02));steel=mat('Brushed steel',(.5,.54,.57),.8)
alpha=mat('Reel cutout',(.012,.012,.012),.25,'headerAlpha_diffuse.png',True)
blades=mat('Cutter cutout',(.16,.17,.18),.8,'headerBlades02_diffuse.png',True)
decal=mat('Factory decals',(.85,.85,.85),.1,'headerHD50FDecals_diffuse.png',True)
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 name=o.name
 if name.startswith(('headerHD50F_main_component','colPart','canola','alpha03','smokeEmitter','drumMain_decals')):
  bpy.data.objects.remove(o,do_unlink=True);continue
 for v in o.data.vertices:v.co=(o.matrix_world@v.co)*.01
 o.matrix_world.identity();o.data.materials.clear()
 chosen=green
 if name.startswith(('hoses','belt')):chosen=rubber
 if name.startswith(('reelAlpha','spikes')):chosen=alpha
 if name.startswith('knifesAlpha'):chosen=blades
 if name.startswith(('logos','screws')):chosen=decal
 o.data.materials.append(chosen)
 if name=='headerHD50F_vis':
  o.data.materials.append(black);o.data.materials.append(steel)
  for f in o.data.polygons:
   c=f.center
   # Reel framework ahead of the back beam is black; frame remains green.
   if c.y<-.30 and c.z>.48:f.material_index=1
  bm=bmesh.new();bm.from_mesh(o.data)
  remove=[v for v in bm.verts if abs(v.co.x)<1.30 and v.co.y>1.035 and .10<v.co.z<1.30]
  bmesh.ops.delete(bm,geom=remove,context='VERTS')
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
  seen=set();remove=[]
  for v in bm.verts:
   if v in seen:continue
   todo=[v];seen.add(v);part=[]
   while todo:
    a=todo.pop();part.append(a)
    for e in a.link_edges:
     b=e.other_vert(a)
     if b not in seen:seen.add(b);todo.append(b)
   lo=[min(v.co[i] for v in part) for i in range(3)];hi=[max(v.co[i] for v in part) for i in range(3)]
   if lo[0]>-1.01 and hi[0]<1.01 and lo[1]>.55 and hi[1]<1.02 and lo[2]>.39 and hi[2]<.89:remove.extend(part)
  bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(o.data);bm.free()
 o.data.update()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.world.color=(.35,.35,.35)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.07));floor=bpy.context.object;floor.name='Neutral ground';floor.data.materials.append(mat('Ground',(.19,.21,.18)))
for loc,power,size in [((1,1,9),2200,8),((-6,3,5),1600,7),((3,-5,7),2000,6)]:
 d=bpy.data.lights.new('Soft daylight','AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new('Soft daylight',d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Rear preview');o=bpy.data.objects.new('Rear preview',d);scene.collection.objects.link(o);o.location=(3.6,6,2.9);o.rotation_euler=(Vector((0,.85,.85))-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=5.3;scene.camera=o
scene.render.resolution_x=1800;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
scene.render.filepath=str(p/'textured_rear_v1.png');bpy.ops.wm.save_as_mainfile(filepath=str(p/'textured_preview_v1.blend'));bpy.ops.render.render(write_still=True)
