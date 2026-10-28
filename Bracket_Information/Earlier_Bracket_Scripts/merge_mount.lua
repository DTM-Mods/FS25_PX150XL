local root = getRootNode()
local function find(node, name)
    if getName(node) == name then return node end
    for i = 0, getNumOfChildren(node) - 1 do local r = find(getChildAt(node, i), name) if r then return r end end
end
local comp1 = find(root, "fd250_main_component1")
local node = loadI3DFile("C:/Users/groov/GE_work/px150/mount/px150Mount_v3.i3d", false, false, false)
local mount = find(node, "px150Mount")
link(comp1, mount)
delete(node)
local vis = find(root, "fd250_vis")
local hoseSrc = find(root, "electricIn01_attached")
local BLACK, STEEL, MAIN = getMaterial(vis, 2), getMaterial(vis, 3), getMaterial(vis, 10)
local HOSE = getMaterial(hoseSrc, 0)
local red = {mountStripeLeft=true, mountStripeRight=true, couplerCap0=true, couplerCap3=true}
local steel = {"Fitting", "Nipple", "couplerPlate", "Clamp", "couplerCap1", "couplerCap2"}
for i = 0, getNumOfChildren(mount) - 1 do
    local s = getChildAt(mount, i)
    local n = getName(s)
    local m = BLACK
    if n:find("^hose") then m = HOSE end
    for _, k in ipairs(steel) do if n:find(k) then m = STEEL end end
    if red[n] then m = MAIN end
    setMaterial(s, m, 0)
end
print("[MERGE] mount linked into comp1 as child " .. (getNumOfChildren(comp1) - 1) .. ", parts " .. getNumOfChildren(mount))
