"""Export only the approved sticker surfaces, with their own FS25 material slot."""
from pathlib import Path
import xml.etree.ElementTree as E
import bpy

root = Path.cwd()
out = root / 'source/integration/endcap_color_build'
bpy.ops.wm.open_mainfile(filepath=str(root / 'previews/endcap_sticker_v5/endcap_sticker_preview_v5.blend'))
asset = E.Element('i3D', name='PX150XL approved end cap stickers', version='1.6')
shapes = E.SubElement(asset, 'Shapes')
scene = E.SubElement(asset, 'Scene')

def vector(v):
    return f'{v.x:.9g} {v.z:.9g} {-v.y:.9g}'

for number, side in enumerate((1, -1), 1):
    obj = bpy.data.objects[f'End cap sticker {side}']
    assert obj.matrix_world.is_identity
    mesh = obj.data
    mesh.calc_loop_triangles()
    shape = E.SubElement(shapes, 'IndexedTriangleSet', name=f'endCapSticker{number}', shapeId=str(number))
    count = len(mesh.loop_triangles) * 3
    vertices = E.SubElement(shape, 'Vertices', count=str(count), normal='true', uv0='true', uv1='true')
    triangles = E.SubElement(shape, 'Triangles', count=str(len(mesh.loop_triangles)))
    for index, tri in enumerate(mesh.loop_triangles):
        for loop in tri.loops:
            co = mesh.vertices[mesh.loops[loop].vertex_index].co
            normal = mesh.corner_normals[loop].vector
            uv = f'{co.y:.9g} {co.z:.9g}'
            E.SubElement(vertices, 'v', p=vector(co), n=vector(normal), t0=uv, t1=uv)
        E.SubElement(triangles, 't', vi=f'{index*3} {index*3+1} {index*3+2}')
    subsets = E.SubElement(shape, 'Subsets', count='1')
    E.SubElement(subsets, 'Subset', firstVertex='0', numVertices=str(count), firstIndex='0',
                 numIndices=str(count), materialSlotName='px150_endCapSticker', uvDensity0='1', uvDensity1='1')
    E.SubElement(scene, 'Shape', name=f'endCapSticker{number}', shapeId=str(number), nodeId=str(number))
    print(f'Exported {obj.name}: {len(mesh.loop_triangles)} triangles, slot px150_endCapSticker')
E.indent(asset, space='  ')
E.ElementTree(asset).write(out / 'approved_stickers.i3d', encoding='utf-8', xml_declaration=True)
