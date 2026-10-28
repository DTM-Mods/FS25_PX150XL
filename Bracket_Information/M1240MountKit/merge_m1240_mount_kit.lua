-- M1240 mount kit: merge into the header open in GIANTS Editor (a COPY in a scratch folder), then File > Save.
-- Edit the four settings, then in the GE script console: source("<path>/merge_m1240_mount_kit.lua")
local KIT = "C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/Library/_M1240MountKit/m1240MountKit_px150.i3d"
local COMPONENT = "fd250_main_component1"   -- header's main component (the brackets become its last child)
local MAT_SHAPE = "fd250_vis"                -- shape whose materials are borrowed
local BLACK_SLOT, STEEL_SLOT = 2, 3          -- material slots on MAT_SHAPE: black frame metal, steel

local root = getRootNode()
local function find(node, name)
    if getName(node) == name then return node end
    for i = 0, getNumOfChildren(node) - 1 do local r = find(getChildAt(node, i), name) if r then return r end end
end
local old = find(root, "px150Mount") if old then delete(old) end
local comp = find(root, COMPONENT)
local node = loadI3DFile(KIT, false, false, false)
local mount = find(node, "px150Mount")
link(comp, mount)
delete(node)
local src = find(root, MAT_SHAPE)
local BLACK, STEEL = getMaterial(src, BLACK_SLOT), getMaterial(src, STEEL_SLOT)
for i = 0, getNumOfChildren(mount) - 1 do
    local c = getChildAt(mount, i)
    setMaterial(c, getName(c):find("^hitch") and STEEL or BLACK, 0)
end
print("[M1240 KIT] linked under " .. COMPONENT .. ", parts " .. getNumOfChildren(mount))
