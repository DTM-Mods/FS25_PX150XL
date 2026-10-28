for _,r in ipairs(pxPoseRestore or {}) do setTranslation(r.node,r.x,r.y,r.z);setRotation(r.node,r.rx,r.ry,r.rz) end
local function find(n,name) if getName(n)==name then return n end for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name) if r then return r end end end
local ref=find(getRootNode(),'PX_REFERENCE_MESH');if ref then setName(ref,'headerHD50F_vis');setVisibility(getParent(ref),false) end
local final=find(pxCompletedModel,'PX_FINAL_MESH');if final then setName(final,'headerHD50F_vis') end
clearSelection();setTranslation(pxFinalCam,0,2.3,-12);setDirection(pxFinalCam,0,1.5,-12,0,1,0);setCamera(pxFinalCam);print('FINAL_NORMAL_POSE_RESTORED')
