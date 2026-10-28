local function find(n,name) if getName(n)==name then return n end for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name) if r then return r end end end
local original=find(getRootNode(),'headerHD50F_main_component1');local ref=find(original,'headerHD50F_vis');setName(ref,'PX_REFERENCE_MESH')
if pxCompletedModel then delete(pxCompletedModel) end
pxCompletedModel=loadI3DFile('C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/FS25_PX150XL/px150xlWindrower.i3d',false,false,false);link(getRootNode(),pxCompletedModel)
local result=find(pxCompletedModel,'headerHD50F_vis');setName(result,'PX_FINAL_MESH')
pxPoseRestore={}
for _,shape in ipairs({ref,result}) do
 print('FINAL_BINARY_BONES '..getNumOfShapeBones(shape))
 for b=0,getNumOfShapeBones(shape)-1 do
  local node=getShapeBone(shape,b);local n=getName(node)
  if n=='reel' or n=='reelPart' or n=='reelArm' or n=='knifesMove' then
   local x,y,z=getTranslation(node);local rx,ry,rz=getRotation(node);pxPoseRestore[#pxPoseRestore+1]={node=node,x=x,y=y,z=z,rx=rx,ry=ry,rz=rz}
   if n=='knifesMove' then setTranslation(node,x+.03,y,z) elseif n=='reelArm' then setRotation(node,rx-.15,ry,rz) else setRotation(node,rx+.35,ry,rz) end
  end
 end
end
setVisibility(original,true);clearSelection();addSelection(ref);addSelection(result);print('CONTROLLED_POSE_COMPARE_READY')
