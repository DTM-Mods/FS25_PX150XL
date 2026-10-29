import bpy,xml.etree.ElementTree as E
from pathlib import Path
r=Path.cwd();p=r/'source/integration/release_2_5_1_0'
bpy.ops.wm.open_mainfile(filepath=str(r/'previews/right_label_center_v1/right_label_centered_preview.blend'))
o=bpy.data.objects['PX150XL right model'];mesh=o.data;mesh.calc_loop_triangles()
shape=E.Element('IndexedTriangleSet',name='PX150XL right model',shapeId='9900')
vs=E.SubElement(shape,'Vertices',count=str(len(mesh.loop_triangles)*3),normal='true',uv0='true',uv1='true')
ts=E.SubElement(shape,'Triangles',count=str(len(mesh.loop_triangles)))
def vec(v):return f'{v.x:.9g} {v.z:.9g} {-v.y:.9g}'
for k,t in enumerate(mesh.loop_triangles):
 for loop in t.loops:
  v=mesh.vertices[mesh.loops[loop].vertex_index];co=o.matrix_world@v.co;n=(o.matrix_world.to_3x3().inverted().transposed()@mesh.corner_normals[loop].vector).normalized()
  uv=mesh.uv_layers[0].data[loop].uv if mesh.uv_layers else (0,0)
  E.SubElement(vs,'v',p=vec(co),n=vec(n),t0=f'{uv[0]} {uv[1]}',t1=f'{uv[0]} {uv[1]}')
 E.SubElement(ts,'t',vi=f'{3*k} {3*k+1} {3*k+2}')
ss=E.SubElement(shape,'Subsets',count='1');E.SubElement(ss,'Subset',firstVertex='0',numVertices=str(len(mesh.loop_triangles)*3),firstIndex='0',numIndices=str(len(mesh.loop_triangles)*3),uvDensity0='1',uvDensity1='1')
E.ElementTree(shape).write(p/'corrected_right_label.xml',encoding='utf-8')
