import bpy,pathlib,json
p=pathlib.Path.cwd()/'previews/hd50f_adapter_v1';bpy.ops.wm.open_mainfile(filepath=str(p/'px150xl_dark_branding_v2.blend'))
o=bpy.data.objects['headerHD50F_vis'];vs=[v.co for v in o.data.vertices if abs(v.co.x)>7.7]
print('END BOUNDS',[(i,min(v[i] for v in vs),max(v[i] for v in vs)) for i in range(3)])
for name in ['grainExtension','headerHD50F_vis']:
 o=bpy.data.objects.get(name)
 if o:
  print(name,[(i,min(v.co[i] for v in o.data.vertices),max(v.co[i] for v in o.data.vertices)) for i in range(3)])
