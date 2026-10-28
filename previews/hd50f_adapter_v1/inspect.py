import bpy, pathlib, json
bpy.ops.wm.obj_import(filepath=str(pathlib.Path.cwd()/'previews/hd50f_adapter_v1/header_export.obj'))
rows=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  v=[o.matrix_world@x.co for x in o.data.vertices]
  rows.append([o.name,len(v),len(o.data.polygons),[round(min(x[i] for x in v),3) for i in range(3)],[round(max(x[i] for x in v),3) for i in range(3)]])
pathlib.Path('previews/hd50f_adapter_v1/mesh_inventory.json').write_text(json.dumps(rows,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(pathlib.Path.cwd()/'previews/hd50f_adapter_v1/header_edit.blend'))
