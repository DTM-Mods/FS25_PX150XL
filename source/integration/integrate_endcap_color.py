"""Stage the approved stickers and the native, isolated shop color configuration."""
from pathlib import Path
import copy
import json
import shutil
import xml.etree.ElementTree as E

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / 'source/integration/endcap_color_build'
BACKUP = BUILD / 'before_2_2_1_0'
BACKUP.mkdir(exist_ok=True)
QA = BUILD / 'FS25_PX150XL'
QA.mkdir(exist_ok=True)
for name in ('modDesc.xml', 'px150xlWindrower.xml', 'px150xlWindrower.i3d', 'px150xlWindrower.i3d.shapes'):
    if not (BACKUP / name).exists():
        shutil.copy2(ROOT / name, BACKUP / name)
manifest = json.loads((ROOT / 'source/mechanical/local_build_manifest.json').read_text())
for name in manifest['entries']:
    dest = QA / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / name, dest)

model = E.parse(ROOT / 'px150xlWindrower.i3d')
root = model.getroot()
assert not any(m.get('name') == 'PX150XL_endCapSticker_mat' for m in root.findall('Materials/Material'))
material = copy.deepcopy(next(m for m in root.findall('Materials/Material') if m.get('name') == 'PX150XL_lettering_white'))
material_id = str(max(int(m.get('materialId')) for m in root.findall('Materials/Material')) + 1)
material.set('materialId', material_id)
material.set('name', 'PX150XL_endCapSticker_mat')
next(p for p in material.findall('CustomParameter') if p.get('name') == 'colorScale').set('value', '0.8 0.16 0.018')
root.find('Materials').append(material)
stickers = E.parse(BUILD / 'approved_stickers.i3d').getroot()
node_id = max(int(n.get('nodeId', '0')) for n in root.iter()) + 1
component = root.find('Scene/Shape')
for i, shape in enumerate(stickers.findall('Shapes/IndexedTriangleSet')):
    shape_id = str(9100 + i)
    shape.set('shapeId', shape_id)
    root.find('Shapes').append(shape)
    E.SubElement(component, 'Shape', name=f'PX150XL_endCapSticker_{("left", "right")[i]}',
                 shapeId=shape_id, nodeId=str(node_id+i), materialIds=material_id,
                 clipDistance='300', castsShadows='false', receiveShadows='true')
E.indent(model, space='  ')
model.write(QA / 'px150xlWindrower.i3d', encoding='utf-8', xml_declaration=True)

vehicle = E.parse(QA / 'px150xlWindrower.xml')
v = vehicle.getroot()
assert v.find('designColorConfigurations') is None
config = E.Element('designColorConfigurations', title='$l10n_px150_endCapColor',
                   useDefaultColors='true', price='250', defaultColorMaterialTemplateName='calibratedPaint')
E.SubElement(config, 'designColorConfiguration', name='$l10n_px150_endCapOrange',
             color='0.8 0.16 0.018', materialTemplateName='calibratedPaint', isDefault='true', price='250')
E.SubElement(config, 'material', materialSlotName='px150_endCapSticker', materialTemplateUseColorOnly='true')
v.insert(list(v).index(v.find('i3dMappings')), config)
E.indent(vehicle, space='    ')
vehicle.write(QA / 'px150xlWindrower.xml', encoding='utf-8', xml_declaration=True)

desc = (QA / 'modDesc.xml').read_text(encoding='utf-8')
assert '<version>2.2.1.0</version>' in desc
desc = desc.replace('<version>2.2.1.0</version>', '<version>2.3.0.0</version>')
desc = desc.replace('    </l10n>', '''        <text name="px150_endCapColor">
            <en>End cap color</en>
            <de>Endkappenfarbe</de>
        </text>
        <text name="px150_endCapOrange">
            <en>PropaineX orange</en>
            <de>PropaineX Orange</de>
        </text>
    </l10n>''')
english, german = desc.split('<de><![CDATA[', 1)
english = english.replace('Changelog 2.2.1.0:', 'Changelog 2.3.0.0:\n- End cap color shop option with full native color palette; only the sticker changes color.\n\nChangelog 2.2.1.0:', 1)
german = german.replace('Changelog 2.2.1.0:', 'Changelog 2.3.0.0:\n- Endkappenfarbe im Shop mit kompletter Standardfarbpalette; nur der Aufkleber wechselt die Farbe.\n\nChangelog 2.2.1.0:', 1)
(QA / 'modDesc.xml').write_text(english + '<de><![CDATA[' + german, encoding='utf-8')
print('Staged 2.3.0.0: 2 approved sticker shapes, one exclusive material slot, full native palette, default orange.')
