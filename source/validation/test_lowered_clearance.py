"""Exercise the actual Lua fit and native-joint adapter with deterministic geometry."""
from pathlib import Path
from lupa.lua51 import LuaRuntime

root = Path(__file__).resolve().parents[2]
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute('''
table.unpack = unpack
Event = {new=function(mt) return setmetatable({},mt) end}
function Class(c,b) c.__index=c; return c end
function InitEventClass() end
Logging = {warning=function() end,info=function() end}
''')
lua.execute((root/'scripts/PX150LoweredClearance.lua').read_text())
lua.execute('''
local C=PX150LoweredClearance
-- Coupled nonlinear lift/pitch fit: the front must remain fixed, not just sockets.
for _,baselinePitch in ipairs({-.08,0,.08}) do
    local oldA,oldR=.85,math.rad(10)
    local function height(a,r,x,y)
        local theta=baselinePitch+math.rad(5)*(1-a)+r*a
        return 1.5-1.4*a+x*math.sin(theta)+y*math.cos(theta)
    end
    local reference=height(oldA,oldR,1.751043,-.304072)
    local function errors(a,r)
        return height(a,r,1.751043,-.304072)-reference,
            height(a,r,-.19303,-.04013)-.05
    end
    local a,r=C.solvePose(oldA,oldR,errors)
    assert(a and a>=0 and a<=1,'reachable fit failed')
    local front,rear=errors(a,r)
    assert(math.abs(front)<.001 and math.abs(rear)<.001)
end
assert(C.solvePose(.5,0,function() return 1,1 end)==nil,'singular fit must fail safely')
assert(C.solvePose(.5,0,function(a,r) return a-3,r end)==nil,'unreachable lift must not escape native range')

-- Full adapter: actual component->input-frame conversion and restoration of
-- carrier graphics transforms: sampling operates on temporary copies only.
local nodes={[10]={0,0,0},[11]={.37,0,0},[13]={0,0,.123}}
local parents={[11]=10,[13]=11}
local counter=100
function createTransformGroup() counter=counter+1;nodes[counter]={0,0,0};return counter end
function getRootNode() return 0 end
function link(parent,node) parents[node]=parent end
function getParent(node) return parents[node] or 0 end
function getTranslation() return 0,0,0 end
function setTranslation() end
function getScale() return 1,1,1 end
function setScale() end
function getWorldTranslation() return 0,0,0 end
function setWorldTranslation() end
function getWorldRotation() return 0,0,0 end
function setWorldRotation() end
function delete(root)
    local children={}
    for node,parent in pairs(parents) do if parent==root then table.insert(children,node) end end
    for _,child in ipairs(children) do delete(child) end
    nodes[root],parents[root]=nil,nil
end
local pitchBase=0
function getRotation(n) return table.unpack(nodes[n]) end
function setRotation(n,x,y,z) nodes[n]={x,y,z} end
function rotateAboutLocalAxis(n,a,x,y,z) nodes[n][3]=nodes[n][3]+a end
function localToLocal(component,input,x,y,z)
    local dy,dz=y+.274,z+1.360056
    local tilt=math.rad(18.72)
    return dy*math.sin(tilt)+dz*math.cos(tilt),dy*math.cos(tilt)-dz*math.sin(tilt),-x
end
function localToWorld(n,x,y,z)
    local a=nodes[getParent(n)][1]
    local t=pitchBase+nodes[n][3]
    return x*math.cos(t)-y*math.sin(t),1.5-1.4*a+x*math.sin(t)+y*math.cos(t),z
end
g_currentMission={terrainRootNode=99}
function getTerrainHeightAtWorldPos() return 0 end
local input={node=2,heightNodes={},upperRotationOffset=math.rad(5),lowerRotationOffset=math.rad(10),lowerDistanceToGround=.30}
local desc={allowsLowering=true,lowerDistanceToGround=.1,upperDistanceToGround=1.5,
    rootNode=10,rotationNode=11,jointTransform=13,jointOrigRot={0,0,0},
    upperRotation={0,0,0},lowerRotation={1,0,0},upperRotationOffset=0,lowerRotationOffset=0}
local carrier={spec_attacherJoints={attacherJoints={desc}},
    updateAttacherJointRotationNodes=function(self,d,a) nodes[11][1]=a end}
local header={components={{node=1}},px150Clearance={carrier=carrier,jointIndex=1,baseDistance=.30,baseAngle=math.rad(10)},
    getActiveInputAttacherJoint=function() return input end}
local distance,angle,reference=C.calibrate(header)
assert(distance and angle and reference,'adapter fit failed')
assert(math.abs(nodes[11][1]-.37)<1e-12 and math.abs(nodes[13][3]-.123)<1e-12,'temporary transforms leaked')
local alpha=(distance-1.5)/(.1-1.5)
carrier:updateAttacherJointRotationNodes(desc,alpha)
setRotation(13,0,0,math.rad(5)*(1-alpha)+angle*alpha)
local x,y,z=localToLocal(1,2,0,0,.395944)
local _,worldY=localToWorld(13,x,y,z)
assert(math.abs(worldY-reference)<.001,'front height drifted')
local socketY=math.huge
for _,z in ipairs({-1.53,-1.23}) do
    local sx,sy,sz=localToLocal(1,2,1.3965,-.374,z)
    local _,y=localToWorld(13,sx,sy,sz)
    socketY=math.min(socketY,y)
end
assert(math.abs(socketY-.05)<.001,'rear target not met')
for node in pairs(nodes) do assert(node<100,'temporary fit nodes leaked') end

-- Join/reattach uses the original source reference, not a previous calibrated
-- pose received over the network; detaching restores the original settings.
local live={spec_attachable={inputAttacherJoints={input}},
    getActiveInputAttacherJoint=function() return input end,
    getAttacherVehicle=function() return nil end}
C.onLoad(live)
local baselineDistance,baselineAngle=input.lowerDistanceToGround,input.lowerRotationOffset
live.px150Clearance={}
C.apply(live,.6,.25)
C.onPostAttach(live,carrier,1,1)
assert(live.px150Clearance.baseDistance==baselineDistance)
assert(live.px150Clearance.baseAngle==baselineAngle)
assert(live.px150Clearance.distance==.6 and live.px150Clearance.angle==.25)
local buffer={}
function streamWriteBool(_,x) table.insert(buffer,x) end
function streamWriteFloat32(_,x) table.insert(buffer,x) end
function streamReadBool() return table.remove(buffer,1) end
function streamReadFloat32() return table.remove(buffer,1) end
C.onWriteStream(live,1,{})
local joined={getActiveInputAttacherJoint=function() return nil end}
C.onReadStream(joined,1,{})
assert(joined.px150Clearance.distance==.6 and joined.px150Clearance.angle==.25)
C.onPreDetach(live)
assert(input.lowerDistanceToGround==baselineDistance and input.lowerRotationOffset==baselineAngle)
assert(live.px150Clearance==nil)
print('PASS: front reference, 5 cm rear, native bounds/fallback, temporary geometry, join/reattach reference, streams and detach reset.')
''')
