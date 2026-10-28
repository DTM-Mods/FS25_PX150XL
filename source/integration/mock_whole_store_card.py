from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import xml.etree.ElementTree as E
p=Path('source/integration');v=E.parse('px150xlWindrower.xml');name=v.findtext('storeData/name');price=int(v.findtext('storeData/price'))
# Reproduce the proportions and image offset observed in the user's shop-card screenshot.
# This is a layout mock-up, not an in-game capture.
W,H=438,725
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',n)
def card(texture):
 out=Image.new('RGB',(W,H),(33,34,32));d=ImageDraw.Draw(out)
 d.rounded_rectangle((40,74,406,663),radius=15,fill=(38,40,36),outline=(57,62,48),width=3)
 im=Image.open(texture).convert('RGBA').resize((362,362),Image.Resampling.LANCZOS)
 # Same 362 px scaling and vertical origin as the card supplied by the user.
 layer=Image.new('RGBA',(W,H),(0,0,0,0));layer.alpha_composite(im,(43,-46));out=Image.alpha_composite(out.convert('RGBA'),layer).convert('RGB');d=ImageDraw.Draw(out)
 d.text((223,387),'PropaineX',font=font(28),anchor='mm',fill=(238,238,238))
 d.line((42,456,404,456),fill=(56,58,51),width=1)
 d.text((223,502),name,font=font(22),anchor='mm',fill=(230,233,220))
 title='PX150 XL WINDROWER PRO EDITIO...';d.text((57,547),title,font=font(17),anchor='lm',fill=(120,168,3))
 regular=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',36);d.text((223,584),f'$ {price:,}',font=regular,anchor='mm',fill=(238,241,228))
 return out
old=card(p/'store_px150xl_v2_1_0.dds');new=card('store_px150xl.dds')
old.save(p/'whole_store_card_before_v1.png');new.save(p/'whole_store_card_fixed_v1.png')
comparison=Image.new('RGB',(W*2,H+48),(27,28,27));comparison.paste(old,(0,48));comparison.paste(new,(W,48));d=ImageDraw.Draw(comparison);d.text((W//2,24),'BEFORE',font=font(22),anchor='mm',fill='white');d.text((W+W//2,24),'REVISED - LAYOUT MOCK-UP',font=font(19),anchor='mm',fill='white');comparison.save(p/'whole_store_card_comparison_v1.png')
print('Created full shop card comparison based on supplied screenshot proportions.')
