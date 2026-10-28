import bpy,bmesh,pathlib,json
p=pathlib.Path.cwd()/'previews/hd50f_adapter_v1'
bpy.ops.wm.open_mainfile(filepath=str(p/'textured_preview_v1.blend'))
o=bpy.data.objects['headerHD50F_vis'];bm=bmesh.new();bm.from_mesh(o.data);seen=set();rows=[]
for v in bm.verts:
 if v in seen:continue
 todo=[v];seen.add(v);part=[]
 while todo:
  a=todo.pop();part.append(a)
  for e in a.link_edges:
   b=e.other_vert(a)
   if b not in seen:seen.add(b);todo.append(b)
 lo=[min(v.co[i] for v in part) for i in range(3)];hi=[max(v.co[i] for v in part) for i in range(3)]
 if lo[0]>-1.1 and hi[0]<1.1 and lo[2]>.20 and hi[2]<1.05:
  rows.append([len(part),[round(x,4) for x in lo],[round(x,4) for x in hi]])
(p/'remaining_finger_components.json').write_text(json.dumps(rows))
