import bpy, json
from pathlib import Path
from mathutils import Vector

r = Path.cwd()
p = r / 'previews/reel_discs_color_v1'
bpy.ops.wm.open_mainfile(filepath=str(r / 'previews/header_front_angle_v1/px150xl_full_front_angle_v1.blend'))
obj = bpy.data.objects['headerHD50F_vis']
islands = json.loads((p / 'disc_islands.json').read_text())
discs = [a for a in islands if a['max'][0]-a['min'][0] < .02 and a['verts'] == 326]
assert len(discs) == 2
ids = {i for a in discs for i in a['ids']}
material = bpy.data.materials['End cap sticker - demonstration orange']
obj.data.materials.append(material)
index = len(obj.data.materials)-1
selected = []
for poly in obj.data.polygons:
    if all(i in ids for i in poly.vertices):
        selected.append((poly, poly.material_index))
        poly.material_index = index
assert selected
scene = bpy.context.scene
scene.render.filepath = str(p / 'px150xl_matching_reel_discs_wide_v1.png')
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(p / 'px150xl_matching_reel_discs_v1.blend'))
scene.camera.location = (11.5, -4, 2.8)
scene.camera.rotation_euler = (Vector((7.55, -.1, .85))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera.data.ortho_scale = 3.8
scene.render.resolution_x = 1200
scene.render.resolution_y = 900
for after, label in ((False, 'before'), (True, 'after')):
    for poly, original in selected:
        poly.material_index = index if after else original
    scene.render.filepath = str(p / f'reel_disc_detail_{label}_v1.png')
    bpy.ops.render.render(write_still=True)
(p / 'NOTES.md').write_text(f'2026-10-28 (Codex): PREVIEW ONLY. Both outer reel discs assigned same orange preview material as end-cap sticker. Selected exactly two disconnected thin circular mesh islands (326 vertices each), x ranges +/-7.45077..7.46624, Blender y[-1.45566,-.25566],z[.29745,1.49745]. Reassigned {len(selected)} faces; geometry/holes/tines/supports unchanged. Wide front-angle and same-camera detail before/after rendered. Runtime and shop option unchanged pending approval.\n')
