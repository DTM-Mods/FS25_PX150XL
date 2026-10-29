import bpy,json
from pathlib import Path
r=Path.cwd();p=r/'previews/reel_discs_color_v1';bpy.ops.wm.open_mainfile(filepath=str(r/'previews/header_front_angle_v1/px150xl_full_front_angle_v1.blend'))
o=bpy.data.objects['headerHD50F_vis'];m=o.data;parent=list(range(len(m.vertices)))
def find(x):
 while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
 return x
for e in m.edges:
 a,b=map(find,e.vertices);parent[b]=a
g={}
for v in m.vertices:g.setdefault(find(v.index),[]).append(v.index)
rows=[]
for ids in g.values():
 co=[o.matrix_world@m.vertices[i].co for i in ids];lo=[min(v[k] for v in co) for k in range(3)];hi=[max(v[k] for v in co) for k in range(3)]
 if (lo[0]>7.3 or hi[0]<-7.3) and hi[1]-lo[1]>.7 and hi[2]-lo[2]>.7:rows.append({'verts':len(ids),'min':lo,'max':hi,'ids':ids})
(p/'disc_islands.json').write_text(json.dumps(rows));print([(x['verts'],x['min'],x['max']) for x in rows])
