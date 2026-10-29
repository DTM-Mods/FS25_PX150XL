import bpy
from pathlib import Path
from mathutils import Vector

r = Path.cwd()
p = r / 'previews/front_chute_closeup_v1'
bpy.ops.wm.open_mainfile(filepath=str(r / 'previews/mount_color_v1/macdon_mount_orange_preview_v1.blend'))
scene = bpy.context.scene
scene.cycles.samples = 32
scene.render.resolution_x = 1600
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.camera.location = (0, -7, 2.5)
scene.camera.rotation_euler = (Vector((0, .35, .45))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera.data.ortho_scale = 4.5
scene.render.filepath = str(p / 'px150xl_center_chute_front_closeup_v1.png')
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(p / 'px150xl_center_chute_front_closeup_v1.blend'))
