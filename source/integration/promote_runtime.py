from pathlib import Path
import xml.etree.ElementTree as E,shutil
from PIL import Image
r=Path.cwd();p=r/'source/integration';backup=r/'source/mechanical/v2_0_runtime';backup.mkdir(exist_ok=True)
for name in ['modDesc.xml','px150xlWindrower.xml','px150xlWindrower.i3d']:
 if not (backup/name).exists():shutil.copy2(r/name,backup/name)
i=E.parse(p/'final_complete_binary.i3d').getroot();i.set('name','PX150XL Windrower');i.find('Shapes').set('externalShapesFile','px150xlWindrower.i3d.shapes');E.indent(i,space='  ');E.ElementTree(i).write(r/'px150xlWindrower.i3d',encoding='utf-8',xml_declaration=True);shutil.copy2(p/'final_complete_binary.i3d.shapes',r/'px150xlWindrower.i3d.shapes')
v=E.parse(r/'px150xlWindrower.xml').getroot();v.find('powerConsumer').set('neededMaxPtoPower','45');v.find('storeData/image').text='store_px150xl.png';E.indent(v,space='    ');E.ElementTree(v).write(r/'px150xlWindrower.xml',encoding='utf-8',xml_declaration=True)
d=E.parse(r/'modDesc.xml').getroot();d.find('version').text='2.1.0.0';d.find('iconFilename').text='store_px150xl.dds';E.indent(d,space='    ');E.ElementTree(d).write(r/'modDesc.xml',encoding='utf-8',xml_declaration=True)
im=Image.open(p/'shop_px150xl_hero.png').convert('RGBA');bbox=im.getbbox();im=im.crop(bbox);im.thumbnail((496,420),Image.Resampling.LANCZOS);out=Image.new('RGBA',(512,512),(0,0,0,0));out.alpha_composite(im,((512-im.width)//2,(512-im.height)//2));out.save(r/'store_px150xl.dds',pixel_format='DXT5')
print('Promoted complete binary model and shop render. Version 2.1.0.0; mower power45kW.')
