import bpy,bmesh,pathlib
p=pathlib.Path.cwd()/'previews/hd50f_adapter_v1'
bpy.ops.wm.open_mainfile(filepath=str(p/'adapter_removed_mockup_v2.blend'))
o=bpy.data.objects['header_export'];scene=bpy.context.scene
scene.render.filepath=str(p/'feed_drum_before_v1.png');bpy.ops.render.render(write_still=True)
bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
seen=set();remove=[];parts=0
for v in bm.verts:
 if v in seen:continue
 todo=[v];seen.add(v);part=[]
 while todo:
  a=todo.pop();part.append(a)
  for e in a.link_edges:
   b=e.other_vert(a)
   if b not in seen:seen.add(b);todo.append(b)
 lo=[min(v.co[i] for v in part) for i in range(3)];hi=[max(v.co[i] for v in part) for i in range(3)]
 if lo[0]>-1.01 and hi[0]<1.01 and lo[1]>.55 and hi[1]<1.02 and lo[2]>.39 and hi[2]<.89:
  remove.extend(part);parts+=1
bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(o.data);bm.free();o.data.update()
scene.render.filepath=str(p/'feed_drum_after_v1.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(p/'adapter_and_feed_drum_removed_v1.blend'))
(p/'FEED_DRUM_NOTES.md').write_text(f'2026-10-28 (Codex): Preview-only physical removal of center feed drum and its fingers from adapter_removed_mockup_v2.blend. Deleted {parts} connected components ({len(remove)} welded vertices) within drum bounds x +/-1.01, rear y 0.55..1.02, height 0.39..0.89 m. Verified in Blender renders, not tested in game. Working source unchanged. Before: feed_drum_before_v1.png; after: feed_drum_after_v1.png. Previous previews preserved. User standing preference: before/after side by side, opened automatically in the existing left VS Code editor pane.\n')
print('Removed components:',parts,'vertices:',len(remove))
