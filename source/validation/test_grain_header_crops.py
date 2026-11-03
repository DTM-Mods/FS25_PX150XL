"""Run with lupa available on PYTHONPATH; no game installation required."""
from pathlib import Path
import xml.etree.ElementTree as ET
from lupa.lua51 import LuaRuntime

root = Path(__file__).resolve().parents[2]
lua = LuaRuntime()
# Mock map: fruits 1 WHEAT, 2 RYE, 3 TRITICALE, 4 SORGHUM (no ground type), 5 MAIZE (not a grain header crop).
lua.execute("""
Mower = {}
Utils = {appendedFunction = function(a, b) return function(...) a(...); b(...) end end}
FruitTypeManager = {loadMapData = function(self) end}
SpecializationUtil = {
    hasSpecialization = function(wanted, specs)
        for _, spec in ipairs(specs) do
            if spec == wanted then return true end
        end
        return false
    end,
    registerEventListener = function(vehicleType, event, listener)
        assert(event == 'onLoad')
        vehicleType.listener = listener
    end
}
g_fruitTypeManager = {
    getConverterDataByName = function(self, name)
        assert(name == 'COMBINE_MOWER')
        return {[1] = {fillTypeIndex=1001, conversionFactor=1}}
    end,
    getFruitTypeIndicesByCategoryNames = function(self, names) assert(names == 'GRAINHEADER'); return {1, 2, 3, 4} end,
    getFillTypeIndexByFruitTypeIndex = function(self, i) return ({101, 102, 103, 104, 105})[i] end,
    getFruitTypeByIndex = function(self, i) return {index=i, minHarvestingGrowthState=5, maxHarvestingGrowthState=6} end
}
local pickup = {[1001] = {targetFillTypeIndex=101, conversionFactor=1}}
g_fillTypeManager = {
    converterNameToIndex = {PICKUPHEADER_GRAIN = 7},
    getConverterDataByName = function(self, name) assert(name == 'PICKUPHEADER_GRAIN'); return pickup end,
    addFillTypeConversion = function(self, c, s, t, f) assert(c == 7); pickup[s] = {targetFillTypeIndex=t, conversionFactor=f} end
}
g_densityMapHeightManager = {
    getDensityMapHeightTypeByFillTypeIndex = function(self, f) if f ~= 104 then return {} end end
}
pickupTable = pickup
""")
lua.execute((root / 'scripts/PX150GrainHeaderCrops.lua').read_text())
lua.execute("""
local G = PX150GrainHeaderCrops
assert(G.prerequisitesPresent({Mower}))
local vehicleType = {}
G.registerEventListeners(vehicleType)
FruitTypeManager.loadMapData(g_fruitTypeManager)

-- Wheat keeps its map swath; rye, triticale and sorghum are found from the category.
assert(G.extraFruits[1] == nil and G.extraFruits[5] == nil)
assert(G.extraFruits[2] == 102 and G.extraFruits[3] == 103 and G.extraFruits[4] == 104)
assert(pickupTable[102].targetFillTypeIndex == 102 and pickupTable[103].targetFillTypeIndex == 103)
assert(pickupTable[1001].targetFillTypeIndex == 101)

local mapSwath = {fillTypeIndex=1001, conversionFactor=1}
local ai = {}
local header = {spec_mower={fruitTypeConverters={[1]=mapSwath}},
    addAIFruitRequirement = function(self, i) ai[#ai+1] = i end}
vehicleType.listener.onLoad(header)
local c = header.spec_mower.fruitTypeConverters
assert(c[1] == mapSwath)
assert(c[2].fillTypeIndex == 102 and c[2].conversionFactor == 1)
assert(c[3].fillTypeIndex == 103)
assert(c[4] == nil) -- no ground type for this grain on the map
assert(c[5] == nil)
assert(#ai == 2)
""")
desc = ET.parse(root / 'modDesc.xml').getroot()
specs = [s.get('name') for s in desc.find('vehicleTypes/type')]
assert 'grainHeaderCrops' in specs and specs.index('grainHeaderCrops') < specs.index('yieldBonus')
assert any(s.get('filename') == 'scripts/PX150GrainHeaderCrops.lua' for s in desc.find('specializations'))
print('PASS test_grain_header_crops')
