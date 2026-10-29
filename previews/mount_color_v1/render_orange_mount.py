import bpy, json
from pathlib import Path
from mathutils import Vector

r = Path.cwd()
p = r / 'previews/mount_color_v1'
# Start from the scene with original black reel discs.
bpy.ops.wm.open_mainfile(filepath=str(r / 'previews/header_front_angle_v1/px150xl_full_front_angle_v1.blend'))
orange = bpy.data.materials['End cap sticker - demonstration orange']
parts = [o for o in bpy.data.objects if o.type == 'MESH' and
         (o.name.startswith(('mount', 'hitch')) or o.name == 'PX150XL_square_steel_crossbar')]
assert len(parts) >= 20
original = {o.name: list(o.data.materials) for o in parts}
scene = bpy.context.scene
scene.cycles.samples = 32
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.camera.location = (6, 9, 4)
scene.camera.rotation_euler = (Vector((0, .6, .55))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera.data.ortho_scale = 7.4
for after, label in ((False, 'before'), (True, 'after')):
    if after:
        for obj in parts:
            for i in range(len(obj.data.materials)):
                obj.data.materials[i] = orange
    scene.render.filepath = str(p / f'macdon_mount_rear_three_quarter_{label}_v1.png')
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(p / 'macdon_mount_orange_preview_v1.blend'))
(p / 'NOTES.md').write_text('2026-10-28 (Codex): PREVIEW ONLY. User rejected matching orange reel discs; source scene retains original black discs. Requested entire scratch-built M1240 attacher in same orange as end-cap sticker: all mount/hitch meshes and square crossbar recolored, branding retained. Same-camera rear three-quarter before/after. Runtime and shop configuration unchanged pending preview approval. Parts: ' + ', '.join(o.name for o in parts) + '\n')
(p / 'recolored_parts.json').write_text(json.dumps([o.name for o in parts], indent=2))
