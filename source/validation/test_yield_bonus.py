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

local shared = {
    [1] = {conversionFactor=1, fillTypeIndex=101},
    [2] = {conversionFactor=0.75, fillTypeIndex=102},
    [99] = {conversionFactor=2.5, fillTypeIndex=199}
}
local function newHeader()
    return {spec_mower={fruitTypeConverters={
        [1]=shared[1], [2]=shared[2], [99]=shared[99]
    }}}
end
local first, second = newHeader(), newHeader()
vehicleType.listener.onPostLoad(first)
vehicleType.listener.onPostLoad(second)
for input, original in pairs(shared) do
    local a = first.spec_mower.fruitTypeConverters[input]
    local b = second.spec_mower.fruitTypeConverters[input]
    assert(a ~= original and a ~= b)
    assert(a.fillTypeIndex == original.fillTypeIndex)
    assert(math.abs(a.conversionFactor / original.conversionFactor - 1.10) < 1e-12)
    assert(a.conversionFactor == b.conversionFactor) -- multiple headers do not stack
end
assert(shared[1].conversionFactor == 1)
assert(shared[2].conversionFactor == 0.75)
assert(shared[99].conversionFactor == 2.5)
assert(math.abs(10000 * first.spec_mower.fruitTypeConverters[1].conversionFactor - 11000) < 1e-8)
""")
desc = ET.parse(root / 'modDesc.xml').getroot()
vehicle = ET.parse(root / 'px150xlWindrower.xml').getroot()
assert vehicle.get('type') == desc.find('vehicleTypes/type').get('name')
assert desc.find('vehicleTypes/type').get('parent') == 'mower'
assert desc.find('specializations/specialization').get('filename') == 'scripts/PX150YieldBonus.lua'
joint = vehicle.find('attachable/inputAttacherJoints/inputAttacherJoint')
assert joint.find('distanceToGround').get('lower') == '0.30'
assert joint.get('lowerRotationOffset') == '10'
print('PASS: 10% yield, map crop factors, independent headers, shared converters unchanged, XML wiring and height retained')
