import bpy,pathlib
from mathutils import Vector
p=pathlib.Path.cwd()/'previews/hd50f_adapter_v1';bpy.ops.wm.open_mainfile(filepath=str(p/'px150xl_endcap_large_diagonal_v1.blend'));o=bpy.data.objects['headerHD50F_vis']
for y in [-.2,0,.2,.4,.6,.8,1.0]:
 hits=[]
 for j in range(20,141):
  z=j*.01;hit,pt,n,idx=o.ray_cast(Vector((9,y,z)),Vector((-1,0,0)))
  if hit and pt.x>7.85:hits.append(z)
 print('PROFILE',y,max(hits) if hits else None)
