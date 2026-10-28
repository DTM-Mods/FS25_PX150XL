import bpy,pathlib,xml.etree.ElementTree as E,math
from mathutils import Vector
r=pathlib.Path.cwd();p=r/'previews/crossbar_v1'
bpy.ops.wm.open_mainfile(filepath=str(r/'previews/hd50f_adapter_v1/px150xl_endcap_parallel_top_v1.blend'))
# Match the actual rebuilt runtime main mesh, rather than the older approximate cut preview.
s=E.parse(r/'source/integration/final_unoptimized.i3d').find("./Shapes/IndexedTriangleSet[@shapeId='1001']")
assert s is not None
vertices=[tuple(map(float,x.get('p').split())) for x in s.findall('Vertices/v')];normals=[tuple(map(float,x.get('n').split())) for x in s.findall('Vertices/v')];uvs=[tuple(map(float,x.get('t0').split())) for x in s.findall('Vertices/v')]
verts=[(x,-z,y) for x,y,z in vertices];faces=[tuple(map(int,x.get('vi').split())) for x in s.findall('Triangles/t')]
me=bpy.data.meshes.new('Actual_runtime_edited_main');me.from_pydata(verts,[],faces);me.update();uv=me.uv_layers.new(name='UV0')
for loop in me.loops:uv.data[loop.index].uv=uvs[loop.vertex_index]
for f in me.polygons:f.use_smooth=True
me.normals_split_custom_set_from_vertices([(x,-z,y) for x,y,z in normals])
o=bpy.data.objects['headerHD50F_vis'];old=o.data;o.data=me;dark=bpy.data.materials.get('PX150XL dark graphite paint');assert dark is not None;me.materials.append(dark)
# Main runtime mask already contains the complete receiver/drum/support-gear removal.
scene=bpy.context.scene;scene.cycles.samples=40;scene.render.resolution_x=1600;scene.render.resolution_y=1050;scene.render.resolution_percentage=100
cam=scene.camera;cam.location=(3.8,6.5,3.0);cam.rotation_euler=(Vector((0,1.05,.85))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=5.6
scene.render.filepath=str(p/'before_crossbar.png');bpy.ops.render.render(write_still=True)
# 160 mm square cross tube, spanning brace centers; overlaps posts at each end.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,1.24,1.24));bar=bpy.context.object;bar.name='PX150XL_square_steel_crossbar';bar.dimensions=(2.548,.16,.16);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
black=bpy.data.materials.get('px150Mount_black_mat');bar.data.materials.append(black if black else dark)
bevel=bar.modifiers.new('Rounded steel tube edges','BEVEL');bevel.width=.003;bevel.segments=3
bar.modifiers.new('Steel face normals','WEIGHTED_NORMAL')
# Existing upper hitch is now backed by the tube; name sits just off its rear face.
brand=bpy.data.objects['PropaineX rear brand'];brand.location.y=1.323;brand.location.z=1.24
scene.render.filepath=str(p/'after_crossbar.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(p/'crossbar_mockup.blend'))
(p/'README.md').write_text('2026-10-28 (Codex): User resumed deferred repair and requested mock-up first. Actual runtime edited main rebuilt from supported exported XML geometry for accurate missing-beam depiction. Added one 160x160 mm square steel tube across brace centers x +/-1.274 m (length2.548m), center Blender(0,1.24,1.24), 3mm bevel. Connects posts and backs silver upper hitch. Existing PropaineX name moved flush to rear tube face at y1.323,z1.24; opaque tube blocks reverse-side floating lettering. Same camera/light before-after. Preview only: runtime geometry, joints, store image and testing ZIP unchanged. Source mass2950kg remains.\n',encoding='utf-8')
print('CROSSBAR MOCKUP RENDERED')
