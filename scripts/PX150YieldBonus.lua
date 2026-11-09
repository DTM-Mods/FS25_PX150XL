-- Apply a fixed yield bonus to alfalfa, clover and field grass only, on this header's private
-- converter records. Every other crop keeps the map's own factor.
PX150YieldBonus = {}

PX150YieldBonus.FACTOR = 1.25
PX150YieldBonus.FRUITS = {ALFALFA=true, CLOVER=true, FIELDGRASS=true}

function PX150YieldBonus.prerequisitesPresent(specializations)
    return SpecializationUtil.hasSpecialization(Mower, specializations)
end

function PX150YieldBonus.registerEventListeners(vehicleType)
    SpecializationUtil.registerEventListener(vehicleType, "onPostLoad", PX150YieldBonus)
end

function PX150YieldBonus:onPostLoad(savegame)
    local spec = self.spec_mower
    local converters = {}

    -- Mower.onLoad references the map's shared converter records. Copy each
    -- boosted record before changing its factor so other implements keep their yield.
    for inputFruitType, converterData in pairs(spec.fruitTypeConverters) do
        local fruitType = g_fruitTypeManager:getFruitTypeByIndex(inputFruitType)
        if fruitType ~= nil and PX150YieldBonus.FRUITS[fruitType.name] then
            local copy = {}
            for key, value in pairs(converterData) do
                copy[key] = value
            end
            copy.conversionFactor = converterData.conversionFactor * PX150YieldBonus.FACTOR
            converters[inputFruitType] = copy
        else
            converters[inputFruitType] = converterData
        end
    end

    spec.fruitTypeConverters = converters
end
