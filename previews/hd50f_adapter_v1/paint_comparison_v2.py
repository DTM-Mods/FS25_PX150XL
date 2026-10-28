from PIL import Image,ImageDraw
from pathlib import Path
p=Path('previews/hd50f_adapter_v1');a=Image.open(p/'hd50f_bracket_pins_visible_v2.png').convert('RGB');b=Image.open(p/'px150xl_dark_branding_v2.png').convert('RGB');o=Image.new('RGB',(a.width+b.width,a.height+70),(235,235,235));o.paste(a,(0,70));o.paste(b,(a.width,70));d=ImageDraw.Draw(o);d.text((30,18),'BEFORE',fill=(20,20,20),font_size=32);d.text((a.width+30,18),'AFTER - PropaineX PX150XL',fill=(20,20,20),font_size=32);o.save(p/'px150xl_paint_branding_comparison_v2.png')
