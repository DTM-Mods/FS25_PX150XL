import bpy,bmesh,pathlib,json
from mathutils import Vector
root=pathlib.Path.cwd()/'previews/hd50f_adapter_v1'
bpy.ops.wm.open_mainfile(filepath=str(root/'header_edit.blend'))
o=bpy.data.objects['header_export']
for x in list(bpy.data.objects):
 if x!=o:bpy.data.objects.remove(x,do_unlink=True)
# GIANTS OBJ export uses centimeters; convert to meters.
for v in o.data.vertices:v.co*=.01
o.data.update();o.color=(.12,.33,.09,1)
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.5
scene.display.shading.color_type='OBJECT';scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH'
scene.display.shading.background_type='WORLD';scene.world.color=(.18,.18,.18)
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
camdata=bpy.data.cameras.new('Rear comparison');cam=bpy.data.objects.new('Rear comparison',camdata);scene.collection.objects.link(cam)
cam.location=(3.6,6.0,2.9);target=Vector((0,.85,.85));cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
camdata.type='ORTHO';camdata.ortho_scale=5.2;scene.camera=cam
scene.render.filepath=str(root/'before_geometry.png');bpy.ops.render.render(write_still=True)
# Preview-only physical cut of the rear central combine receiver.
# Header-wide top beam retained; rear central receiver below it removed.
bm=bmesh.new();bm.from_mesh(o.data)
remove=[v for v in bm.verts if abs(v.co.x)<1.30 and v.co.y>1.035 and .10<v.co.z<1.30]
count=len(remove);bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(o.data);bm.free();o.data.update()
scene.render.filepath=str(root/'after_geometry.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'adapter_removed_mockup.blend'))
(root/'MOCKUP_NOTES.md').write_text(f'''# HD50F physical-removal mock-up
2026-10-28 (Codex): GIANTS Editor supported OBJ export verified. Imported exported geometry into Blender. Rendered same-camera before/after clay views. Physically deleted {count} vertices of the rear central combine receiver from the scratch mesh. No visibility hiding used. The region is a preliminary cut: |x|<1.30 m, rear y>1.035 m, height 0.10..1.30 m (Blender coordinates). Header-wide upper beam retained. Review cut boundaries before production geometry work. Blender OBJ copy is static and does not preserve original skinning or materials; this is a geometry mock-up, not a game-ready replacement. Working header files unchanged. Original full-color rear screenshot: before.png.
''',encoding='utf-8')
print('PHYSICALLY REMOVED VERTICES',count)
