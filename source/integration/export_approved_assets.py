import bpy,pathlib,sys
r=pathlib.Path.cwd();p=r/'source/integration'
bpy.ops.wm.open_mainfile(filepath=str(r/'previews/hd50f_adapter_v1/px150xl_endcap_parallel_top_v1.blend'))
keep=[]
for o in list(bpy.data.objects):
 if o.name=='px150Mount' or o.name.startswith(('mount','hitch','PropaineX rear brand','PX150XL left model','PX150XL right model')):keep.append(o)
 else:bpy.data.objects.remove(o,do_unlink=True)
for o in list(bpy.data.objects):
 if o.type=='FONT':
  bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.ops.object.convert(target='MESH')
 if o.type=='MESH':
  while len(o.data.uv_layers)<2:o.data.uv_layers.new(name='UV'+str(len(o.data.uv_layers)))
  o['i3D_collision']=False
bpy.ops.wm.save_as_mainfile(filepath=str(p/'approved_mount_and_labels.blend'))
sys.path.insert(0,bpy.utils.user_resource('SCRIPTS',path='addons'))
import io_export_i3d.dcc as dp
from io_export_i3d import i3d_export
from io_export_i3d.dcc import dccBlender as d
d.isNodeVisible=lambda n:bpy.data.objects[n].visible_get();dp.isNodeVisible=d.isNodeVisible
d.UISetAttrBool('i3D_exportUseSoftwareFileName',False);d.UISetAttrBool('i3D_binaryFiles',False);d.UISetAttrString('i3D_exportFileLocation',str(p/'approved_mount_and_labels.i3d'));i3d_export.I3DExportAll()
