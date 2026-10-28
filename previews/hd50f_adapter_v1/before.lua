local root=getRootNode()
function findHD(node,name)
 if getName(node)==name then return node end
 for i=0,getNumOfChildren(node)-1 do local r=findHD(getChildAt(node,i),name) if r then return r end end
end
local c=findHD(root,"canolaExtension") if c then setVisibility(c,false) end
hdCam=createCamera("hdPreviewCam",math.rad(40),0.1,500)
link(root,hdCam)
setTranslation(hdCam,3.8,2.6,-6.5)
setDirection(hdCam,3.8,1.8,-5.6,0,1,0)
setCamera(hdCam)
print("HD50F BEFORE PREVIEW READY")
