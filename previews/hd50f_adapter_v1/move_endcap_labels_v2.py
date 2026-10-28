import bpy,pathlib
from mathutils import Vector,Matrix
p=pathlib.Path.cwd()/'previews/hd50f_adapter_v1';bpy.ops.wm.open_mainfile(filepath=str(p/'px150xl_dark_branding_v2.blend'))
body=bpy.data.objects['headerHD50F_vis']
for side,name in [(1,'PX150XL left model'),(-1,'PX150XL right model')]:
 o=bpy.data.objects[name];hit,loc,normal,index=body.ray_cast(Vector((side*9,.60,.66)),Vector((-side,0,0)))
 assert hit,'End-cap surface not found'
 o.location=loc+normal*.005
 up=Vector((0,0,1));right=up.cross(normal).normalized();up=normal.cross(right).normalized()
 o.rotation_euler=Matrix((right,up,normal)).transposed().to_euler();o.data.size=.095;o.scale=(1,1,1)
 bpy.context.view_layer.objects.active=o
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.ops.object.convert(target='MESH')
 o=bpy.context.object
 for v in o.data.vertices:
  co=o.matrix_world@v.co
  hit2,pt,n,idx=body.ray_cast(Vector((side*9,co.y,co.z)),Vector((-side,0,0)))
  if hit2:v.co=o.matrix_world.inverted()@(pt+n*.006)
 print('END LABEL',side,tuple(o.location),tuple(normal))
scene=bpy.context.scene;scene.cycles.samples=24;scene.render.resolution_x=1400;scene.render.resolution_y=950
cam=scene.camera;cam.data.ortho_scale=3.4
bpy.ops.wm.save_as_mainfile(filepath=str(p/'px150xl_endcap_labels_v2.blend'))
for side,label in [(1,'left'),(-1,'right')]:
 cam.location=(side*11.5,3.6,2.0);target=Vector((side*7.65,.65,.8));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(p/f'px150xl_{label}_endcap_v2.png');bpy.ops.render.render(write_still=True)
(p/'ENDCAP_LABEL_NOTES.md').write_text('2026-10-28 (Codex): Moved existing two PX150XL preview text objects from inner rear panels onto actual left/right outer end-cap surfaces using side raycasts at Blender y=1.0,z=0.88. Text oriented to surface normals with 5 mm offset. PropaineX beam brand unchanged. Scratch scene px150xl_endcap_labels_v2.blend; left/right end close-up renders px150xl_left_endcap_v2.png and px150xl_right_endcap_v2.png. Runtime source unchanged; verified Blender render only.\n')
