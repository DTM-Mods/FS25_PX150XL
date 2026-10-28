import bpy,pathlib
from mathutils import Vector
p=pathlib.Path.cwd()/'previews/crossbar_v1';bpy.ops.wm.open_mainfile(filepath=str(p/'crossbar_mockup.blend'))
scene=bpy.context.scene;scene.cycles.samples=24;scene.render.resolution_x=1400;scene.render.resolution_y=950
cam=scene.camera;cam.location=(2.5,4.8,4.3);cam.rotation_euler=(Vector((0,1.1,1.15))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=4.3
bar=bpy.data.objects['PX150XL_square_steel_crossbar'];brand=bpy.data.objects['PropaineX rear brand']
bar.hide_render=True;brand.location.y=1.322;brand.location.z=1.23;scene.render.filepath=str(p/'before_crossbar_upper_view.png');bpy.ops.render.render(write_still=True)
bar.hide_render=False;brand.location.y=1.323;brand.location.z=1.24;scene.render.filepath=str(p/'after_crossbar_upper_view.png');bpy.ops.render.render(write_still=True)
