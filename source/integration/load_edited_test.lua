local function find(n,name) if getName(n)==name then return n end for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name) if r then return r end end end
local root=getRootNode();local old=find(root,'headerHD50F_main_component1');setVisibility(old,false)
pxCompletedModel=loadI3DFile('C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/FS25_PX150XL/source/integration/animated_edited_test.i3d',false,false,false)
link(root,pxCompletedModel)
local s=find(pxCompletedModel,'headerHD50F_vis');print('REBUILT_MESH_LOADED '..tostring(s));local n,positions=getShapeVertexPositions(s);print('REBUILT_VERTICES '..n);local sk,single=getShapeIsSkinned(s);print('REBUILT_SKIN '..tostring(sk)..' '..tostring(single))
pxFinalCam=createCamera('PX150XL_final_view',math.rad(40),.1,500);link(root,pxFinalCam);setTranslation(pxFinalCam,11,4,-17);setDirection(pxFinalCam,11,3.2,-17,0,1,0);setCamera(pxFinalCam)
