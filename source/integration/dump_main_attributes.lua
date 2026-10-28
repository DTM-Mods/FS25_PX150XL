local function find(n,name) if getName(n)==name then return n end for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name) if r then return r end end end
local s=find(getRootNode(),'headerHD50F_vis')
local cnt,p=getShapeVertexPositions(s);local n0,uv0=getShapeVertexTexCoords(s,0);local n1,uv1=getShapeVertexTexCoords(s,1);local nc,colors=getShapeVertexColors(s)
print(string.format('MAIN_BUFFERS positions=%s uv0=%s uv1=%s colors=%s',tostring(cnt),tostring(n0),tostring(n1),tostring(nc)))
local f=io.open('C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/FS25_PX150XL/source/integration/main_vertex_attributes.json','w')
f:write('{"count":'..cnt)
for _,item in ipairs({{'positions',p},{'uv0',uv0},{'uv1',uv1},{'colors',colors}}) do
 f:write(',"'..item[1]..'":[')
 if item[2] then for k,v in ipairs(item[2]) do if k>1 then f:write(',') end f:write(string.format('%.8g',v)) end end
 f:write(']')
end
f:write('}');f:close();print('MAIN_ATTRIBUTES_WRITTEN')
