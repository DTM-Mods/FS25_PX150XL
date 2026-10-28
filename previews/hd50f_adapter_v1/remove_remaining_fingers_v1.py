import bpy,bmesh,pathlib
p=pathlib.Path.cwd()/'previews/hd50f_adapter_v1'
bpy.ops.wm.open_mainfile(filepath=str(p/'textured_preview_v1.blend'))
o=bpy.data.objects['headerHD50F_vis'];bm=bmesh.new();bm.from_mesh(o.data);seen=set();remove=[];parts=0
for v in bm.verts:
 if v in seen:continue
 todo=[v];seen.add(v);part=[]
 while todo:
  a=todo.pop();part.append(a)
  for e in a.link_edges:
   b=e.other_vert(a)
   if b not in seen:seen.add(b);todo.append(b)
 lo=[min(v.co[i] for v in part) for i in range(3)];hi=[max(v.co[i] for v in part) for i in range(3)]
 if len(part)==8 and lo[0]>-.70 and hi[0]<.70 and lo[1]>.40 and hi[1]<1.02 and lo[2]>.30 and hi[2]<1.0:
  remove.extend(part);parts+=1
assert parts==13, f'Unexpected finger count {parts}'
bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(o.data);bm.free();o.data.update()
scene=bpy.context.scene;scene.render.filepath=str(p/'textured_rear_no_fingers_v1.png')
bpy.ops.wm.save_as_mainfile(filepath=str(p/'textured_preview_no_fingers_v1.blend'));bpy.ops.render.render(write_still=True)
(p/'FINGER_CLEANUP_NOTES.md').write_text('2026-10-28 (Codex): Physically removed exactly 13 disconnected drum fingers, 104 welded vertices, from textured_preview_v1.blend. Same camera, lighting, textures and render settings preserved. Output textured_rear_no_fingers_v1.png; scratch scene textured_preview_no_fingers_v1.blend. Verified Blender render, UNTESTED in game. Production source unchanged.\n')
print('Removed',parts,'fingers;',len(remove),'vertices')
