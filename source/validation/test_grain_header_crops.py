"""Run with lupa available on PYTHONPATH; no game installation required."""
from pathlib import Path
import xml.etree.ElementTree as ET
from lupa.lua51 import LuaRuntime

root = Path(__file__).resolve().parents[2]


def run(map_full, model):
    lua = LuaRuntime()
    lua.globals().mapFull = map_full
    lua.globals().model = model
    # Mock map: fruits 1 WHEAT, 2 RYE, 3 TRITICALE, 4 SORGHUM (no ground type), 5 MAIZE (not a grain header crop),
    # 6 SPELT (grain heap only), 7 CANOLA. Swath fills 1001 WHEAT_CUT, 1007 CANOLA_CUT; own swaths 2002 rye, 2003 triticale.
    lua.execute("""
    Mower = {}
    Utils = {appendedFunction = function(a, b) return function(...) a(...); b(...) end end}
    FruitTypeManager = {loadMapData = function(self) end}
    FillTypeManager = {loadModFillTypes = function(self) end}
    logLines = {}
    Logging = {info = function(f, ...) logLines[#logLines+1] = string.format(f, ...) end,
               warning = function(f, ...) error('unexpected warning: ' .. string.format(f, ...)) end}
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
    -- grain L/m2 as in the game files; straw (windrow) 3.68 for all
    grainL = {[1]=0.89, [2]=0.96, [3]=0.95, [4]=0.82, [5]=1.2, [6]=0.8, [7]=0.6}
    STRAW = 3.68
    local linked = {[1]=1001, [7]=1007} -- crop file windrow cutFillType
    local swathToFruit = {[1001]=1, [1007]=7}
    descs = {}
    for i, n in ipairs(names) do
        descs[i] = {index=i, name=n, minHarvestingGrowthState=5, maxHarvestingGrowthState=6, literPerSqm=grainL[i],
                    windrowCutFillType = linked[i] and {index=linked[i]} or nil}
    end
    -- Two guesses at the game's hidden code; the fix must give the same grain under both.
    -- 'straw': every crop is laid at straw volume; a linked swath converts back to grain x1.25 at pickup.
    -- 'grain': a linked crop is laid as its grain amount, x1.25 at pickup; unlinked crops at straw volume.
    -- In both, an unlinked swath is picked up litre for litre (what the user saw: ~4x grain).
    function laidPerArea(f)
        if model == 'grain' and linked[f] then return grainL[f] end
        return STRAW
    end
    function grainPerSwathLiter(s)
        local f = swathToFruit[s]
        if f == nil then return 1 end
        if model == 'grain' then return 1.25 end
        return grainL[f] / STRAW * 1.25
    end
    g_fruitTypeManager = {
        getFruitTypeAreaLiters = function(self, f, area, windrow) assert(windrow == true); return area * laidPerArea(f) end,
        getCutWindrowHarvestFillLevel = function(self, s, liters) return liters * grainPerSwathLiter(s) end,
        getFruitTypeByName = function(self, n) for i, v in ipairs(names) do if v == n then return descs[i] end end end,
        getConverterDataByName = function(self, name)
            assert(name == 'COMBINE_MOWER')
            return {[1] = {fillTypeIndex=1001, conversionFactor=1}, [7] = {fillTypeIndex=1007, conversionFactor=1}}
        end,
        getFruitTypeIndicesByCategoryNames = function(self, names) assert(names == 'GRAINHEADER'); return {1, 2, 3, 4, 6, 7} end,
        getFillTypeIndexByFruitTypeIndex = function(self, i) return 100 + i end,
        getFruitTypeByIndex = function(self, i) return descs[i] end
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
        assert(pickupTable[1007].conversionFactor == 1 and pickupTable[1001].conversionFactor == 1) -- map records untouched
    else
        assert(c[2].fillTypeIndex == 2002 and c[3].fillTypeIndex == 2003)
        assert(pickupTable[2002].targetFillTypeIndex == 102 and pickupTable[2003].targetFillTypeIndex == 103)
    end
    -- Grain from one m2 cut and picked up, against the swath crop it is matched to (same bonus, own yield).
    local function grainFrom(fruit)
        local laid = laidPerArea(fruit) * c[fruit].conversionFactor
        local s = c[fruit].fillTypeIndex
        return laid * grainPerSwathLiter(s) * pickupTable[s].conversionFactor
    end
    local wheatGrain = laidPerArea(1) * grainPerSwathLiter(1001) * pickupTable[1001].conversionFactor
    local canolaGrain = laidPerArea(7) * grainPerSwathLiter(1007) * pickupTable[1007].conversionFactor
    assert(math.abs(wheatGrain - 0.89 * 1.25) < 1e-9) -- the reference itself: wheat yield with the 25%
    local refRye = mapFull and canolaGrain / 0.6 or wheatGrain / 0.89   -- rye -> canola swath when the map is full
    local refTriticale = wheatGrain / 0.89
    assert(math.abs(grainFrom(2) - refRye * 0.96) < 1e-9, grainFrom(2))
    assert(math.abs(grainFrom(3) - refTriticale * 0.95) < 1e-9, grainFrom(3))
    if not mapFull then
        assert(math.abs(grainFrom(2) - 0.96 * 1.25) < 1e-9)      -- rye: own yield +25%, like wheat
        assert(math.abs(grainFrom(2) / (STRAW * 1) - 0.326) < 0.001) -- was STRAW L of grain per m2: about 3.1x less now
        -- Swath laid on the ground is now the wheat swath's size per m2, scaled by yield.
        assert(math.abs(laidPerArea(2) * c[2].conversionFactor - laidPerArea(1) * 0.96 / 0.89) < 1e-9)
    end
    assert(#logLines >= 2)
    assert(c[4] == nil) -- no ground type for this grain on the map
    assert(c[5] == nil)
    assert(c[6].fillTypeIndex == 106 and pickupTable[106].targetFillTypeIndex == 106) -- other crops: grain strip
    assert(c[6].conversionFactor == 1 and pickupTable[106].conversionFactor == 1) -- grain strips unchanged by this fix
    assert(#ai == 3)

    -- A second header reuses the same decisions.
    local second = newHeader()
    vehicleType.listener.onLoad(second)
    assert(second.spec_mower.fruitTypeConverters[2].fillTypeIndex == c[2].fillTypeIndex)
    """)


for model in ('straw', 'grain'):
    run(False, model)
    run(True, model)
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
