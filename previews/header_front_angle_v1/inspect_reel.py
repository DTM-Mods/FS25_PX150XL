import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path.cwd();bpy.ops.wm.open_mainfile(filepath=str(r/'previews/header_front_angle_v1/px150xl_full_front_angle_v1.blend'))
rows=[]
for o in bpy.data.objects:
 if o.type=='MESH':
  pts=[o.matrix_world@Vector(v) for v in o.bound_box];rows.append({'name':o.name,'vertices':len(o.data.vertices),'min':[min(v[k] for v in pts) for k in range(3)],'max':[max(v[k] for v in pts) for k in range(3)]})
p=r/'previews/reel_discs_color_v1';p.mkdir(exist_ok=True);(p/'mesh_objects.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=1))
