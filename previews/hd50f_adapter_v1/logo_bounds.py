import bpy,pathlib
p=pathlib.Path.cwd()/'previews/hd50f_adapter_v1';bpy.ops.wm.open_mainfile(filepath=str(p/'grouped_source.blend'))
for o in bpy.data.objects:
 if o.name.startswith('logos'):
  vs=[(o.matrix_world@v.co)*.01 for v in o.data.vertices];print('LOGO',o.name,[(i,round(min(v[i] for v in vs),3),round(max(v[i] for v in vs),3)) for i in range(3)])
