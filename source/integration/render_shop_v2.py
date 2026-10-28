import bpy,pathlib
from mathutils import Vector
r=pathlib.Path.cwd();p=r/'source/integration'
bpy.ops.wm.open_mainfile(filepath=str(r/'previews/hd50f_adapter_v1/px150xl_endcap_parallel_top_v1.blend'))
scene=bpy.context.scene;scene.cycles.samples=48;scene.render.resolution_x=2048;scene.render.resolution_y=1024;scene.render.resolution_percentage=100
bpy.data.objects['Neutral ground'].hide_render=True;scene.render.film_transparent=True
for m in bpy.data.materials:
 if m.use_nodes and m.name=='PX150XL dark graphite paint':
  s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Metallic'].default_value=.12;s.inputs['Roughness'].default_value=.48
for o in bpy.data.objects:
 if o.type=='LIGHT':o.data.energy*=.7
cam=scene.camera;cam.location=(20,-11,5.0);cam.rotation_euler=(Vector((0,0,.65))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=12.5
scene.render.filepath=str(p/'shop_px150xl_hero_v2.png');bpy.ops.render.render(write_still=True)
