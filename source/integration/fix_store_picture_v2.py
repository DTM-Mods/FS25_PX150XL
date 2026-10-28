from pathlib import Path
from PIL import Image,ImageDraw
import shutil,io,struct
r=Path.cwd();p=r/'source/integration';backup=p/'store_px150xl_v2_1_0.dds'
if not backup.exists():shutil.copy2(r/'store_px150xl.dds',backup)
im=Image.open(p/'shop_px150xl_hero_v2.png').convert('RGBA');im=im.crop(im.getbbox());im.thumbnail((496,246),Image.Resampling.LANCZOS);canvas=Image.new('RGBA',(512,512),(0,0,0,0));canvas.alpha_composite(im,((512-im.width)//2,508-im.height));canvas.save(p/'store_px150xl_v2_preview.png')
old=Image.open(backup).convert('RGBA');comparison=Image.new('RGB',(1024,560),(35,38,39));comparison.paste(old,(0,48),old);comparison.paste(canvas,(512,48),canvas);d=ImageDraw.Draw(comparison);d.text((20,12),'BEFORE',font_size=24,fill=(235,235,235));d.text((532,12),'AFTER - STORE PICTURE',font_size=24,fill=(235,235,235));comparison.save(p/'store_picture_comparison_v2.png')
# Store GUI texture: DXT5, exactly three mip levels.
base=canvas;parts=[];head=None
for level in range(3):
 b=io.BytesIO();base.save(b,format='DDS',pixel_format='DXT5');data=b.getvalue()
 if head is None:head=bytearray(data[:128])
 parts.append(data[128:]);base=base.resize((base.width//2,base.height//2),Image.Resampling.LANCZOS)
struct.pack_into('<I',head,28,3);struct.pack_into('<I',head,8,struct.unpack_from('<I',head,8)[0]|0x20000);struct.pack_into('<I',head,108,0x401008);(r/'store_px150xl.dds').write_bytes(head+b''.join(parts))
s=(r/'modDesc.xml').read_text(encoding='utf-8').replace('<version>2.1.0.0</version>','<version>2.1.1.0</version>');needle='Changelog 2.1.0.0:';s=s.replace(needle,'Changelog 2.1.1.0:\n- Improved store picture angle, lighting and placement.\n\n'+needle,1);pos=s.find('<de><![CDATA[')
if pos>=0:s=s[:pos]+s[pos:].replace(needle,'Changelog 2.1.1.0:\n- Verbessertes Shopbild mit neuer Ansicht und Platzierung.\n\n'+needle,1)
(r/'modDesc.xml').write_text(s,encoding='utf-8')
print('Store picture bbox',canvas.getbbox(),'version2.1.1.0; runtime geometry unchanged')
