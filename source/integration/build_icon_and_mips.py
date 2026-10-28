from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import importlib.util,io,struct,xml.etree.ElementTree as E
r=Path.cwd();p=r/'source/integration';spec=importlib.util.spec_from_file_location('pro_banner',r.parent/'Library/_ProEditionBanner/add_banner.py');banner=importlib.util.module_from_spec(spec);spec.loader.exec_module(banner)
im=Image.open(p/'shop_px150xl_hero.png').convert('RGBA');im=im.crop(im.getbbox());im.thumbnail((496,280),Image.Resampling.LANCZOS)
icon=Image.new('RGBA',(512,512),(25,28,31,255));d=ImageDraw.Draw(icon)
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',49);d.text((256,132),'PX150 XL',font=font,anchor='mm',fill=(242,242,239,255))
icon.alpha_composite(im,((512-im.width)//2,210+(240-im.height)//2));b=banner.make_banner();icon.alpha_composite(b,((512-b.width)//2,20));icon.save(p/'icon_px150xl_proedition_preview.png')
# Generate complete block-compressed DDS mip chains.
def dds(image,path,fmt):
 levels=[];base=image.convert('RGBA');size=base.size
 while True:
  buf=io.BytesIO();base.save(buf,format='DDS',pixel_format=fmt);b=buf.getvalue();levels.append(b[128:])
  if base.size==(1,1):break
  base=base.resize((max(1,base.width//2),max(1,base.height//2)),Image.Resampling.LANCZOS)
 buf=io.BytesIO();image.convert('RGBA').save(buf,format='DDS',pixel_format=fmt);head=bytearray(buf.getvalue()[:128]);struct.pack_into('<I',head,8,struct.unpack_from('<I',head,8)[0]|0x20000);struct.pack_into('<I',head,28,len(levels));struct.pack_into('<I',head,108,0x401008);path.write_bytes(head+b''.join(levels))
 print(path.name,fmt,len(levels),'mip levels')
dds(icon,r/'icon_px150xl.dds','DXT1')
dds(Image.open(r/'store_px150xl.dds'),r/'store_px150xl.dds','DXT5');dds(Image.open(r/'brand_propainex.dds'),r/'brand_propainex.dds','DXT5')
doc=E.parse(r/'modDesc.xml');doc.find('iconFilename').text='icon_px150xl.dds';doc.find('title/en').text='PX150 XL Windrower Pro Edition';E.indent(doc,space='    ');doc.write(r/'modDesc.xml',encoding='utf-8',xml_declaration=True)
path=r/'source/mechanical/package_local.py';s=path.read_text().replace('mechanical runtime only; approved Blender appearance not integrated','complete animated edited model, approved brackets/paint/branding and M1240 grain-swath mechanics');path.write_text(s)
