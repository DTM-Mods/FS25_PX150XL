from pathlib import Path
import xml.etree.ElementTree as E,io,struct
from PIL import Image
r=Path.cwd()
def dds_limited(path,fmt,count):
 base=Image.open(path).convert('RGBA');levels=[];buf=io.BytesIO();base.save(buf,format='DDS',pixel_format=fmt);head=bytearray(buf.getvalue()[:128])
 for n in range(max(1,count)):
  buf=io.BytesIO();base.save(buf,format='DDS',pixel_format=fmt);levels.append(buf.getvalue()[128:]);base=base.resize((max(1,base.width//2),max(1,base.height//2)),Image.Resampling.LANCZOS)
 if count<=1:struct.pack_into('<I',head,28,0);struct.pack_into('<I',head,8,struct.unpack_from('<I',head,8)[0]&~0x20000);struct.pack_into('<I',head,108,0x1000)
 else:struct.pack_into('<I',head,28,count);struct.pack_into('<I',head,8,struct.unpack_from('<I',head,8)[0]|0x20000);struct.pack_into('<I',head,108,0x401008)
 path.write_bytes(head+b''.join(levels))
dds_limited(r/'icon_px150xl.dds','DXT1',0);dds_limited(r/'brand_propainex.dds','DXT5',0);dds_limited(r/'store_px150xl.dds','DXT5',3)
i=E.parse(r/'px150xlWindrower.i3d')
for f in i.findall('./Files/File'):
 name=f.get('filename','')
 if name.startswith('textures/'):f.set('filename','$data/vehicles/'+name[len('textures/'):])
E.indent(i,space='  ');i.write(r/'px150xlWindrower.i3d',encoding='utf-8',xml_declaration=True)
v=E.parse(r/'px150xlWindrower.xml');v.find('.//motionPathEffect').set('textureFilename','$data/vehicles/johnDeere/headerHD50F/beltXArray.dds')
store=v.find('storeData')
for e in list(store):
 if e.tag.endswith('MemoryUsage'):store.remove(e)
E.indent(v,space='    ');v.write(r/'px150xlWindrower.xml',encoding='utf-8',xml_declaration=True)
d=E.parse(r/'modDesc.xml');title=d.find('title');E.SubElement(title,'de').text='PX150 XL Schwadschneidwerk Pro Edition'
desc=d.find('description');desc.clear();E.SubElement(desc,'en').text='__DESCRIPTION_EN__';E.SubElement(desc,'de').text='__DESCRIPTION_DE__'
en='''PX150 XL Windrower Pro Edition by PropaineX.
15.2 m grain windrower header for the MacDon M1240.
Cuts wheat, barley, oat, canola and soybean into swaths for pickup with the MacDon PW8. Additional crops depend on map support.
Requires the MacDon Pack. Category: Special Headers.
Price: $144,500. Working speed: 10 km/h. Required power: 45 kW.

Changelog 2.1.0.0:
- Complete M1240 windrower conversion with central grain swath.
- Edited animated header, custom brackets, dark paint and PropaineX/PX150XL branding.
- New shop image and Pro Edition mod icon.'''
de='''PX150 XL Schwadschneidwerk Pro Edition von PropaineX.
15,2 m Getreideschneidwerk fuer den MacDon M1240.
Legt Weizen, Gerste, Hafer, Raps und Sojabohnen im Schwad ab. Aufnahme mit dem MacDon PW8. Weitere Fruechte erfordern Kartenunterstuetzung.
Benoetigt das MacDon Pack. Kategorie: Sonderschneidwerke.
Preis: 144.500 EUR. Arbeitsgeschwindigkeit: 10 km/h. Leistungsbedarf: 45 kW.

Changelog 2.1.0.0:
- Vollstaendiger M1240-Umbau mit zentraler Schwadablage.
- Bearbeitetes animiertes Modell, eigene Halterungen, dunkle Lackierung und PropaineX/PX150XL-Beschriftung.
- Neues Shopbild und Pro-Edition-Modsymbol.'''
E.indent(d,space='    ');text=E.tostring(d.getroot(),encoding='unicode');text=text.replace('__DESCRIPTION_EN__','<![CDATA['+en+']]>').replace('__DESCRIPTION_DE__','<![CDATA['+de+']]>');(r/'modDesc.xml').write_text('<?xml version="1.0" encoding="utf-8"?>\n'+text,encoding='utf-8')
print('Fixed TestRunner metadata/mipmaps and replaced unchanged duplicate textures with native $data references.')
