import bpy,pathlib
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
p=pathlib.Path.cwd()/'previews/hd50f_adapter_v1'
bpy.ops.wm.obj_import(filepath=str(p/'header_export.obj'),use_split_objects=True,use_split_groups=True)
print('GROUPS',[(o.name,len(o.data.polygons)) for o in bpy.context.scene.objects if o.type=='MESH'])
bpy.ops.wm.save_as_mainfile(filepath=str(p/'grouped_source.blend'))
