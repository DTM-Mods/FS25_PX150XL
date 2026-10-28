from PIL import Image,ImageDraw
from pathlib import Path
p=Path('previews/hd50f_adapter_v1');a=Image.open(p/'textured_rear_no_fingers_v1.png').convert('RGB');b=Image.open(p/'hd50f_with_brackets_v1.png').convert('RGB')
out=Image.new('RGB',(a.width+b.width,a.height+70),(235,235,235));out.paste(a,(0,70));out.paste(b,(a.width,70));d=ImageDraw.Draw(out);d.text((30,18),'BEFORE',fill=(20,20,20),font_size=32);d.text((a.width+30,18),'AFTER - saved bracket kit fitted',fill=(20,20,20),font_size=32);d.line((a.width,0,a.width,out.height),fill=(240,240,240),width=4);out.save(p/'hd50f_brackets_comparison_v1.png')
