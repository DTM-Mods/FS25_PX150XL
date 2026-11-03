-- Let this header cut every crop the loaded map lists for grain headers.
-- Rye and triticale are laid as this mod's own grain-coloured swaths; if the map
-- has no free heap slot for them, as the map swath closest in colour instead.
-- Other crops without a swath conversion on the map are laid as their own grain.
-- The grain pickup header is taught to collect whatever is laid.
PX150GrainHeaderCrops = {}
local G = PX150GrainHeaderCrops
G.extraFruits = {}

-- Fruit name -> this mod's swath fill type (fillTypes/px150Swaths.xml).
G.OWN_SWATHS = {RYE="PX150_RYE_SWATH", TRITICALE="PX150_TRITICALE_SWATH"}
-- Average colour of the grain texture each crop uses in a trailer, and of the
-- base game swaths, measured from the game's fillPlanes textures.
G.GRAIN_COLOURS = {RYE={139,129,102}, TRITICALE={168,127,69}}
G.SWATH_COLOURS = {WHEAT_CUT={143,113,62}, BARLEY_CUT={145,109,54}, OAT_CUT={131,104,53},
    CANOLA_CUT={141,107,68}, SOYBEAN_CUT={119,96,43}}

-- Runs after the map's fruit types, categories and converters are loaded.
-- Nothing is named here: the list comes from the map every time.
function G.collectFromMap(manager)
    G.extraFruits = {}
    G.drops = nil
    local swaths = manager:getConverterDataByName("COMBINE_MOWER") or {}
    for _, fruitTypeIndex in ipairs(manager:getFruitTypeIndicesByCategoryNames("GRAINHEADER") or {}) do
        local fillTypeIndex = manager:getFillTypeIndexByFruitTypeIndex(fruitTypeIndex)
        if swaths[fruitTypeIndex] == nil and fillTypeIndex ~= nil then
            G.extraFruits[fruitTypeIndex] = fillTypeIndex
        end
    end
end

FruitTypeManager.loadMapData = Utils.appendedFunction(FruitTypeManager.loadMapData, function(self)
    G.collectFromMap(self)
end)

-- The base pickup effects list only the base swaths; without this the PW8 shows no
-- straw going in for the rye and triticale swaths.
G.modDirectory = g_currentModDirectory
G.modName = g_currentModName
MotionPathEffectManager.loadMapData = Utils.appendedFunction(MotionPathEffectManager.loadMapData, function(self)
    if g_fillTypeManager:getFillTypeIndexByName("PX150_RYE_SWATH") ~= nil then
        self:loadMotionPathEffectsXML("fillTypes/px150PickupEffects.xml", G.modDirectory, G.modName)
    end
end)

local function canLay(fillTypeIndex)
    return fillTypeIndex ~= nil and g_densityMapHeightManager:getDensityMapHeightTypeByFillTypeIndex(fillTypeIndex) ~= nil
end

-- The map swath (a COMBINE_MOWER target the map can lay) closest in colour to the grain.
function G.closestMapSwath(grainColour)
    local best, bestDistance
    for _, converted in pairs(g_fruitTypeManager:getConverterDataByName("COMBINE_MOWER") or {}) do
        local colour = G.SWATH_COLOURS[g_fillTypeManager:getFillTypeNameByIndex(converted.fillTypeIndex)]
        if colour ~= nil and canLay(converted.fillTypeIndex) then
            local distance = 0
            for i = 1, 3 do
                distance = distance + (colour[i] - grainColour[i])^2
            end
            if bestDistance == nil or distance < bestDistance then
                best, bestDistance = converted.fillTypeIndex, distance
            end
        end
    end
    return best
end

-- Decides once per map what each extra crop is laid as. Heap types are all
-- registered by the time vehicles load, so this runs from the first header's onLoad.
function G.resolveDrops()
    if G.drops ~= nil then return end
    G.drops = {}
    local pickupConverter = g_fillTypeManager.converterNameToIndex["PICKUPHEADER_GRAIN"]
    local pickupData = g_fillTypeManager:getConverterDataByName("PICKUPHEADER_GRAIN")
    for fruitTypeIndex, grainFillTypeIndex in pairs(G.extraFruits) do
        local name = g_fruitTypeManager:getFruitTypeByIndex(fruitTypeIndex).name
        local own = G.OWN_SWATHS[name] and g_fillTypeManager:getFillTypeIndexByName(G.OWN_SWATHS[name])
        local dropFillTypeIndex
        if canLay(own) then
            dropFillTypeIndex = own
        elseif G.GRAIN_COLOURS[name] ~= nil then
            -- Picked up as that map swath's own crop.
            dropFillTypeIndex = G.closestMapSwath(G.GRAIN_COLOURS[name])
            if dropFillTypeIndex ~= nil then
                Logging.info("PX150XL: no free heap slot for %s swath, laying %s instead", name,
                    g_fillTypeManager:getFillTypeNameByIndex(dropFillTypeIndex))
            end
        end
        if dropFillTypeIndex == nil and canLay(grainFillTypeIndex) then
            dropFillTypeIndex = grainFillTypeIndex
        end
        if dropFillTypeIndex ~= nil then
            G.drops[fruitTypeIndex] = dropFillTypeIndex
            -- The pickup header reads this shared converter live while working.
            if pickupData ~= nil and pickupData[dropFillTypeIndex] == nil then
                g_fillTypeManager:addFillTypeConversion(pickupConverter, dropFillTypeIndex, grainFillTypeIndex, 1)
            end
        end
    end
end

function G.prerequisitesPresent(specializations)
    return SpecializationUtil.hasSpecialization(Mower, specializations)
end

function G.registerEventListeners(vehicleType)
    SpecializationUtil.registerEventListener(vehicleType, "onLoad", G)
end

-- After Mower.onLoad and before PX150YieldBonus.onPostLoad, so added crops get the same bonus.
function G:onLoad(savegame)
    local spec = self.spec_mower
    G.resolveDrops()
    for fruitTypeIndex, fillTypeIndex in pairs(G.drops) do
        if spec.fruitTypeConverters[fruitTypeIndex] == nil then
            spec.fruitTypeConverters[fruitTypeIndex] = {fillTypeIndex=fillTypeIndex, conversionFactor=1}
            if self.addAIFruitRequirement ~= nil then
                local desc = g_fruitTypeManager:getFruitTypeByIndex(fruitTypeIndex)
                self:addAIFruitRequirement(desc.index, desc.minHarvestingGrowthState, desc.maxHarvestingGrowthState)
            end
        end
    end
end
