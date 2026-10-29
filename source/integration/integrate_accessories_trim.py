"""Bind approved mount geometry to the existing end-cap shop color slot."""
from pathlib import Path
import copy, shutil, json
import xml.etree.ElementTree as E

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / 'source/integration/accessories_trim_build'
BACKUP = BUILD / 'before_2_3_0_0'
BACKUP.mkdir(parents=True, exist_ok=True)
QA = BUILD / 'FS25_PX150XL'
QA.mkdir(exist_ok=True)
for name in ('modDesc.xml','px150xlWindrower.xml','px150xlWindrower.i3d','px150xlWindrower.i3d.shapes'):
    if not (BACKUP / name).exists(): shutil.copy2(ROOT / name, BACKUP / name)
for name in json.loads((ROOT / 'source/mechanical/local_build_manifest.json').read_text())['entries']:
    dest = QA / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / name, dest)
model = E.parse(ROOT / 'px150xlWindrower.i3d')
root = model.getroot()
material_id = next(m.get('materialId') for m in root.findall('Materials/Material') if m.get('name')=='PX150XL_endCapSticker_mat')
sources = {}
for file in ('approved_mount_and_labels.i3d','approved_crossbar.i3d'):
    a = E.parse(ROOT / 'source/integration' / file).getroot()
    shapes = {s.get('shapeId'):s for s in a.findall('Shapes/IndexedTriangleSet')}
    for n in a.findall('.//Shape'):
        name = n.get('name','')
        if name.startswith(('mount','hitch')) or name=='PX150XL_square_steel_crossbar':
            sources[name] = copy.deepcopy(shapes[n.get('shapeId')])
assert len(sources)==21
for index, (name, shape) in enumerate(sources.items()):
    target = next(n for n in root.iter('Shape') if n.get('name')==name)
    shape_id = str(9200+index)
    shape.set('shapeId', shape_id)
    for subset in shape.findall('Subsets/Subset'):
        subset.set('materialSlotName','px150_endCapSticker')
    root.find('Shapes').append(shape)
    target.set('shapeId',shape_id)
    target.set('materialIds',material_id)
E.indent(model,space='  ')
model.write(QA/'px150xlWindrower.i3d',encoding='utf-8',xml_declaration=True)
p=QA/'px150xlWindrower.xml'
p.write_text(p.read_text(encoding='utf-8').replace('$l10n_px150_endCapColor','$l10n_px150_accessoriesTrim'),encoding='utf-8')
p=QA/'modDesc.xml'
s=p.read_text(encoding='utf-8').replace('<version>2.3.0.0</version>','<version>2.4.0.0</version>')
s=s.replace('name="px150_endCapColor"','name="px150_accessoriesTrim"').replace('<en>End cap color</en>','<en>Accessories and trim</en>').replace('<de>Endkappenfarbe</de>','<de>Zubehoer und Zierleisten</de>')
english,german=s.split('<de><![CDATA[',1)
english=english.replace('Changelog 2.3.0.0:', 'Changelog 2.4.0.0:\n- Accessories and trim color option now recolors both end-cap stickers and the complete custom MacDon attacher together, for $250.\n\nChangelog 2.3.0.0:',1)
german=german.replace('Changelog 2.3.0.0:', 'Changelog 2.4.0.0:\n- Gemeinsame Farbwahl fuer Endkappenaufkleber und kompletten eigenen MacDon-Anbaurahmen fuer $250.\n\nChangelog 2.3.0.0:',1)
p.write_text(english+'<de><![CDATA['+german,encoding='utf-8')
(BUILD/'bound_mount_parts.json').write_text(json.dumps(list(sources),indent=2))
print('Staged2.4.0.0:21 custom mount shapes +2 end-cap stickers, one $250 Accessories and trim color option.')
