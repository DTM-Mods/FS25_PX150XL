from pathlib import Path
import xml.etree.ElementTree as E,numpy as np,json
r=Path.cwd();p=r/'source/integration';v=[];uv=[];norm=[];faces=[];group=''
for line in (p/'rig_rest.obj').open():
 if line.startswith('g '):group=line.strip()[2:]
 elif line.startswith('v '):v.append([float(x)/100 for x in line.split()[1:]])
 elif line.startswith('vt '):uv.append([float(x) for x in line.split()[1:3]])
 elif line.startswith('vn '):norm.append([float(x) for x in line.split()[1:4]])
 elif line.startswith('f ') and group=='headerHD50F_vis':faces.append([[int(a)-1 for a in x.split('/')] for x in line.split()[1:]])
v=np.array(v);uv=np.array(uv);norm=np.array(norm);binding=np.load(p/'rig_binding.npz');bone={int(k):int(b) for k,b in zip(binding['vertex_ids'],binding['bone_indices'])}
# Physical removal of combine receiver, complete drum/fingers, combine coupler and support gear.
remove=set()
for k,b in bone.items():
 x,y,z=v[k]
 if b in (1,2,3,4,5) or (b==0 and abs(x)<1.30 and z< -1.035 and .10<y<1.30):remove.add(k)
keep=[f for f in faces if not any(x[0] in remove for x in f)]
keys=sorted({tuple(x) for f in keep for x in f});remap={k:i for i,k in enumerate(keys)}
i=E.parse(r/'px150xlWindrower.i3d').getroot();shapes=i.find('Shapes');s=E.SubElement(shapes,'IndexedTriangleSet',name='PX150XL_edited_animated_main',shapeId='1001',isOptimized='false',bvCenter='0 0.8 0',bvRadius='9')
ve=E.SubElement(s,'Vertices',count=str(len(keys)),normal='true',tangent='true',uv0='true',singleblendweights='true')
fmt=lambda a:' '.join(f'{float(x):.8g}' for x in a)
for vi,ti,ni in keys:E.SubElement(ve,'v',p=fmt(v[vi]),n=fmt(norm[ni]),t0=fmt(uv[ti]),bi=str(bone[vi]))
tr=E.SubElement(s,'Triangles',count=str(len(keep)))
for f in keep:E.SubElement(tr,'t',vi=' '.join(str(remap[tuple(x)]) for x in f))
ss=E.SubElement(s,'Subsets',count='1');E.SubElement(ss,'Subset',firstVertex='0',numVertices=str(len(keys)),firstIndex='0',numIndices=str(len(keep)*3),materialSlotName='px150xl_graphite_main')
main=next(e for e in i.iter('Shape') if e.get('name')=='headerHD50F_vis');main.set('shapeId','1001');main.set('materialIds','3')
mat=next(e for e in i.findall('Materials/Material') if e.get('materialId')=='3')
for cp in mat.findall('CustomParameter'):
 if cp.get('name')=='colorScale':cp.set('value','0.016 0.018 0.020')
# Remove the original branding and separately drawn combine coupler/drum decals. Preserve node indices.
stripped=[]
for e in i.iter():
 if e.get('name') in ['johnDeereMultiCoupler','hosesDetached','logos_decals','drumMain_decals'] and e.tag=='Shape':
  e.tag='TransformGroup'
  for a in ['shapeId','materialIds','skinBindNodeIds','castsShadows','receiveShadows','decalLayer']:e.attrib.pop(a,None)
  stripped.append(e.get('name'))
E.indent(i,space='  ');E.ElementTree(i).write(p/'animated_edited_test.i3d',encoding='utf-8',xml_declaration=True)
# External unchanged shape resource and texture references need to resolve at this scratch location.
import shutil
shutil.copy2(r/'headerHD50F.i3d.shapes',p/'headerHD50F.i3d.shapes')
if not (p/'textures').exists():shutil.copytree(r/'textures',p/'textures')
(p/'mesh_rebuild_report.json').write_text(json.dumps({'original_main_faces':len(faces),'retained_main_faces':len(keep),'physically_removed_vertices':len(remove),'retained_vertices':len(keys),'recovered_bone_count':23,'remaining_bone_indices':sorted({bone[k[0]] for k in keys}),'stripped_shapes':stripped},indent=2))
print((p/'mesh_rebuild_report.json').read_text())
