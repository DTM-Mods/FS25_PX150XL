"""Run with lupa available on PYTHONPATH; no game installation required."""
from pathlib import Path
import xml.etree.ElementTree as ET
from lupa import LuaRuntime

root = Path(__file__).resolve().parents[2]
lua = LuaRuntime()
lua.execute("""
Mower = {}
SpecializationUtil = {
    hasSpecialization = function(wanted, specs)
        for _, spec in ipairs(specs) do
            if spec == wanted then return true end
        end
        return false
    end,
    registerEventListener = function(vehicleType, event, listener)
        assert(event == 'onPostLoad')
        vehicleType.listener = listener
    end
}
""")
lua.execute((root / 'scripts/PX150YieldBonus.lua').read_text())
lua.execute("""
assert(PX150YieldBonus.prerequisitesPresent({Mower}))
assert(not PX150YieldBonus.prerequisitesPresent({}))
local vehicleType = {}
PX150YieldBonus.registerEventListeners(vehicleType)
assert(vehicleType.listener == PX150YieldBonus)

-- 1 WHEAT, 2 ALFALFA, 3 CLOVER, 99 a map crop with a non-unit factor
local names = {[1]='WHEAT', [2]='ALFALFA', [3]='CLOVER', [99]='SUMMERBARLEY'}
g_fruitTypeManager = {getFruitTypeByIndex = function(self, i)
    if names[i] then return {index=i, name=names[i]} end
end}
local shared = {
    [1] = {conversionFactor=1, fillTypeIndex=101},
    [2] = {conversionFactor=0.75, fillTypeIndex=102},
    [3] = {conversionFactor=1, fillTypeIndex=103},
    [99] = {conversionFactor=2.5, fillTypeIndex=199},
    [500] = {conversionFactor=1, fillTypeIndex=500} -- unknown fruit index
}
local function newHeader()
    local c = {}
    for k, v in pairs(shared) do c[k] = v end
    return {spec_mower={fruitTypeConverters=c}}
end
local first, second = newHeader(), newHeader()
vehicleType.listener.onPostLoad(first)
vehicleType.listener.onPostLoad(second)
local boosted = {[2]=true, [3]=true}
for input, original in pairs(shared) do
    local a = first.spec_mower.fruitTypeConverters[input]
    local b = second.spec_mower.fruitTypeConverters[input]
    assert(a ~= nil and b ~= nil)
    assert(a.fillTypeIndex == original.fillTypeIndex)
    if boosted[input] then
        assert(a ~= original and a ~= b)
        assert(math.abs(a.conversionFactor / original.conversionFactor - 1.15) < 1e-12)
        assert(a.conversionFactor == b.conversionFactor) -- multiple headers do not stack
    else
        assert(a == original and a.conversionFactor == original.conversionFactor)
    end
end
assert(shared[1].conversionFactor == 1)
assert(shared[2].conversionFactor == 0.75)
assert(shared[3].conversionFactor == 1)
assert(shared[99].conversionFactor == 2.5)
assert(math.abs(10000 * first.spec_mower.fruitTypeConverters[3].conversionFactor - 11500) < 1e-8)
assert(first.spec_mower.fruitTypeConverters[1].conversionFactor == 1)
""")
desc = ET.parse(root / 'modDesc.xml').getroot()
vehicle = ET.parse(root / 'px150xlWindrower.xml').getroot()
assert vehicle.get('type') == desc.find('vehicleTypes/type').get('name')
assert desc.find('vehicleTypes/type').get('parent') == 'mower'
assert desc.find('specializations/specialization').get('filename') == 'scripts/PX150YieldBonus.lua'
joint = vehicle.find('attachable/inputAttacherJoints/inputAttacherJoint')
assert joint.find('distanceToGround').get('lower') == '0.30'
assert joint.get('lowerRotationOffset') == '10'
print('PASS: 15% yield on alfalfa and clover only, other crops unchanged, map crop factors, independent headers, shared converters unchanged, XML wiring and height retained')
