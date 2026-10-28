import bpy,bmesh,json,pathlib
bpy.ops.wm.open_mainfile(filepath=str(pathlib.Path.cwd()/'previews/hd50f_adapter_v1/header_edit.blend'))
o=bpy.data.objects['header_export']; bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.01);bm.verts.ensure_lookup_table();seen=set();rows=[]
for v in bm.verts:
 if v in seen:continue
 todo=[v];seen.add(v);part=[]
 while todo:
  a=todo.pop();part.append(a)
  for e in a.link_edges:
   b=e.other_vert(a)
   if b not in seen:seen.add(b);todo.append(b)
 lo=[min(v.co[i] for v in part) for i in range(3)];hi=[max(v.co[i] for v in part) for i in range(3)]
 if lo[0]>-190 and hi[0]<190 and hi[1]>95 and hi[2]>30:rows.append([len(part),[round(x,2) for x in lo],[round(x,2) for x in hi]])
pathlib.Path('previews/hd50f_adapter_v1/components.json').write_text(json.dumps(rows))
