from pathlib import Path
import xml.etree.ElementTree as E,shutil,json,re
r=Path.cwd();p=r/'source/integration/release_2_5_1_0'
def split(v):return re.split(r'[ ,]+',v)
def nodes(file):
 root=E.parse(file).getroot();out={}
 def visit(n,path):
  out[path]=n
  for k,ch in enumerate(n):visit(ch,path+(k,))
 visit(root.find('Scene'),());return root,out,{n.get('nodeId'):path for path,n in out.items() if n.get('nodeId')}
a,x,xi=nodes(p/'before/px150xlWindrower.i3d');b,y,yi=nodes(p/'px150xlWindrower.i3d');assert x.keys()==y.keys()
am={n.get('materialId'):n.get('name') for n in a.findall('Materials/Material')};bm={n.get('materialId'):n.get('name') for n in b.findall('Materials/Material')}
for path,n in x.items():
 nn=y[path];assert n.tag==nn.tag
 for k,v in n.attrib.items():
  if k in ['nodeId','shapeId']:continue
  if k=='materialIds':assert [am[j] for j in split(v)]==[bm[j] for j in split(nn.get(k))];continue
  if k=='skinBindNodeIds':assert [xi[j] for j in split(v)]==[yi[j] for j in split(nn.get(k))];continue
  if n.get('name')=='PX150XL right model' and k in ['translation','rotation']:continue
  assert nn.get(k)==v,(path,k,v,nn.get(k))
assert not b.findall('Shapes/IndexedTriangleSet')
for n in ['px150xlWindrower.i3d','px150xlWindrower.i3d.shapes']:shutil.copy2(p/n,r/n)
qa=p/'FS25_PX150XL';qa.mkdir(exist_ok=True);files=json.loads((r/'source/mechanical/local_build_manifest.json').read_text())['entries'];files=sorted(set(files+['scripts/PX150ShopDisplay.lua']))
for n in files:
 dst=qa/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/n,dst)
print('Compiled label integrated; hierarchy, materials and skin-binding targets preserved;',len(files),'runtime files staged')
