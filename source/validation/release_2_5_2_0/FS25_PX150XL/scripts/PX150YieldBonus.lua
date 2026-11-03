-- Apply a fixed yield bonus only to this header's private converter records.
PX150YieldBonus = {}

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
    -- record before changing its factor so other implements keep their yield.
    for inputFruitType, converterData in pairs(spec.fruitTypeConverters) do
        local copy = {}
        for key, value in pairs(converterData) do
            copy[key] = value
        end
        copy.conversionFactor = converterData.conversionFactor * 1.10
        converters[inputFruitType] = copy
    end

    spec.fruitTypeConverters = converters
end
