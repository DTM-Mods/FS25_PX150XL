import bpy
from pathlib import Path
from mathutils import Vector

p = Path.cwd() / 'previews/hd50f_adapter_v1'
out = Path.cwd() / 'previews/endcap_sticker_v2'
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
    verts, faces = [], []
    def clip(poly, distance):
        result = []
        for a, b in zip(poly, poly[1:] + poly[:1]):
            da, db = distance(a), distance(b)
            if da >= 0:
                result.append(a)
            if (da >= 0) != (db >= 0):
                result.append(a.lerp(b, da / (da - db)))
        return result
    body.data.calc_loop_triangles()
    for tri in body.data.loop_triangles:
        if tri.normal.x * side < .45:
            continue
        poly = [body.matrix_world @ body.data.vertices[i].co for i in tri.vertices]
        for distance in (lambda v: side * v.x - 7.89,
                         lambda v: .90 - v.y,
                         lambda v: .485 - (v.z - .5 * v.y)):
            poly = clip(poly, distance) if poly else []
        if len(poly) < 3:
            continue
        start = len(verts)
        verts.extend(tuple(v + Vector((side * .004, 0, 0))) for v in poly)
        faces.append(tuple(range(start, start + len(poly))))
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
    scene.render.filepath = str(out / f'endcap_sticker_{label}_v2.png')
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'endcap_sticker_preview_v2.blend'))
(out / 'NOTES.md').write_text('2026-10-28 (Codex): PREVIEW ONLY. Separate surface-projected sticker layer on both end caps, orange for coverage review, independent material. Leaves model lettering strip and rear y>0.90m bare. Fits approved cap mesh via raycast; 4mm preview offset. No runtime source changes. Orange is a demonstration color; final in-game color configuration not implemented.\n')
