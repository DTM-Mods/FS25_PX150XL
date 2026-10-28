from pathlib import Path
import xml.etree.ElementTree as E,copy
p=Path('source/integration');r=E.parse(p/'animated_edited_test.i3d').getroot();a=E.parse(p/'approved_mount_and_labels.i3d').getroot()
# Independent clean materials for our bracket and lettering geometry.
E.SubElement(r.find('Files'),'File',fileId='90',filename='$data/shared/default_vmask.png')
material_map={'3':'203','21':'202','23':'201'}
for old,new,color in [('23','201','0.02 0.02 0.02'),('21','202','0.55 0.55 0.56'),('3','203','0.88 0.88 0.85')]:
 source='5' if old=='21' else '3';m=copy.deepcopy(next(x for x in r.findall('Materials/Material') if x.get('materialId')==source));m.set('materialId',new);m.set('name',{'201':'PX150XL_bracket_black','202':'PX150XL_bracket_steel','203':'PX150XL_lettering_white'}[new])
 cp=next((x for x in m.findall('CustomParameter') if x.get('name')=='colorScale'),None)
 if cp is None:cp=E.SubElement(m,'CustomParameter',name='colorScale')
 cp.set('value',color);m.find('Normalmap').set('fileId','33');m.find('Glossmap').set('fileId','90');r.find('Materials').append(m)
for m in r.findall('Materials/Material'):
 if m.get('materialId') in ['3','7','23']:
  cp=next((x for x in m.findall('CustomParameter') if x.get('name')=='colorScale'),None)
  if cp is not None:cp.set('value','0.016 0.018 0.020')
shape_map={s.get('shapeId'):str(1100+i) for i,s in enumerate(a.findall('Shapes/IndexedTriangleSet'))}
for s in a.findall('Shapes/IndexedTriangleSet'):
 s.set('shapeId',shape_map[s.get('shapeId')]);r.find('Shapes').append(s)
component=r.find('Scene/Shape');nodeid=max(int(e.get('nodeId','0')) for e in r.iter())+1
for top in a.findall('Scene/*'):
 for e in top.iter():
  if e.get('nodeId'):e.set('nodeId',str(nodeid));nodeid+=1
  if e.get('shapeId'):e.set('shapeId',shape_map[e.get('shapeId')])
  if e.get('materialIds'):e.set('materialIds',' '.join(material_map[x] for x in e.get('materialIds').split()))
 component.append(top)
# Reference actual silver hitch pin so the M1240 top link meets the installed bracket.
for e in r.iter():
 if e.get('name')=='topReferenceM1240':e.set('translation','0 1.385 -1.325')
E.indent(r,space='  ');E.ElementTree(r).write(p/'final_unoptimized.i3d',encoding='utf-8',xml_declaration=True)
print('Final asset:',len(r.findall('Shapes/IndexedTriangleSet')),'new shapes; animated main + brackets + branding merged')
