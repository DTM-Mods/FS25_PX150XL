"""Offline audit. Engine/density/network boundaries are stubs, never a live game probe."""
from pathlib import Path
import re, json, hashlib, zipfile, xml.etree.ElementTree as ET
from lupa.lua51 import LuaRuntime

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROFILE = ROOT.parents[1]
results = {}

def native(file, name):
    text = (HERE/'gameSource'/file).read_text(encoding='utf-8-sig')
    start = text.index('function '+name+'(')
    end = re.search(r'^function ', text[start+1:], re.M)
    return text[start:start+1+end.start()] if end else text[start:]

lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute('''
function Class(c,b) c.__index=c;return c end
Event={new=function(mt)return setmetatable({},mt)end}
function InitEventClass()end
SpecializationUtil={hasSpecialization=function()return true end,registerEventListener=function()end}
''')
for path in (ROOT/'scripts').glob('*.lua'):
    lua.execute(path.read_text())
results['lua51_syntax'] = 'All three runtime scripts compile and load with engine globals stubbed'

# Execute the game function, including its native liter calculation and buffer cap.
lua.execute('Mower={CLIENT_DM_UPDATE_RADIUS=100};FillType={GRASS_WINDROW=999};FSDensityMapUtil={};g_time=1')
lua.execute(native('Mower.lua','Mower:processMowerArea'))
lua.execute('''
function getWorldTranslation()return 0,0,0 end
function FSDensityMapUtil.getStoneArea()return 0 end
function FSDensityMapUtil.updateMowerArea()return 1,1,0,0,0,0,0,0,0,1 end
g_currentMission={getHarvestScaleMultiplier=function()return 1.25 end}
local baseLiters=100
g_fruitTypeManager={getFruitTypeAreaLiters=function()return baseLiters end}
local shared={[1]={conversionFactor=.75,fillTypeIndex=101}}
local function header(bonus,server)
 local h={isServer=server,currentUpdateDistance=0,drop={litersToDrop=0},
 spec_mower={fruitTypeConverters=shared,workAreaParameters={lastChangedArea=0,lastStatsArea=0,lastTotalArea=0,lastUsedAreas=0,lastUsedAreasSum=0}},
 getLastSpeed=function()return 10 end,getIsAIActive=function()return false end,
 getDropArea=function(self)return self.drop end,setTestAreaRequirements=function()end}
 if bonus then PX150YieldBonus.onPostLoad(h)end
 return h
end
for _,server in ipairs({true,false})do
 local h,b=header(true,server),header(false,server)
 local a={start=1,width=2,height=3,index=1}
 local changed,total=Mower.processMowerArea(h,a,16)
 Mower.processMowerArea(b,a,16)
 assert(changed==1 and total==1)
 assert(math.abs(h.drop.litersToDrop/b.drop.litersToDrop-1.10)<1e-12)
 assert(shared[1].conversionFactor==.75)
 local old=h.drop.litersToDrop
 h.isServer=false;h.currentUpdateDistance=101
 assert(Mower.processMowerArea(h,a,16)==0 and h.drop.litersToDrop==old)
end
local h=header(true,true)
baseLiters=1000
Mower.processMowerArea(h,{start=1,width=2,height=3,index=1},16)
assert(h.drop.litersToDrop==1000) -- 1031.25 calculated, native cap discards excess.
''')
results['native_mower'] = 'PASS: server/near-client native 10% calculation, shared isolation, distant-client guard; native 1000 L cap reproduced'

lua.execute('''
RigidBodyType={DYNAMIC=1,KINEMATIC=2,STATIC=3}
local bodies={1,3};local calls=0
function getRigidBodyType(n)return bodies[n]end
function setRigidBodyType(n,v)bodies[n]=v;calls=calls+1 end
local h={components={{node=1},{node=2}},getIsInShowroom=function()return false end}
PX150ShopDisplay.onPostLoad(h)
assert(calls==0 and bodies[1]==1)
h.getIsInShowroom=function()return true end
PX150ShopDisplay.onPostLoad(h)
assert(calls==1 and bodies[1]==2 and bodies[2]==3)
local input={lowerDistanceToGround=.3,lowerRotationOffset=.17}
local h={getActiveInputAttacherJoint=function()return input end,getAttacherVehicle=function()return nil end}
local e=PX150ClearanceEvent.emptyNew()
e.vehicle,e.distance,e.angle=h,.6,.25
e:run({getIsServer=function()return false end})
assert(h.px150Clearance==nil)
e:run({getIsServer=function()return true end})
assert(input.lowerDistanceToGround==.3 and h.px150Clearance==nil)
''')
results['shop_and_network'] = 'PASS showroom guard/static preservation, client-origin rejection and detached server-event rejection (updated after source fix)'

lua.execute('AttacherJoints={};MathUtil={lerp=function(a,b,t)return a+(b-a)*t end};math.clamp=function(x,a,b)return math.max(a,math.min(b,x))end')
lua.execute(native('AttacherJoints.lua','AttacherJoints:calculateAttacherJointMoveUpperLowerAlpha'))
lua.execute(native('AttacherJoints.lua','AttacherJoints:updateAttacherJointRotation'))
lua.execute('''
local rotation,offset
function setRotation(n,x,y,z)rotation={x,y,z}end
function rotateAboutLocalAxis(n,a,x,y,z)offset=a end
local input={heightNodes={},upperDistanceToGround=2.2,lowerDistanceToGround=.3,
 upperRotationOffset=math.rad(5),lowerRotationOffset=math.rad(10),allowsLowering=true}
local desc={allowsLowering=true,upperDistanceToGround=1.5,lowerDistanceToGround=.1,
 moveAlpha=.9,upperRotationOffset=0,lowerRotationOffset=0,jointOrigRot={0,0,0},jointTransform=7}
local carrier={spec_attacherJoints={attacherJoints={desc}},
 getImplementByObject=function()return {jointDescIndex=1}end,
 updateAttacherJointRotation=AttacherJoints.updateAttacherJointRotation}
local h={px150Clearance={carrier=carrier,jointIndex=1},spec_attachable={attacherJoint=input},
 getActiveInputAttacherJoint=function()return input end,getAttacherVehicle=function()return carrier end}
PX150LoweredClearance.apply(h,.2384,math.rad(16.087))
local upper,lower=AttacherJoints.calculateAttacherJointMoveUpperLowerAlpha(carrier,desc,h,false)
assert(upper==0 and math.abs(lower-(.2384-1.5)/(.1-1.5))<1e-12)
assert(desc.jointFrameInvalid==true)
assert(math.abs(offset-(input.upperRotationOffset*.1+input.lowerRotationOffset*.9))<1e-12)
''')
results['native_attachment'] = 'PASS: actual native lower-alpha mapping and rotation offset consume fitted values; frame marked invalid for native refresh (physics boundary stubbed)'

v = ET.parse(ROOT/'px150xlWindrower.xml').getroot()
i = ET.parse(ROOT/'px150xlWindrower.i3d').getroot()
scene = list(i.find('Scene'))
maps = {}
for m in v.findall('i3dMappings/i3dMapping'):
    indices = [int(x) for x in re.split(r'[>|]',m.get('node')) if x]
    node = scene[indices[0]]
    for index in indices[1:]: node = list(node)[index]
    assert m.get('id') not in maps
    maps[m.get('id')] = node
results['mappings'] = f'PASS {len(maps)} unique mappings resolve into current I3D'

issues = []
for file,tree in [('modDesc.xml',ET.parse(ROOT/'modDesc.xml').getroot()),('px150xlWindrower.xml',v),('px150xlWindrower.i3d',i)]:
    for el in tree.iter():
        for key,val in el.attrib.items():
            if key.lower() in {'filename','texturefilename','externalshapesfile','image'} or (el.tag=='File' and key=='filename'):
                if val.startswith('$data/'):
                    p=Path('G:/SteamLibrary/steamapps/common/Farming Simulator 25/data')/val[6:]
                elif val.startswith('$'):continue
                else:p=ROOT/val
                if not p.is_file() and p.suffix=='.png':p=p.with_suffix('.dds')
                if not p.is_file():issues.append([file,val])
assert not issues,issues
results['references'] = 'PASS explicit filename/texture/external-shapes/image attributes including loose $data assets'

with zipfile.ZipFile(PROFILE/'mods/FS25_PX150XL.zip') as z:
    assert z.testzip() is None
    assert 'modDesc.xml' in z.namelist() and all('\\' not in n for n in z.namelist())
    differences=[n for n in z.namelist() if (ROOT/n).read_bytes()!=z.read(n)]
    results['installed_identity']={'files':len(z.namelist()),'sha256':hashlib.sha256((PROFILE/'mods/FS25_PX150XL.zip').read_bytes()).hexdigest(),'all_entries_equal_source':not differences,'source_differences':differences}

# Continuous keyframe boundary check; compare with the original loose game XML.
base=ET.parse('G:/SteamLibrary/steamapps/common/Farming Simulator 25/data/vehicles/johnDeere/headerHD50F/headerHD50F.xml').getroot()
discontinuities=[]
for part in v.findall('animations/animation/part'):
    for nxt in v.findall('animations/animation/part'):
        if part is nxt or part.get('node')!=nxt.get('node') or part.get('endTime')!=nxt.get('startTime'):continue
        for end,start in [('endTrans','startTrans'),('endRot','startRot')]:
            if part.get(end) and nxt.get(start) and part.get(end).split()!=nxt.get(start).split():
                discontinuities.append({'node':part.get('node'),'time':part.get('endTime'),'end':part.get(end),'next_start':nxt.get(start),'same_as_base_game':any(p.attrib==nxt.attrib for p in base.findall('animations/animation/part'))})
results['animation_discontinuities']=discontinuities
(HERE/'native_results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
