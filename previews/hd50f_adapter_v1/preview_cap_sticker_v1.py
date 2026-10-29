import bpy
from pathlib import Path
from mathutils import Vector

p = Path.cwd() / 'previews/hd50f_adapter_v1'
out = Path.cwd() / 'previews/endcap_sticker_v1'
out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(p / 'px150xl_endcap_parallel_top_v1.blend'))
body = bpy.data.objects['headerHD50F_vis']
mat = bpy.data.materials.new('End cap sticker - demonstration orange')
mat.diffuse_color = (0.8, 0.16, 0.018, 1)
mat.use_nodes = True
shader = mat.node_tree.nodes['Principled BSDF']
shader.inputs['Base Color'].default_value = mat.diffuse_color
shader.inputs['Roughness'].default_value = .38
decals = []
for side in (1, -1):
    verts, faces, indices = [], [], {}
    step = .012
    # Sticker lower field, excluding model-number strip and the rear of the cap.
    for iy in range(211):
        y = -1.4 + iy * step
        for iz in range(131):
            z = -.15 + iz * step
            if y > .90 or (y > -.035 and z - .5 * y > .485):
                continue
            hit, point, normal, face = body.ray_cast(Vector((side * 9, y, z)), Vector((-side, 0, 0)))
            if not hit or side * point.x < 7.89 or side * normal.x < .45:
                continue
            indices[iy, iz] = len(verts)
            verts.append(tuple(point + normal * .004))
    for (iy, iz), a in indices.items():
        keys = [(iy+1, iz), (iy+1, iz+1), (iy, iz+1)]
        if all(k in indices for k in keys):
            face = (a, *(indices[k] for k in keys))
            faces.append(face if side > 0 else face[::-1])
    mesh = bpy.data.meshes.new(f'End cap sticker {side}')
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(mesh.name, mesh)
    bpy.context.collection.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = True
    decals.append(obj)

scene = bpy.context.scene
scene.cycles.samples = 24
scene.render.resolution_x = 1200
scene.render.resolution_y = 850
scene.render.resolution_percentage = 100
scene.camera.location = (11.5, 3.6, 2.0)
scene.camera.rotation_euler = (Vector((7.65, .65, .8)) - scene.camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera.data.ortho_scale = 3.0
for visible, label in ((False, 'before'), (True, 'after')):
    for obj in decals:
        obj.hide_render = not visible
    scene.render.filepath = str(out / f'endcap_sticker_{label}_v1.png')
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'endcap_sticker_preview_v1.blend'))
(out / 'NOTES.md').write_text('2026-10-28 (Codex): PREVIEW ONLY. Separate surface-projected sticker layer on both end caps, orange for coverage review, independent material. Leaves model lettering strip and rear y>0.90m bare. Fits approved cap mesh via raycast; 4mm preview offset. No runtime source changes. Orange is a demonstration color; final in-game color configuration not implemented.\n')
