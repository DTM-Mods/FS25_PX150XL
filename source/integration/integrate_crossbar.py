from pathlib import Path
import xml.etree.ElementTree as E,shutil
r=Path.cwd();p=r/'source/integration';backup=p/'v2_1_1_before_crossbar';backup.mkdir(exist_ok=True)
for n in ['px150xlWindrower.i3d','px150xlWindrower.i3d.shapes']:
 if not (backup/n).exists():shutil.copy2(r/n,backup/n)
i=E.parse(r/'px150xlWindrower.i3d').getroot();a=E.parse(p/'approved_crossbar.i3d').getroot();assert len(a.findall('Shapes/IndexedTriangleSet'))==1
shape=a.find('Shapes/IndexedTriangleSet');shape.set('shapeId','9001');i.find('Shapes').append(shape)
black=next(m.get('materialId') for m in i.findall('Materials/Material') if m.get('name')=='PX150XL_bracket_black')
node=a.find('Scene/Shape');node.set('shapeId','9001');node.set('materialIds',black);node.set('nodeId',str(max(int(e.get('nodeId','0')) for e in i.iter())+1));i.find('Scene/Shape').append(node)
brand=next(e for e in i.iter() if e.get('name')=='PropaineX rear brand');brand.set('translation','0.65 1.24 -1.323')
E.indent(i,space='  ');E.ElementTree(i).write(p/'crossbar_integrated_unoptimized.i3d',encoding='utf-8',xml_declaration=True)
# External shape reference resolved by existing integration copy from the complete binary.
shutil.copy2(r/'px150xlWindrower.i3d.shapes',p/'px150xlWindrower.i3d.shapes')
print('Approved crossbar integrated into scratch source. Lowered angle unchanged.')
