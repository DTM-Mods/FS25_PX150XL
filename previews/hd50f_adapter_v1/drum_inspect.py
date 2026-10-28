import bpy,bmesh,pathlib,json
p=pathlib.Path.cwd()/'previews/hd50f_adapter_v1'
bpy.ops.wm.open_mainfile(filepath=str(p/'adapter_removed_mockup_v2.blend'))
o=bpy.data.objects['header_export'];bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
seen=set();rows=[]
for v in bm.verts:
 if v in seen:continue
 todo=[v];seen.add(v);part=[]
 while todo:
  a=todo.pop();part.append(a)
  for e in a.link_edges:
   b=e.other_vert(a)
   if b not in seen:seen.add(b);todo.append(b)
 lo=[min(v.co[i] for v in part) for i in range(3)];hi=[max(v.co[i] for v in part) for i in range(3)]
 if lo[0]>-1.9 and hi[0]<1.9 and hi[1]>.5 and lo[2]<.9:
  rows.append([len(part),[round(x,3) for x in lo],[round(x,3) for x in hi]])
(p/'drum_components.json').write_text(json.dumps(rows))
