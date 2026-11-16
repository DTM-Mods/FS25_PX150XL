-- Fixed yield bonuses on this header's private converter records:
-- alfalfa, clover and field grass +25%; any crop whose combine leaves no swath on the
-- loaded map (no windrow fill type in its crop file) +25%. Every other crop keeps the map's factor.
PX150YieldBonus = {}

PX150YieldBonus.FACTOR = 1.25
PX150YieldBonus.FRUITS = {ALFALFA=true, CLOVER=true, FIELDGRASS=true}
PX150YieldBonus.NO_SWATH_FACTOR = 1.25

function PX150YieldBonus.getFactor(fruitType)
    if PX150YieldBonus.FRUITS[fruitType.name] then
        return PX150YieldBonus.FACTOR
    elseif fruitType.windrowFillType == nil then
        return PX150YieldBonus.NO_SWATH_FACTOR
    end
    return nil
end

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
        local factor = fruitType ~= nil and PX150YieldBonus.getFactor(fruitType)
        if factor then
            local copy = {}
            for key, value in pairs(converterData) do
                copy[key] = value
            end
            copy.conversionFactor = converterData.conversionFactor * factor
            converters[inputFruitType] = copy
        else
            converters[inputFruitType] = converterData
        end
    end

    spec.fruitTypeConverters = converters
end
