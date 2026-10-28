from pathlib import Path
import xml.etree.ElementTree as E,copy,math
root=Path.cwd()
v=E.parse(root/'headerHD50F.xml').getroot();v.set('type','mower')
v.find('storeData/name').text='PX150XL Windrower'
v.find('storeData/brand').text='PROPAINEX'
for e in list(v.findall('storeData/specs/combination')):v.find('storeData/specs').remove(e)
v.find('storeData/functions/function').text='$l10n_px150_functionWindrower'
v.find('base/typeDesc').text='$l10n_typeDesc_mower'
v.find('base/filename').text='px150xlWindrower.i3d'
# Dedicated carrier uses its own hydraulics, not the combine PTO/coupler.
for tag in ['powerTakeOffs','connectionHoses','dynamicMount']:
 for e in v.findall(tag):v.remove(e)
a=v.find('attachable');a.clear();ajs=E.SubElement(a,'inputAttacherJoints')
j=E.SubElement(ajs,'inputAttacherJoint',node='attacherJointM1240',jointType='cutter',lowerRotLimitScale='0 0 0',upperRotationOffset='5',topReferenceNode='topReferenceM1240',bottomArmLeftNode='bottomArmLeftM1240',bottomArmRightNode='bottomArmRightM1240')
E.SubElement(j,'subType',name='m1240',showWarning='false');E.SubElement(j,'distanceToGround',lower='0.4',upper='2.2')
# No combine support-wheel physics to hold the cutting line above ground.
v.remove(v.find('wheels'))
for a0 in v.findall('animations/animation'):
 if a0.get('name')=='supportWheels':v.find('animations').remove(a0)
for e in list(v.findall('cylindered/movingTools/movingTool')):
 if e.get('node')=='supportWheels':v.find('cylindered/movingTools').remove(e)
for e in list(v.findall('cylindered/movingParts/movingPart')):
 if e.get('node')=='supportWheelsHydraulic':v.find('cylindered/movingParts').remove(e)
g=v.find('groundReferenceNodes');g.clear();E.SubElement(g,'groundReferenceNode',node='cutGroundReference',threshold='0.25')
w=v.find('workAreas');w.clear();area=E.SubElement(w,'workArea',type='mower',functionName='processMowerArea',disableBackwards='true')
E.SubElement(area,'area',startNode='workAreaStart',widthNode='workAreaWidth',heightNode='workAreaHeight');E.SubElement(area,'groundReferenceNode',index='1');E.SubElement(area,'testAreas',autoGenerate='true',zOffset='0.5',xOffset='0.5',length='0.6',numAreas='16',areaWidthScale='0.25');E.SubElement(area,'mower',dropWindrow='true',dropAreaIndex='2');E.SubElement(area,'onlyActiveWhenLowered',value='true')
aux=E.SubElement(w,'workArea',type='auxiliary');E.SubElement(aux,'area',startNode='swathDropStart',widthNode='swathDropWidth',heightNode='swathDropHeight')
c=v.find('cutter');m=E.Element('mower',fruitTypeConverter='COMBINE_MOWER')
for tag in ['animationNodes','fruitExtraObjects','sounds']:
 e=c.find(tag)
 if e is not None:m.append(copy.deepcopy(e))
for e in list(m.findall('animationNodes/animationNode')):
 if e.get('node')=='drumMain':m.find('animationNodes').remove(e)
e=copy.deepcopy(c.find('effect'));e.tag='cutterEffects';e.find('effectNode/motionPathEffect').set('textureFilename','beltXArray.dds');m.append(e)
v.insert(list(v).index(c),m);v.remove(c)
t=v.find('turnOnVehicle');t.set('turnedOnByAttacherVehicle','false');t.set('toggleButton','IMPLEMENT_EXTRA');t.set('turnOnText','$l10n_px150_turnOn');t.set('turnOffText','$l10n_px150_turnOff');t.set('aiRequiresTurnOn','true')
# Power requirement retained for this heavier 15.2 m machine; RPM agrees with carrier reference.
v.find('powerConsumer').set('ptoRpm','470')
# Append nodes: existing animation/mapping paths remain stable.
i=E.parse(root/'headerHD50F.i3d').getroot();component=i.find('Scene/Shape');baseidx=len(component);ids=[int(e.get('nodeId')) for e in i.iter() if e.get('nodeId')];nid=max(ids)+1
mount=E.SubElement(component,'TransformGroup',name='px150M1240Mechanics',nodeId=str(nid));nid+=1
mapping=v.find('i3dMappings')
def node(name,parent=mount,**attrs):
 global nid
 e=E.SubElement(parent,'TransformGroup',name=name,nodeId=str(nid),**attrs);nid+=1;return e
jointframe=node('m1240Mount',translation='0 -0.274 -1.360056',rotation='0 -90 0');node('attacherJointM1240',jointframe,rotation='0 0 18.72')
node('bottomArmLeftM1240',translation='1.274 -0.274 -1.360056');node('bottomArmRightM1240',translation='-1.274 -0.274 -1.360056')
angle=math.radians(18.72);ty=-.274+.370*math.sin(angle)+1.122*math.cos(angle);tz=-1.360056+.370*math.cos(angle)-1.122*math.sin(angle)
node('topReferenceM1240',translation=f'0 {ty:.6f} {tz:.6f}')
node('cutGroundReference',translation='0 0 0.395944')
node('swathDropStart',translation='0.75 0 0.155944');node('swathDropWidth',translation='-0.75 0 0.155944');node('swathDropHeight',translation='0.75 0 -1.004056')
for idx,e in enumerate(mount):
 if e.get('name')=='m1240Mount':E.SubElement(mapping,'i3dMapping',id='attacherJointM1240',node=f'0>{baseidx}|{idx}|0')
 else:E.SubElement(mapping,'i3dMapping',id=e.get('name'),node=f'0>{baseidx}|{idx}')
# Support gear has no role on the carrier; hide its skinned bones, retaining hierarchy indices.
for e in i.iter():
 if e.get('name') in ['supportWheels','supportWheelsHydraulic']:e.set('visibility','false')
E.indent(v,space='    ');E.ElementTree(v).write(root/'px150xlWindrower.xml',encoding='utf-8',xml_declaration=True)
E.indent(i,space='  ');E.ElementTree(i).write(root/'px150xlWindrower.i3d',encoding='utf-8',xml_declaration=True)
d=E.Element('modDesc',descVersion='115');E.SubElement(d,'author').text='PropaineX';E.SubElement(d,'version').text='2.0.0.0';E.SubElement(E.SubElement(d,'title'),'en').text='PX150XL Windrower';E.SubElement(E.SubElement(d,'description'),'en').text='15.2 m grain windrower header for the MacDon M1240. Cuts supported grain crops into swaths for pickup with the MacDon PW8. Requires MacDon Pack.';E.SubElement(d,'iconFilename').text='store_headerHD50F.dds';E.SubElement(d,'multiplayer',supported='true');E.SubElement(E.SubElement(d,'dependencies'),'dependency').text='pdlc_macDonPack'
l=E.SubElement(d,'l10n')
for name,text in [('px150_functionWindrower','Cuts grain and lays a swath (MacDon M1240)'),('px150_turnOn','Turn on header'),('px150_turnOff','Turn off header')]:E.SubElement(E.SubElement(l,'text',name=name),'en').text=text
E.SubElement(E.SubElement(d,'brands'),'brand',name='PROPAINEX',title='PropaineX',image='brand_propainex.dds');E.SubElement(E.SubElement(d,'storeItems'),'storeItem',xmlFilename='px150xlWindrower.xml');E.indent(d,space='    ');E.ElementTree(d).write(root/'modDesc.xml',encoding='utf-8',xml_declaration=True)
from PIL import Image,ImageDraw,ImageFont
im=Image.new('RGBA',(512,256),(0,0,0,0));dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',68);dr.text((256,128),'PropaineX',font=font,anchor='mm',fill=(235,235,235,255));im.save(root/'brand_propainex.dds',pixel_format='DXT5')
print('Created mechanical runtime source 2.0.0.0. Joint z=-1.360056; top ref',ty,tz,'; added nodes',nid-max(ids)-1)
