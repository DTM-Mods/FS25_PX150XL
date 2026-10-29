import bpy, json
from pathlib import Path

r = Path.cwd()
p = r / 'previews/mount_black_sockets_v1'
bpy.ops.wm.open_mainfile(filepath=str(r / 'previews/mount_color_v1/macdon_mount_orange_preview_v1.blend'))
black = bpy.data.materials['PX150XL dark graphite paint']
steel = bpy.data.materials.new('PX150XL hitch pins - bare steel preview')
steel.use_nodes = True
shader = steel.node_tree.nodes['Principled BSDF']
shader.inputs['Base Color'].default_value = (.55,.55,.56,1)
shader.inputs['Metallic'].default_value = 1
shader.inputs['Roughness'].default_value = .28
black_names = ['hitchPlate0','hitchPlate1','mountCheek0Left','mountCheek0Right',
               'mountCheek1Left','mountCheek1Right','mountFloorLeft','mountFloorRight']
steel_names = ['hitchPin','hitchPinHead','mountBoltLeft','mountBoltRight','mountKeeperLeft','mountKeeperRight']
for names, material in ((black_names,black),(steel_names,steel)):
    for name in names:
        obj = bpy.data.objects[name]
        for i in range(len(obj.data.materials)):
            obj.data.materials[i] = material
scene = bpy.context.scene
scene.render.filepath = str(p / 'macdon_mount_black_sockets_steel_pins_v1.png')
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(p / 'macdon_mount_black_sockets_steel_pins_v1.blend'))
(p / 'NOTES.md').write_text('2026-10-28 (Codex): PREVIEW ONLY. Lower socket cheeks/floors and upper hitch plates match main body black. Upper/lower pins, pin head and keeper clips use bare metallic steel. Legs/arms/caps/crossbar retain orange trim. Original reel discs stay black. Same rear-three-quarter camera as approved orange mount. Runtime not changed pending preview approval.\n')
(p / 'material_groups.json').write_text(json.dumps({'black':black_names,'steel':steel_names},indent=2))
