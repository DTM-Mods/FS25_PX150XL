import bpy
from pathlib import Path
from mathutils import Vector
r=Path.cwd();p=r/'previews/macdon_red_default_v1'
bpy.ops.wm.open_mainfile(filepath=str(r/'previews/right_label_center_v1/right_label_centered_preview.blend'))
s=bpy.context.scene;s.cycles.samples=16;s.render.resolution_x=1200;s.render.resolution_y=750
cam=s.camera;cam.location=(-17,10,6);cam.rotation_euler=(Vector((0,0,.65))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=18.8
s.render.filepath=str(p/'before.png');bpy.ops.render.render(write_still=True)
m=bpy.data.materials['End cap sticker - demonstration orange'];m.diffuse_color=(.2775,.0016,0,1);m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=m.diffuse_color
bpy.ops.wm.save_as_mainfile(filepath=str(p/'macdon_red_default_preview.blend'))
s.render.filepath=str(p/'after.png');bpy.ops.render.render(write_still=True)
