import bpy,pathlib,sys
r=pathlib.Path.cwd();p=r/'source/integration'
bpy.ops.wm.open_mainfile(filepath=str(r/'previews/crossbar_v1/crossbar_mockup.blend'))
for o in list(bpy.data.objects):
 if o.name!='PX150XL_square_steel_crossbar':bpy.data.objects.remove(o,do_unlink=True)
o=bpy.data.objects['PX150XL_square_steel_crossbar']
while len(o.data.uv_layers)<2:o.data.uv_layers.new(name='UV'+str(len(o.data.uv_layers)))
o['i3D_collision']=False
sys.path.insert(0,bpy.utils.user_resource('SCRIPTS',path='addons'))
import io_export_i3d.dcc as dp
from io_export_i3d import i3d_export
from io_export_i3d.dcc import dccBlender as d
d.isNodeVisible=lambda n:bpy.data.objects[n].visible_get();dp.isNodeVisible=d.isNodeVisible
d.UISetAttrBool('i3D_exportUseSoftwareFileName',False);d.UISetAttrBool('i3D_binaryFiles',False);d.UISetAttrString('i3D_exportFileLocation',str(p/'approved_crossbar.i3d'));i3d_export.I3DExportAll()
