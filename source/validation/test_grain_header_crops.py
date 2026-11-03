"""Run with lupa available on PYTHONPATH; no game installation required."""
from pathlib import Path
import xml.etree.ElementTree as ET
from lupa.lua51 import LuaRuntime

root = Path(__file__).resolve().parents[2]


def run(map_full):
    lua = LuaRuntime()
    lua.globals().mapFull = map_full
    # Mock map: fruits 1 WHEAT, 2 RYE, 3 TRITICALE, 4 SORGHUM (no ground type), 5 MAIZE (not a grain header crop),
    # 6 SPELT (grain heap only), 7 CANOLA. Swath fills 1001 WHEAT_CUT, 1007 CANOLA_CUT; own swaths 2002 rye, 2003 triticale.
    lua.execute("""
    Mower = {}
    Utils = {appendedFunction = function(a, b) return function(...) a(...); b(...) end end}
    FruitTypeManager = {loadMapData = function(self) end}
    Logging = {info = function(...) end}
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
    local names = {'WHEAT', 'RYE', 'TRITICALE', 'SORGHUM', 'MAIZE', 'SPELT', 'CANOLA'}
    g_fruitTypeManager = {
        getConverterDataByName = function(self, name)
            assert(name == 'COMBINE_MOWER')
            return {[1] = {fillTypeIndex=1001, conversionFactor=1}, [7] = {fillTypeIndex=1007, conversionFactor=1}}
        end,
        getFruitTypeIndicesByCategoryNames = function(self, names) assert(names == 'GRAINHEADER'); return {1, 2, 3, 4, 6, 7} end,
        getFillTypeIndexByFruitTypeIndex = function(self, i) return 100 + i end,
        getFruitTypeByIndex = function(self, i) return {index=i, name=names[i], minHarvestingGrowthState=5, maxHarvestingGrowthState=6} end
    }
    local fillNames = {[1001]='WHEAT_CUT', [1007]='CANOLA_CUT', [2002]='PX150_RYE_SWATH', [2003]='PX150_TRITICALE_SWATH'}
    local pickup = {[1001] = {targetFillTypeIndex=101, conversionFactor=1}, [1007] = {targetFillTypeIndex=107, conversionFactor=1}}
    g_fillTypeManager = {
        converterNameToIndex = {PICKUPHEADER_GRAIN = 7},
        getConverterDataByName = function(self, name) assert(name == 'PICKUPHEADER_GRAIN'); return pickup end,
        addFillTypeConversion = function(self, c, s, t, f) assert(c == 7); pickup[s] = {targetFillTypeIndex=t, conversionFactor=f} end,
        getFillTypeIndexByName = function(self, n) for i, v in pairs(fillNames) do if v == n then return i end end end,
        getFillTypeNameByIndex = function(self, i) return fillNames[i] end
    }
    g_densityMapHeightManager = {
        getDensityMapHeightTypeByFillTypeIndex = function(self, f)
            if f == 104 then return nil end
            if mapFull and (f == 2002 or f == 2003) then return nil end
            return {}
        end
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

    -- Wheat and canola keep their map swath; rye, triticale, sorghum and spelt are found from the category.
    assert(G.extraFruits[1] == nil and G.extraFruits[5] == nil and G.extraFruits[7] == nil)
    assert(G.extraFruits[2] == 102 and G.extraFruits[3] == 103 and G.extraFruits[4] == 104 and G.extraFruits[6] == 106)

    local mapSwath = {fillTypeIndex=1001, conversionFactor=1}
    local ai = {}
    local function newHeader()
        return {spec_mower={fruitTypeConverters={[1]=mapSwath}}, addAIFruitRequirement = function(self, i) ai[#ai+1] = i end}
    end
    local header = newHeader()
    vehicleType.listener.onLoad(header)
    local c = header.spec_mower.fruitTypeConverters
    assert(c[1] == mapSwath)
    if mapFull then
        -- Closest map swath by colour: rye -> canola swath, triticale -> wheat swath; picked up as those crops.
        assert(c[2].fillTypeIndex == 1007 and c[3].fillTypeIndex == 1001)
        assert(pickupTable[1007].targetFillTypeIndex == 107 and pickupTable[1001].targetFillTypeIndex == 101)
    else
        assert(c[2].fillTypeIndex == 2002 and c[2].conversionFactor == 1 and c[3].fillTypeIndex == 2003)
        assert(pickupTable[2002].targetFillTypeIndex == 102 and pickupTable[2003].targetFillTypeIndex == 103)
    end
    assert(c[4] == nil) -- no ground type for this grain on the map
    assert(c[5] == nil)
    assert(c[6].fillTypeIndex == 106 and pickupTable[106].targetFillTypeIndex == 106) -- other crops: grain strip
    assert(#ai == 3)

    -- A second header reuses the same decisions.
    local second = newHeader()
    vehicleType.listener.onLoad(second)
    assert(second.spec_mower.fruitTypeConverters[2].fillTypeIndex == c[2].fillTypeIndex)
    """)


run(False)
run(True)
desc = ET.parse(root / 'modDesc.xml').getroot()
specs = [s.get('name') for s in desc.find('vehicleTypes/type')]
assert 'grainHeaderCrops' in specs and specs.index('grainHeaderCrops') < specs.index('yieldBonus')
assert any(s.get('filename') == 'scripts/PX150GrainHeaderCrops.lua' for s in desc.find('specializations'))
assert desc.find('fillTypes').get('filename') == 'fillTypes/px150Swaths.xml'
assert desc.find('densityMapHeightTypes').get('filename') == 'fillTypes/px150SwathHeights.xml'
fills = ET.parse(root / 'fillTypes/px150Swaths.xml').getroot()
heights = ET.parse(root / 'fillTypes/px150SwathHeights.xml').getroot()
fill_names = {f.get('name') for f in fills.iter('fillType')}
assert fill_names == {h.get('fillTypeName') for h in heights.iter('densityMapHeightType')}
for f in fills.iter('fillType'):
    for attr in ('diffuse', 'distance'):
        assert (root / f.find('textures').get(attr)).is_file(), f.find('textures').get(attr)
print('PASS test_grain_header_crops')
