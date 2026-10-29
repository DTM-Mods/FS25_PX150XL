import bpy,json
from pathlib import Path
r=Path.cwd();p=r/'previews/mount_fixed_steel_pins_v1'
bpy.ops.wm.open_mainfile(filepath=str(r/'previews/mount_black_sockets_v1/macdon_mount_black_sockets_steel_pins_v1.blend'))
groups=json.loads((r/'previews/mount_black_sockets_v1/material_groups.json').read_text())
orange=bpy.data.materials['End cap sticker - demonstration orange']
for name in groups['black']:
 o=bpy.data.objects[name]
 for i in range(len(o.data.materials)):o.data.materials[i]=orange
bpy.ops.wm.save_as_mainfile(filepath=str(p/'working_trim_with_steel_pins_v1.blend'))
