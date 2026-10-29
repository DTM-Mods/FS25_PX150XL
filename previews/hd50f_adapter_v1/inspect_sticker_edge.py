import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=str(Path.cwd()/'previews/hd50f_adapter_v1/px150xl_endcap_parallel_top_v1.blend'))
o=bpy.data.objects['headerHD50F_vis'];o.data.calc_loop_triangles();rows=[]
for t in o.data.loop_triangles:
 vs=[o.data.vertices[i].co for i in t.vertices];c=sum(vs,vs[0]*0)/3
 if c.x>7.89 and .70<c.z-.5*c.y<.87 and -.2<c.y<1.2:
  rows.append({'center':list(c),'normal':list(t.normal),'verts':[list(v) for v in vs]})
Path('previews/endcap_sticker_v4/edge_inspection.json').write_text(json.dumps(rows,indent=2));print('COUNT',len(rows));print('NORMALS',[(round(r['center'][1],3),round(r['center'][2]-.5*r['center'][1],3),[round(x,3) for x in r['normal']]) for r in rows])
