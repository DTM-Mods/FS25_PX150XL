import bpy,pathlib
p=pathlib.Path.cwd()/'previews/hd50f_adapter_v1';bpy.ops.wm.open_mainfile(filepath=str(p/'px150xl_endcap_labels_v2.blend'))
for n in ['PX150XL left model','PX150XL right model']:
 o=bpy.data.objects[n];print(n,tuple(o.location),tuple(o.dimensions),tuple(o.rotation_euler));print('verts',len(o.data.vertices))
