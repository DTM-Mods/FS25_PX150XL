"""Actual clearance Lua; offline attachment/stream boundaries, no running game access."""
from pathlib import Path
from lupa.lua51 import LuaRuntime

root = Path(__file__).resolve().parents[2]
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute('''
function Class(c,b)c.__index=c;return c end
Event={new=function(mt)return setmetatable({},mt)end}
function InitEventClass()end
''')
lua.execute((root/'scripts/PX150LoweredClearance.lua').read_text())
lua.execute('''
local C=PX150LoweredClearance
local server={getIsServer=function()return true end}
local client={getIsServer=function()return false end}
local buffer={}
local function write(_,v)table.insert(buffer,v)end
local function read()assert(#buffer>0);return table.remove(buffer,1)end
streamWriteBool,streamWriteFloat32,streamWriteInt32=write,write,write
streamReadBool,streamReadFloat32,streamReadInt32=read,read,read
NetworkUtil={writeNodeObject=write,readNodeObject=read}
local function carrier()
 return {spec_attacherJoints={attacherJoints={{},{}}},
 getImplementByObject=function(self,h)return h.implement end,
 updateAttacherJointRotation=function(self)self.updates=(self.updates or 0)+1 end}
end
local a,b=carrier(),carrier()
local function header()
 local input={lowerDistanceToGround=.3,lowerRotationOffset=.17}
 local h={spec_attachable={inputAttacherJoints={input}},input=input,
 getActiveInputAttacherJoint=function(self)return self.input end,
 getAttacherVehicle=function(self)return self.carrier end}
 C.onLoad(h);return h
end
local function attach(h,c,j)
 h.carrier=c;h.implement={jointDescIndex=j}
 C.onPreAttach(h,c,1,j);C.onPostAttach(h,c,1,j)
end
local function detach(h)
 C.onPreDetach(h);h.carrier=nil;h.implement=nil
 assert(h.input.lowerDistanceToGround==.3 and h.input.lowerRotationOffset==.17)
 assert(h.px150Clearance==nil and h.px150ClearancePending==nil)
end
local function event(h,d,r)return PX150ClearanceEvent.new(h,d,r)end
local h=header();attach(h,a,1)
local old=event(h,.6,.25)
old:run(client)
assert(h.input.lowerDistanceToGround==.3,'client-origin packet accepted')
old:run(server)
assert(h.input.lowerDistanceToGround==.6,'valid current fit rejected')
assert(a.spec_attacherJoints.attacherJoints[1].jointFrameInvalid)

-- Packet arriving after detach cannot mutate input settings or recreate state.
detach(h);old:run(server)
assert(h.input.lowerDistanceToGround==.3 and h.px150Clearance==nil)
-- Same carrier and joint must still reject the previous attachment generation.
attach(h,a,1);old:run(server)
assert(h.input.lowerDistanceToGround==.3,'same-carrier stale packet accepted')
local current=event(h,.55,.24);current:run(server)
assert(h.input.lowerDistanceToGround==.55)
detach(h);attach(h,b,1);current:run(server)
assert(h.input.lowerDistanceToGround==.3,'other-carrier stale packet accepted')
local wrong=event(h,.7,.3);wrong.jointIndex=2;wrong:run(server)
assert(h.input.lowerDistanceToGround==.3,'wrong joint accepted')
wrong=event(h,.7,.3);wrong.inputIndex=2;wrong:run(server)
assert(h.input.lowerDistanceToGround==.3,'wrong input accepted')
wrong=event(h,.7,.3);wrong.carrier=nil;wrong:run(server)
assert(h.input.lowerDistanceToGround==.3,'missing carrier accepted')
wrong=event(h,.7,.3);wrong.vehicle=nil;wrong:run(server)

-- Roundtrip the entire event payload; writer and reader must match exactly.
local packet=event(h,.52,.23)
packet:writeStream(1,client)
local received=PX150ClearanceEvent.emptyNew()
received:readStream(1,server)
assert(#buffer==0 and h.input.lowerDistanceToGround==.52)
assert(received.carrier==b and received.generation==h.px150ClearanceGeneration)

-- Joining after many attachment cycles synchronizes the authoritative counter.
local src=header()
for i=1,6 do attach(src,a,1);detach(src)end
attach(src,a,1);C.apply(src,.48,.22)
local joined=header();attach(joined,a,1)
C.onWriteStream(src,1,client);C.onReadStream(joined,1,server)
assert(#buffer==0 and joined.px150ClearanceGeneration==src.px150ClearanceGeneration)
assert(joined.input.lowerDistanceToGround==.48)
local live=event(src,.49,.21);live.vehicle=joined;live:run(server)
assert(joined.input.lowerDistanceToGround==.49)
detach(joined);attach(joined,a,1);live:run(server)
assert(joined.input.lowerDistanceToGround==.3,'pre-join fit replayed after reattach')
detach(src);attach(src,a,1)
local nextFit=event(src,.46,.2);nextFit.vehicle=joined;nextFit:run(server)
assert(joined.input.lowerDistanceToGround==.46,'peer counters diverged after join/reattach')
C.apply(src,.48,.22)

-- Initial stream may precede native attachment reconstruction. Only this path
-- may retain pending pose information, and it is consumed once on matching attach.
local delayed=header()
C.onWriteStream(src,1,client);C.onReadStream(delayed,1,server)
assert(delayed.px150Clearance==nil and delayed.input.lowerDistanceToGround==.3)
assert(delayed.px150ClearancePending)
attach(delayed,a,1)
assert(delayed.px150ClearancePending==nil and delayed.input.lowerDistanceToGround==.48)
assert(delayed.px150ClearanceGeneration==src.px150ClearanceGeneration)
detach(delayed);attach(delayed,a,1)
assert(delayed.input.lowerDistanceToGround==.3,'join pose reused')
local mismatch=header()
C.onWriteStream(src,1,client);C.onReadStream(mismatch,1,server)
attach(mismatch,b,1)
assert(mismatch.input.lowerDistanceToGround==.3 and mismatch.px150ClearancePending==nil)

-- Unfitted attached and detached joins retain correct generations too.
local unfitted=header();attach(unfitted,a,1)
local fresh=header();attach(fresh,a,1)
C.onWriteStream(unfitted,1,client);C.onReadStream(fresh,1,server)
assert(fresh.px150Clearance.distance==nil and fresh.input.lowerDistanceToGround==.3)
detach(unfitted)
local unattached=header()
C.onWriteStream(unfitted,1,client);C.onReadStream(unattached,1,server)
assert(#buffer==0 and unattached.px150Clearance==nil)
assert(unattached.px150ClearanceGeneration==unfitted.px150ClearanceGeneration)
-- Actual server update still calibrates once and broadcasts the new binding.
local broadcast
Logging={info=function()end,warning=function()error('unexpected calibration failure')end}
g_server={broadcastEvent=function(_,e)broadcast=e end}
C.calibrate=function()return .5,.24,.15 end
a.getLastSpeed=function()return 0 end
local working=header();working.isServer=true;attach(working,a,1)
C.onUpdate(working,800)
assert(broadcast and broadcast.carrier==a and broadcast.inputIndex==1)
assert(broadcast.generation==working.px150ClearanceGeneration)
assert(working.input.lowerDistanceToGround==.5 and working.px150Clearance.done)
local first=broadcast;C.onUpdate(working,800);assert(broadcast==first)
print('PASS: current fits, stale detached/same-carrier/other-carrier packets, joint/input guards, sender guard, event roundtrip, joined/deferred/unfitted streams, counter sync and detach restoration.')
''')
