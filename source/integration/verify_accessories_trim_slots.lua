-- Read the compiled scratch model; exercise only the native color target slot.
local base = 'C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/FS25_PX150XL/source/integration/accessories_trim_build/'
local output = {write=function(_, text) print('PX150_SLOT_CHECK ' .. text) end, close=function() end}
local model
local ok, err = pcall(function()
    model = loadI3DFile(base .. 'FS25_PX150XL/px150xlWindrower.i3d', false, false, false)
    assert(model ~= 0, 'model failed to load')
    link(getRootNode(), model)
    local protected, targets = {}, {}
    local function visit(node)
        if getHasClassId(node, ClassIds.SHAPE) then
            for i = 0, getNumOfMaterials(node)-1 do
                local mat = getMaterial(node, i)
                local r,g,b = getMaterialCustomParameter(mat, 'colorScale')
                local entry = {node=node, index=i, material=mat, r=r, g=g, b=b}
                if getMaterialSlotName(node, i) == 'px150_endCapSticker' then
                    local name=getName(node)
                    assert(string.find(name, 'PX150XL_endCapSticker_')==1 or string.find(name,'mount')==1 or string.find(name,'hitch')==1 or name=='PX150XL_square_steel_crossbar')
                    table.insert(targets, entry)
                    output:write('TARGET ' .. getName(node) .. ' slot=' .. getMaterialSlotName(node, i) .. '\n')
                else
                    table.insert(protected, entry)
                end
            end
        end
        for i=0,getNumOfChildren(node)-1 do visit(getChildAt(node,i)) end
    end
    visit(model)
    assert(#targets == 23, 'expected 23 sticker and attacher targets; got ' .. #targets)
    for _, color in ipairs({{1,0,0},{0,0,1},{0.8,0.16,0.018}}) do
        for _, t in ipairs(targets) do
            setShaderParameter(t.node, 'colorScale', color[1],color[2],color[3],1,false,t.index)
        end
        for _, t in ipairs(targets) do
            local r,g,b = getMaterialCustomParameter(getMaterial(t.node,t.index), 'colorScale')
            assert(math.abs(r-color[1])<0.00001 and math.abs(g-color[2])<0.00001 and math.abs(b-color[3])<0.00001)
        end
        for _, t in ipairs(protected) do
            assert(getMaterial(t.node,t.index)==t.material, 'protected material changed')
            local r,g,b = getMaterialCustomParameter(t.material, 'colorScale')
            assert(r==t.r and g==t.g and b==t.b, 'protected color changed on '..getName(t.node))
        end
    end
    output:write('PASS: exactly 23 sticker and attacher slots; red/blue/orange changes left all ' .. #protected .. ' other material slots unchanged.\n')
end)
if not ok then output:write('FAIL: ' .. tostring(err) .. '\n') end
output:close()
if model and model ~= 0 then delete(model) end
editorExit(0)
