-- Let this header cut every crop the loaded map lists for grain headers.
-- Crops without a swath conversion on the map are laid as their own grain,
-- and the grain pickup header is taught to collect that grain again.
PX150GrainHeaderCrops = {}
local G = PX150GrainHeaderCrops
G.extraFruits = {}

-- Runs after the map's fruit types, categories and converters are loaded.
-- Nothing is named here: the list comes from the map every time.
function G.collectFromMap(manager)
    G.extraFruits = {}
    local swaths = manager:getConverterDataByName("COMBINE_MOWER") or {}
    for _, fruitTypeIndex in ipairs(manager:getFruitTypeIndicesByCategoryNames("GRAINHEADER") or {}) do
        local fillTypeIndex = manager:getFillTypeIndexByFruitTypeIndex(fruitTypeIndex)
        if swaths[fruitTypeIndex] == nil and fillTypeIndex ~= nil then
            G.extraFruits[fruitTypeIndex] = fillTypeIndex
        end
    end
    G.teachPickup()
end

-- The pickup header reads this shared converter while working, so adding to it
-- again from the header's own load covers either map load order. Safe to repeat.
function G.teachPickup()
    local pickupConverter = g_fillTypeManager.converterNameToIndex["PICKUPHEADER_GRAIN"]
    local pickupData = g_fillTypeManager:getConverterDataByName("PICKUPHEADER_GRAIN")
    if pickupData == nil then return end
    for _, fillTypeIndex in pairs(G.extraFruits) do
        if pickupData[fillTypeIndex] == nil then
            g_fillTypeManager:addFillTypeConversion(pickupConverter, fillTypeIndex, fillTypeIndex, 1)
        end
    end
end

FruitTypeManager.loadMapData = Utils.appendedFunction(FruitTypeManager.loadMapData, function(self)
    G.collectFromMap(self)
end)

function G.prerequisitesPresent(specializations)
    return SpecializationUtil.hasSpecialization(Mower, specializations)
end

function G.registerEventListeners(vehicleType)
    SpecializationUtil.registerEventListener(vehicleType, "onLoad", G)
end

-- After Mower.onLoad and before PX150YieldBonus.onPostLoad, so added crops get the same bonus.
function G:onLoad(savegame)
    local spec = self.spec_mower
    G.teachPickup()
    for fruitTypeIndex, fillTypeIndex in pairs(G.extraFruits) do
        -- Only crops the map can actually lay on the ground.
        if spec.fruitTypeConverters[fruitTypeIndex] == nil
            and g_densityMapHeightManager:getDensityMapHeightTypeByFillTypeIndex(fillTypeIndex) ~= nil then
            spec.fruitTypeConverters[fruitTypeIndex] = {fillTypeIndex=fillTypeIndex, conversionFactor=1}
            if self.addAIFruitRequirement ~= nil then
                local desc = g_fruitTypeManager:getFruitTypeByIndex(fruitTypeIndex)
                self:addAIFruitRequirement(desc.index, desc.minHarvestingGrowthState, desc.maxHarvestingGrowthState)
            end
        end
    end
end
