local function find(n,name) if getName(n)==name then return n end for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name) if r then return r end end end
if pxCompletedModel then delete(pxCompletedModel) end
pxCompletedModel=loadI3DFile('C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/FS25_PX150XL/source/integration/final_unoptimized.i3d',false,false,false);link(getRootNode(),pxCompletedModel)
local component=find(pxCompletedModel,'headerHD50F_main_component1');clearSelection();addSelection(component)
print('FINAL_ASSEMBLED '..tostring(getShapeIsSkinned(find(component,'headerHD50F_vis'))))
setTranslation(pxFinalCam,9,3.8,-15);setDirection(pxFinalCam,9,3,-15,0,1,0);setCamera(pxFinalCam)
