import bpy,pathlib
p=pathlib.Path.cwd()/'previews/hd50f_adapter_v1'
bpy.ops.wm.open_mainfile(filepath=str(p/'px150xl_dark_branding_v1.blend'))
bpy.data.objects['PropaineX rear brand'].location.x=.65
bpy.data.objects['PropaineX rear brand'].location.z=1.23
bpy.data.objects['PX150XL left model'].location.y=1.55
bpy.data.objects['PX150XL right model'].location.y=1.55
bpy.context.scene.render.filepath=str(p/'px150xl_dark_branding_v2.png')
bpy.ops.wm.save_as_mainfile(filepath=str(p/'px150xl_dark_branding_v2.blend'));bpy.ops.render.render(write_still=True)
