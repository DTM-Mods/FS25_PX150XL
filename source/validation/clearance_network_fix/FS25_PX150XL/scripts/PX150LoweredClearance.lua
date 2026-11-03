-- Fit the lowered rear clearance while preserving the original lowered cutterbar
-- clearance. Uses this carrier's live joint geometry, never an old saved pose.
PX150LoweredClearance = {}
local C = PX150LoweredClearance
local unpackValues = unpack or table.unpack
local function clamp(x, lo, hi) return math.max(lo, math.min(hi, x)) end
local function lerp(a, b, t) return a + (b-a)*t end

function C.prerequisitesPresent(specializations)
    return SpecializationUtil.hasSpecialization(Attachable, specializations)
end

function C.registerEventListeners(vehicleType)
    for _, event in ipairs({'onLoad','onPreAttach','onPostAttach','onPreDetach','onUpdate','onReadStream','onWriteStream'}) do
        SpecializationUtil.registerEventListener(vehicleType, event, C)
    end
end

function C:onLoad()
    local joint = self.spec_attachable.inputAttacherJoints[1]
    self.px150ClearanceReference = {distance=joint.lowerDistanceToGround,angle=joint.lowerRotationOffset}
    self.px150ClearanceGeneration = 0
end

-- Bounded two-variable Newton fit with backtracking. The callback returns
-- front-height error and minimum socket-clearance error, both in metres.
function C.solvePose(alpha, angle, evaluate)
    for _=1,20 do
        local f,g = evaluate(alpha,angle)
        if math.max(math.abs(f), math.abs(g)) < 0.001 then return alpha,angle end
        local da = alpha > .999 and -.001 or .001
        local dr = .001
        local fa,ga = evaluate(alpha+da,angle)
        local fr,gr = evaluate(alpha,angle+dr)
        local a,b,c,d = (fa-f)/da,(fr-f)/dr,(ga-g)/da,(gr-g)/dr
        local determinant = a*d-b*c
        if math.abs(determinant) < 1e-8 then return nil end
        local stepA = clamp((-f*d+b*g)/determinant,-.2,.2)
        local stepR = clamp((c*f-a*g)/determinant,-.2,.2)
        local improved = false
        for i=0,8 do
            local scale = .5^i
            local nextA = clamp(alpha+stepA*scale,0,1)
            local nextR = clamp(angle+stepR*scale,-math.pi/4,math.pi/4)
            local nextF,nextG = evaluate(nextA,nextR)
            if nextF*nextF+nextG*nextG < f*f+g*g then
                alpha,angle,improved = nextA,nextR,true
                break
            end
        end
        if not improved then return nil end
    end
    return nil
end

function C.apply(self, distance, angle)
    local data = self.px150Clearance
    if data == nil or data.carrier ~= self:getAttacherVehicle() then return end
    local implement = data.carrier and data.carrier:getImplementByObject(self)
    if implement == nil or implement.jointDescIndex ~= data.jointIndex then return end
    data.distance, data.angle = distance, angle
    local joint = self:getActiveInputAttacherJoint()
    if joint == nil then return end
    joint.lowerDistanceToGround, joint.lowerRotationOffset = distance, angle
    local carrier = self:getAttacherVehicle()
    if carrier ~= nil then
        local implement = carrier:getImplementByObject(self)
        local desc = implement and carrier.spec_attacherJoints.attacherJoints[implement.jointDescIndex]
        if desc ~= nil then
            carrier:updateAttacherJointRotation(desc,self)
            desc.jointFrameInvalid = true
        end
    end
end

-- Native Attachable raises onPreAttach before an optional smooth-attach delay.
-- Count attachment starts, not completions, on both peers. Join streams seed
-- this counter even when attachment reconstruction happens after our stream.
function C:onPreAttach(carrier, inputIndex, jointIndex)
    local joint = self:getActiveInputAttacherJoint()
    if joint == nil then return end
    local pending = self.px150ClearancePending
    self.px150ClearancePending = nil
    local matching = pending and pending.carrier == carrier
        and pending.inputIndex == inputIndex and pending.jointIndex == jointIndex
    self.px150ClearanceGeneration = matching and pending.generation
        or (self.px150ClearanceGeneration or 0)+1
    local reference = self.px150ClearanceReference or {distance=joint.lowerDistanceToGround,angle=joint.lowerRotationOffset}
    self.px150Clearance = {carrier=carrier, inputIndex=inputIndex, jointIndex=jointIndex,
        generation=self.px150ClearanceGeneration, elapsed=0,
        baseDistance=reference.distance, baseAngle=reference.angle}
    if matching then
        self.px150Clearance.distance,self.px150Clearance.angle = pending.distance,pending.angle
    end
end

function C:onPostAttach(carrier, inputIndex, jointIndex)
    local data = self.px150Clearance
    if data and data.carrier == carrier and data.inputIndex == inputIndex
        and data.jointIndex == jointIndex and data.distance then
        C.apply(self,data.distance,data.angle)
    end
end

function C:onPreDetach()
    local data = self.px150Clearance
    local joint = self:getActiveInputAttacherJoint()
    if data and joint and data.baseDistance then
        joint.lowerDistanceToGround, joint.lowerRotationOffset = data.baseDistance,data.baseAngle
    end
    self.px150Clearance = nil
    self.px150ClearancePending = nil
    -- Invalidate packets immediately, including while native detach is running.
    self.px150ClearanceGeneration = (self.px150ClearanceGeneration or 0)+1
end

function C.calibrate(self)
    local data = self.px150Clearance
    local carrier = data.carrier
    local desc = carrier.spec_attacherJoints.attacherJoints[data.jointIndex]
    local input = self:getActiveInputAttacherJoint()
    -- This header has no heightNodes; native lowering is the direct height-to-alpha map.
    if desc == nil or not desc.allowsLowering or #(input.heightNodes or {}) > 0
        or desc.rotationNode == desc.rootNode or desc.rotationNode2 == desc.rootNode
        or desc.upperDistanceToGround == desc.lowerDistanceToGround then return nil end
    local baselineA = clamp((data.baseDistance-desc.upperDistanceToGround)
        /(desc.lowerDistanceToGround-desc.upperDistanceToGround),0,1)
    -- Reproduce only the carrier's joint transform chain in temporary nodes.
    -- Sampling never changes the live carrier or its physics frames.
    local chain = {}
    local node = desc.jointTransform
    while node ~= desc.rootNode and node ~= 0 do
        table.insert(chain,1,node)
        node = getParent(node)
    end
    if node ~= desc.rootNode or #chain == 0 then return nil end
    local temporary = createTransformGroup('px150ClearanceFit')
    link(getRootNode(),temporary)
    setWorldTranslation(temporary,getWorldTranslation(desc.rootNode))
    setWorldRotation(temporary,getWorldRotation(desc.rootNode))
    local copies = {[desc.rootNode]=temporary}
    for _,original in ipairs(chain) do
        local copy = createTransformGroup('px150ClearanceJoint')
        link(copies[getParent(original)],copy)
        setTranslation(copy,getTranslation(original))
        setRotation(copy,getRotation(original))
        setScale(copy,getScale(original))
        copies[original] = copy
    end
    if (desc.rotationNode and not copies[desc.rotationNode])
        or (desc.rotationNode2 and not copies[desc.rotationNode2]) then
        delete(temporary)
        return nil
    end
    local sampleJoint = copies[desc.jointTransform]
    local component = self.components[1].node
    local front = {localToLocal(component,input.node,0,0,.395944)}
    local feet = {}
    for _,side in ipairs({-1,1}) do
        for _,x in ipairs({1.1515,1.3965}) do
            for _,z in ipairs({-1.53,-1.23}) do
                table.insert(feet,{localToLocal(component,input.node,side*x,-.374,z)})
            end
        end
    end
    local terrain = g_currentMission.terrainRootNode
    local function clearance(point)
        local x,y,z = localToWorld(sampleJoint,unpackValues(point))
        return y-getTerrainHeightAtWorldPos(terrain,x,0,z)
    end
    local function pose(alpha,angle)
        if desc.rotationNode then
            local rotation={}
            for i=1,3 do rotation[i]=lerp(desc.upperRotation[i],desc.lowerRotation[i],alpha) end
            setRotation(copies[desc.rotationNode],unpackValues(rotation))
        end
        if desc.rotationNode2 then
            local rotation={}
            for i=1,3 do rotation[i]=lerp(desc.upperRotation2[i],desc.lowerRotation2[i],alpha) end
            setRotation(copies[desc.rotationNode2],unpackValues(rotation))
        end
        setRotation(sampleJoint,unpackValues(desc.jointOrigRot))
        local target = lerp(input.upperRotationOffset,angle,alpha)
        local own = lerp(desc.upperRotationOffset,desc.lowerRotationOffset,alpha)
        rotateAboutLocalAxis(sampleJoint,target-own,0,0,1)
    end
    pose(baselineA,data.baseAngle)
    local referenceFront = clearance(front)
    local function errors(alpha,angle)
        pose(alpha,angle)
        local lowest = math.huge
        for _,foot in ipairs(feet) do lowest = math.min(lowest,clearance(foot)) end
        return clearance(front)-referenceFront,lowest-.05
    end
    local alpha,angle = C.solvePose(baselineA,data.baseAngle,errors)
    if alpha == nil then delete(temporary);return nil end
    local frontError,rearError = errors(alpha,angle)
    delete(temporary)
    if math.abs(frontError)>.002 or math.abs(rearError)>.002 then return nil end
    return lerp(desc.upperDistanceToGround,desc.lowerDistanceToGround,alpha),angle,referenceFront
end

function C:onUpdate(dt)
    local data = self.px150Clearance
    if not self.isServer or data == nil or data.done then return end
    local implement = data.carrier:getImplementByObject(self)
    if implement == nil or implement.attachingIsInProgress then return end
    data.elapsed = data.elapsed+dt
    if data.elapsed<750 or data.carrier:getLastSpeed()>1 then return end
    data.done = true
    local distance,angle,front = C.calibrate(self)
    if distance == nil then
        Logging.warning('PX150 lowered clearance: no reachable 5 cm solution; original cutting setup retained.')
        return
    end
    C.apply(self,distance,angle)
    g_server:broadcastEvent(PX150ClearanceEvent.new(self,distance,angle),nil,nil,self)
    Logging.info('PX150 lowered clearance: original front %.3f m retained; rear target 0.050 m; lower %.4f m / offset %.3f deg.',front,distance,math.deg(angle))
end

function C:onWriteStream(streamId,connection)
    local data = self.px150Clearance
    streamWriteInt32(streamId,self.px150ClearanceGeneration or 0)
    streamWriteBool(streamId,data ~= nil)
    if data ~= nil then
        NetworkUtil.writeNodeObject(streamId,data.carrier)
        streamWriteInt32(streamId,data.inputIndex)
        streamWriteInt32(streamId,data.jointIndex)
        streamWriteBool(streamId,data.distance ~= nil)
        if data.distance ~= nil then
            streamWriteFloat32(streamId,data.distance);streamWriteFloat32(streamId,data.angle)
        end
    end
end

function C:onReadStream(streamId,connection)
    local generation = streamReadInt32(streamId)
    self.px150ClearanceGeneration = generation
    self.px150ClearancePending = nil
    if streamReadBool(streamId) then
        local incoming = {generation=generation,carrier=NetworkUtil.readNodeObject(streamId),
            inputIndex=streamReadInt32(streamId),jointIndex=streamReadInt32(streamId)}
        if streamReadBool(streamId) then
            incoming.distance,incoming.angle = streamReadFloat32(streamId),streamReadFloat32(streamId)
        end
        local data = self.px150Clearance
        if data and data.carrier == incoming.carrier and data.inputIndex == incoming.inputIndex
            and data.jointIndex == incoming.jointIndex then
            data.generation = generation
            if incoming.distance then C.apply(self,incoming.distance,incoming.angle) end
        elseif incoming.carrier ~= nil then
            -- Only initial object streaming may wait for native attachment
            -- reconstruction. Live fit events are never queued for later use.
            self.px150ClearancePending = incoming
        end
    end
end

PX150ClearanceEvent = {}
local PX150ClearanceEvent_mt = Class(PX150ClearanceEvent,Event)
InitEventClass(PX150ClearanceEvent,'PX150ClearanceEvent')
function PX150ClearanceEvent.emptyNew() return Event.new(PX150ClearanceEvent_mt) end
function PX150ClearanceEvent.new(vehicle,distance,angle)
    local self = PX150ClearanceEvent.emptyNew()
    self.vehicle,self.distance,self.angle = vehicle,distance,angle
    local data = vehicle.px150Clearance
    self.carrier,self.inputIndex,self.jointIndex,self.generation =
        data.carrier,data.inputIndex,data.jointIndex,data.generation
    return self
end
function PX150ClearanceEvent:writeStream(streamId,connection)
    NetworkUtil.writeNodeObject(streamId,self.vehicle)
    NetworkUtil.writeNodeObject(streamId,self.carrier)
    streamWriteInt32(streamId,self.inputIndex);streamWriteInt32(streamId,self.jointIndex)
    streamWriteInt32(streamId,self.generation)
    streamWriteFloat32(streamId,self.distance);streamWriteFloat32(streamId,self.angle)
end
function PX150ClearanceEvent:readStream(streamId,connection)
    self.vehicle = NetworkUtil.readNodeObject(streamId)
    self.carrier = NetworkUtil.readNodeObject(streamId)
    self.inputIndex,self.jointIndex = streamReadInt32(streamId),streamReadInt32(streamId)
    self.generation = streamReadInt32(streamId)
    self.distance,self.angle = streamReadFloat32(streamId),streamReadFloat32(streamId)
    self:run(connection)
end
function PX150ClearanceEvent:run(connection)
    if connection:getIsServer() and self.vehicle ~= nil then
        local data = self.vehicle.px150Clearance
        if data and data.carrier == self.carrier and data.inputIndex == self.inputIndex
            and data.jointIndex == self.jointIndex and data.generation == self.generation
            and self.vehicle.px150ClearanceGeneration == self.generation then
            C.apply(self.vehicle,self.distance,self.angle)
        end
    end
end
