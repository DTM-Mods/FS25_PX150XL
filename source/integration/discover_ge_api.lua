local names={}
for k,v in pairs(_G) do if type(v)=='function' and (k:lower():find('export') or k:lower():find('save') or k:lower():find('shape') or k:lower():find('select')) then names[#names+1]=k end end
table.sort(names);for _,n in ipairs(names) do print('INTEGRATE_API '..n) end
local function find(n,name) if getName(n)==name then return n end for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name) if r then return r end end end
local s=find(getRootNode(),'headerHD50F_vis');print('INTEGRATE_SKIN',getShapeIsSkinned(s))
for i=0,getNumOfShapeBones(s)-1 do local b=getShapeBone(s,i);print('INTEGRATE_BONE',i,getName(b),getTranslation(b)) end
