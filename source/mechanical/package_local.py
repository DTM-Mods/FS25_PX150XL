from pathlib import Path
import zipfile,hashlib,xml.etree.ElementTree as E,json
root=Path(__file__).resolve().parents[2]
out=root.parent.parent/'Testing_local'/'FS25_PX150XL.zip'
files={root/'modDesc.xml'}
d=E.parse(root/'modDesc.xml').getroot();vpath=root/d.find('storeItems/storeItem').get('xmlFilename');files.add(vpath)
for e in d.iter():
 if e.tag=='iconFilename':files.add(root/e.text)
 if e.tag=='brand':files.add(root/e.get('image'))
v=E.parse(vpath).getroot();model=root/v.find('base/filename').text;files.add(model);i=E.parse(model).getroot();files.add(model.parent/i.find('Shapes').get('externalShapesFile'))
def add(name,base=root):
 if not name or name.startswith(('$','http:','https:')):return
 p=base/name
 if not p.is_file() and p.suffix.lower()=='.png':p=p.with_suffix('.dds')
 assert p.is_file(),p
 assert p.resolve().is_relative_to(root)
 files.add(p)
add(v.find('storeData/image').text)
for tree,base in [(d,root),(v,root),(i,model.parent)]:
 for e in tree.iter():
  for key in ['filename','textureFilename']:
   if e.get(key):add(e.get(key),base)
assert all(p.suffix.lower() not in ['.md','.py','.blend'] for p in files)
out.parent.mkdir(parents=True,exist_ok=True);temp=out.with_name(out.name+'.tmp')
with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(files):z.write(p,p.relative_to(root).as_posix())
with zipfile.ZipFile(temp) as z:
 assert z.testzip() is None
 assert 'modDesc.xml' in z.namelist()
 assert all('\\' not in n and not n.startswith(('previews/','Bracket_Information/','source/')) for n in z.namelist())
 for p in files:assert hashlib.sha256(z.read(p.relative_to(root).as_posix())).digest()==hashlib.sha256(p.read_bytes()).digest()
temp.replace(out)
sha=hashlib.sha256(out.read_bytes()).hexdigest()
report={'version':d.findtext('version'),'destination':str(out),'files':len(files),'bytes':out.stat().st_size,'sha256':sha,'entries':[p.relative_to(root).as_posix() for p in sorted(files)],'validation':'CRC and every entry SHA-256 match source; forward slash paths; modDesc at root','scope':'complete animated edited model, approved brackets/paint/branding and M1240 grain-swath mechanics'}
(root/'source/mechanical/local_build_manifest.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='entries'},indent=2))
