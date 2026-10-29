"""Build convex compound children from the approved bracket's supported ASCII export.

Keeps each cheek separate so the lift-arm sockets remain open. Does not package.
"""
from pathlib import Path
import json
import shutil
import xml.etree.ElementTree as E
import numpy as np
from scipy.spatial import ConvexHull

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'source/integration/bracket_collision_build'
OUT.mkdir(exist_ok=True)
BACKUP = OUT / 'before'
BACKUP.mkdir(exist_ok=True)
for name in ('px150xlWindrower.i3d', 'px150xlWindrower.i3d.shapes'):
    if not (BACKUP / name).exists():
        shutil.copy2(ROOT / name, BACKUP / name)
    shutil.copy2(ROOT / name, OUT / name)

tree = E.parse(ROOT / 'px150xlWindrower.i3d')
root = tree.getroot()
approved = E.parse(ROOT / 'source/integration/approved_mount_and_labels.i3d').getroot()
source_shapes = {s.get('shapeId'): s for s in approved.findall('Shapes/IndexedTriangleSet')}
mount = next(n for n in root.iter() if n.get('name') == 'px150Mount')
assert not any(n.get('name', '').startswith('colMount') for n in root.iter())
collision_group = next(n for n in root.iter() if n.get('name') == 'collisions')
node_id = max(int(n.get('nodeId', '0')) for n in root.iter()) + 1
report = []
for source in approved.findall('Scene/TransformGroup/Shape'):
    name = source.get('name')
    if not name.startswith(('mountArm', 'mountPost', 'mountCap', 'mountFloor', 'mountCheek')):
        continue
    runtime = next(n for n in mount if n.get('name') == name)
    assert all(runtime.get(k, '0 0 0') == '0 0 0' for k in ('translation', 'rotation'))
    points = np.unique(np.array([list(map(float, v.get('p').split()))
                                for v in source_shapes[source.get('shapeId')].findall('Vertices/v')]), axis=0)
    hull = ConvexHull(points)
    used = sorted(set(hull.simplices.flatten()))
    index = {v: i for i, v in enumerate(used)}
    shape_id = str(9000 + len(report))
    mesh = E.SubElement(root.find('Shapes'), 'IndexedTriangleSet',
                        name='col' + name[0].upper() + name[1:], shapeId=shape_id)
    vertices = E.SubElement(mesh, 'Vertices', count=str(len(used)))
    for i in used:
        E.SubElement(vertices, 'v', p=' '.join(f'{x:.9g}' for x in points[i]))
    triangles = E.SubElement(mesh, 'Triangles', count=str(len(hull.simplices)))
    for tri, equation in zip(hull.simplices, hull.equations):
        a, b, c = map(int, tri)
        if np.dot(np.cross(points[b] - points[a], points[c] - points[a]), equation[:3]) < 0:
            b, c = c, b
        E.SubElement(triangles, 't', vi=f'{index[a]} {index[b]} {index[c]}')
    subsets = E.SubElement(mesh, 'Subsets', count='1')
    E.SubElement(subsets, 'Subset', firstVertex='0', numVertices=str(len(used)),
                 firstIndex='0', numIndices=str(3 * len(hull.simplices)))
    E.SubElement(collision_group, 'Shape', name='col' + name[0].upper() + name[1:],
                 shapeId=shape_id, nodeId=str(node_id), compoundChild='true',
                 collisionFilterGroup='0x10004', collisionFilterMask='0xfe3ffb83',
                 density='0.001', nonRenderable='true', materialIds='21')
    node_id += 1
    report.append(dict(source=name, vertices=len(used), triangles=len(hull.simplices),
                       minimum=points[used].min(axis=0).tolist(), maximum=points[used].max(axis=0).tolist()))
assert len(report) == 12
E.indent(tree, space='  ')
tree.write(OUT / 'px150xlWindrower.i3d', encoding='utf-8', xml_declaration=True)
(OUT / 'collision_geometry.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
