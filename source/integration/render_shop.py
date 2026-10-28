import bpy,pathlib
from mathutils import Vector
r=pathlib.Path.cwd();p=r/'source/integration'
bpy.ops.wm.open_mainfile(filepath=str(r/'previews/hd50f_adapter_v1/px150xl_endcap_parallel_top_v1.blend'))
scene=bpy.context.scene;scene.cycles.samples=32;scene.render.resolution_x=2048;scene.render.resolution_y=1024;scene.render.resolution_percentage=100
bpy.data.objects['Neutral ground'].hide_render=True;scene.render.film_transparent=True
cam=scene.camera;cam.location=(14,-19,8);cam.rotation_euler=(Vector((0,0,.65))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=19.5
scene.render.filepath=str(p/'shop_px150xl_hero.png');bpy.ops.render.render(write_still=True)
