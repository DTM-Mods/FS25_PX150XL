local function find(n,name) if getName(n)==name then return n end for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name) if r then return r end end end
clearSelection();addSelection(find(pxCompletedModel,'headerHD50F_main_component1'));print('FINAL_SELECTED_COMPLETE_COMPONENT')
