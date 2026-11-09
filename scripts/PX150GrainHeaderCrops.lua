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
-- straw going in for the rye and triticale swaths. Mod fill types load after the map's
-- motion path effects, so the effect file is loaded once ours exist.
G.modDirectory = g_currentModDirectory
G.modName = g_currentModName
FillTypeManager.loadModFillTypes = Utils.appendedFunction(FillTypeManager.loadModFillTypes, function(self)
    if self:getFillTypeIndexByName("PX150_RYE_SWATH") ~= nil and g_motionPathEffectManager ~= nil then
        g_motionPathEffectManager:loadMotionPathEffectsXML("fillTypes/px150PickupEffects.xml", G.modDirectory, G.modName)
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

-- The game links wheat, barley, oat, canola and soybean to their swaths in the crop
-- files (windrow cutFillType + windrowCutFactor). Rye and triticale have no such link,
-- so they were laid at straw volume and the PW8 counted every swath litre as grain:
-- about 4x the grain and the straw. Measure what the game does for a linked crop and
-- set the swath crop to the same, scaled by its grain yield against that crop.
-- This also gives them the same pickup bonus as the linked crop.
G.TEST_AREA = 10000
G.REFERENCE_FRUIT = "WHEAT"

local function positive(x)
    return type(x) == "number" and x > 0 and x < math.huge
end

local function swathGrainPerLiter(swathFillTypeIndex)
    local liters = g_fruitTypeManager:getCutWindrowHarvestFillLevel(swathFillTypeIndex, 1000)
    return type(liters) == "number" and liters / 1000 or nil
end

-- The crop the game links to this swath, and its header (COMBINE_MOWER) factor.
local function linkedCrop(swathFillTypeIndex)
    local fallback, fallbackFactor
    for fruitTypeIndex, converted in pairs(g_fruitTypeManager:getConverterDataByName("COMBINE_MOWER") or {}) do
        if converted.fillTypeIndex == swathFillTypeIndex then
            local desc = g_fruitTypeManager:getFruitTypeByIndex(fruitTypeIndex)
            if desc ~= nil and desc.windrowCutFillType ~= nil and desc.windrowCutFillType.index == swathFillTypeIndex then
                return fruitTypeIndex, converted.conversionFactor
            end
            fallback, fallbackFactor = fruitTypeIndex, converted.conversionFactor
        end
    end
    return fallback, fallbackFactor
end

-- Header factor for laying this crop as dropFillTypeIndex and, for an own swath, the
-- PW8 factor. nil when the game can't be measured: amounts are then left as before.
function G.matchSwathAmounts(fruitTypeIndex, dropFillTypeIndex, isOwnSwath, pickupData)
    local manager = g_fruitTypeManager
    if manager.getFruitTypeAreaLiters == nil or manager.getCutWindrowHarvestFillLevel == nil then
        return nil
    end
    local refSwath = dropFillTypeIndex
    if isOwnSwath then
        local ref = manager:getFruitTypeByName(G.REFERENCE_FRUIT)
        refSwath = ref ~= nil and ref.windrowCutFillType ~= nil and ref.windrowCutFillType.index
            or g_fillTypeManager:getFillTypeIndexByName(G.REFERENCE_FRUIT .. "_CUT")
    end
    local refFruitIndex, refHeaderFactor = linkedCrop(refSwath)
    if refFruitIndex == nil then
        return nil
    end
    local fruit, ref = manager:getFruitTypeByIndex(fruitTypeIndex), manager:getFruitTypeByIndex(refFruitIndex)
    local refLaid = manager:getFruitTypeAreaLiters(refFruitIndex, G.TEST_AREA, true)
    local fruitLaid = manager:getFruitTypeAreaLiters(fruitTypeIndex, G.TEST_AREA, true)
    if not (positive(refLaid) and positive(fruitLaid) and positive(fruit.literPerSqm) and positive(ref.literPerSqm)) then
        return nil
    end
    local refGrain = swathGrainPerLiter(refSwath)
    local refPickup = pickupData ~= nil and pickupData[refSwath] ~= nil and pickupData[refSwath].conversionFactor or 1
    local targetLaid = refLaid * (refHeaderFactor or 1) * fruit.literPerSqm / ref.literPerSqm
    local headerFactor = targetLaid / fruitLaid
    local pickupFactor, rawGrain
    if isOwnSwath then
        rawGrain = swathGrainPerLiter(dropFillTypeIndex)
        if not (positive(refGrain) and positive(rawGrain)) then
            return nil
        end
        pickupFactor = refGrain * refPickup / rawGrain
    end
    Logging.info("PX150XL: %s amounts matched to %s. Per test area: was %.0f L laid -> %.0f L grain; now %.0f L laid -> %.0f L grain (%s: %.0f L laid -> %.0f L grain). Header x%.3f, PW8 x%.3f",
        fruit.name, ref.name, fruitLaid, fruitLaid * (rawGrain or refGrain or 0), targetLaid,
        targetLaid * (refGrain or 0) * refPickup, ref.name, refLaid * (refHeaderFactor or 1),
        refLaid * (refHeaderFactor or 1) * (refGrain or 0) * refPickup, headerFactor, pickupFactor or 1)
    return headerFactor, pickupFactor
end

-- Decides once per map what each extra crop is laid as. Heap types are all
-- registered by the time vehicles load, so this runs from the first header's onLoad.
function G.resolveDrops()
    if G.drops ~= nil then return end
    G.drops = {}
    G.headerFactors = {}
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
            local pickupFactor = 1
            if dropFillTypeIndex ~= grainFillTypeIndex then
                local headerFactor, ownPickupFactor = G.matchSwathAmounts(fruitTypeIndex, dropFillTypeIndex,
                    dropFillTypeIndex == own, pickupData)
                if headerFactor ~= nil then
                    G.headerFactors[fruitTypeIndex] = headerFactor
                    pickupFactor = ownPickupFactor or 1
                else
                    Logging.warning("PX150XL: could not measure swath amounts for %s; left unchanged", name)
                end
            elseif g_fruitTypeManager.getFruitTypeAreaLiters ~= nil then
                -- Laid as its own grain: the mower drops windrow litres, but the pickup
                -- counts every litre as grain. Scale the drop down to the grain amount.
                local laid = g_fruitTypeManager:getFruitTypeAreaLiters(fruitTypeIndex, G.TEST_AREA, true)
                local grain = g_fruitTypeManager:getFruitTypeAreaLiters(fruitTypeIndex, G.TEST_AREA, false)
                if positive(laid) and positive(grain) and grain < laid then
                    G.headerFactors[fruitTypeIndex] = grain / laid
                    Logging.info("PX150XL: %s grain row matched to grain yield. Per test area: was %.0f L laid, now %.0f L. Header x%.3f",
                        name, laid, grain, grain / laid)
                end
            end
            -- The pickup header reads this shared converter live while working.
            if pickupData ~= nil and pickupData[dropFillTypeIndex] == nil then
                g_fillTypeManager:addFillTypeConversion(pickupConverter, dropFillTypeIndex, grainFillTypeIndex, pickupFactor)
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
            spec.fruitTypeConverters[fruitTypeIndex] = {fillTypeIndex=fillTypeIndex,
                conversionFactor=G.headerFactors[fruitTypeIndex] or 1}
            if self.addAIFruitRequirement ~= nil then
                local desc = g_fruitTypeManager:getFruitTypeByIndex(fruitTypeIndex)
                self:addAIFruitRequirement(desc.index, desc.minHarvestingGrowthState, desc.maxHarvestingGrowthState)
            end
        end
    end
end

-- Shop crop list: every crop this header cuts on the loaded map, i.e. the map's
-- grain-header crops plus every crop in its COMBINE_MOWER list (e.g. alfalfa, clover).
-- storeData/specs/fruitTypeCategories=grainHeader makes the game create the list;
-- this adds the mower crops to it.
function G.getShopFillTypes(fillTypes)
    local result, seen = {}, {}
    local function add(fillTypeIndex)
        if fillTypeIndex ~= nil and not seen[fillTypeIndex] then
            seen[fillTypeIndex] = true
            table.insert(result, fillTypeIndex)
        end
    end
    for _, fillTypeIndex in ipairs(fillTypes or {}) do
        add(fillTypeIndex)
    end
    local manager = g_fruitTypeManager
    local mowerFruits = {}
    for fruitTypeIndex, _ in pairs(manager:getConverterDataByName("COMBINE_MOWER") or {}) do
        table.insert(mowerFruits, fruitTypeIndex)
    end
    table.sort(mowerFruits)
    for _, fruitTypeIndex in ipairs(mowerFruits) do
        add(manager:getFillTypeIndexByFruitTypeIndex(fruitTypeIndex))
    end
    return result
end

if FillUnit ~= nil and FillUnit.getSpecValueFillTypes ~= nil then
    local original = FillUnit.getSpecValueFillTypes
    FillUnit.getSpecValueFillTypes = function(storeItem, realItem, configurations, ...)
        local fillTypes = original(storeItem, realItem, configurations, ...)
        if storeItem ~= nil and storeItem.xmlFilename ~= nil and G.modDirectory ~= nil
            and storeItem.xmlFilename:lower() == (G.modDirectory .. "px150xlWindrower.xml"):lower() then
            return G.getShopFillTypes(fillTypes)
        end
        return fillTypes
    end
end
