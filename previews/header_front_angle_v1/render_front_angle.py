import bpy
from pathlib import Path
from mathutils import Vector

r = Path.cwd()
p = r / 'previews/header_front_angle_v1'
bpy.ops.wm.open_mainfile(filepath=str(r / 'previews/endcap_sticker_v5/endcap_sticker_preview_v5.blend'))
# Include the approved cross tube without disturbing the retained preview model.
with bpy.data.libraries.load(str(r / 'previews/crossbar_v1/crossbar_mockup.blend'), link=False) as (src, dst):
    dst.objects = [name for name in src.objects if name == 'PX150XL_square_steel_crossbar']
for obj in dst.objects:
    if obj:
        bpy.context.collection.objects.link(obj)
scene = bpy.context.scene
scene.cycles.samples = 32
scene.render.resolution_x = 1800
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.camera.location = (13, -22, 8)
scene.camera.rotation_euler = (Vector((0, 0, .7)) - scene.camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera.data.ortho_scale = 18.8
scene.render.filepath = str(p / 'px150xl_full_front_angle_v1.png')
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(p / 'px150xl_full_front_angle_v1.blend'))
