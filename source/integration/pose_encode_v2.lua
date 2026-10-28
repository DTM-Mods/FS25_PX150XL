local function find(n,name) if getName(n)==name then return n end for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name) if r then return r end end end
local s=find(getRootNode(),'headerHD50F_vis')
pxRigOriginalBones={};local bones=pxRigOriginalBones
for i=0,getNumOfShapeBones(s)-1 do local b=getShapeBone(s,i);local x,y,z=getWorldTranslation(b);bones[i+1]={b=b,x=x,y=y,z=z,index=i};print(string.format('RIG_BONE %d %s %.9f %.9f %.9f',i,getName(b),x,y,z)) end
for _,r in ipairs(bones) do if r.index>0 then setWorldTranslation(r.b,r.x+20*r.index,r.y,r.z) end end
clearSelection();addSelection(find(getRootNode(),'headerHD50F_main_component1'))
print('RIG_POSE_APPLIED')

