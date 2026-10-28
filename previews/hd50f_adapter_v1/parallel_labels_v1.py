import bpy,pathlib,math
from mathutils import Vector,Matrix
p=pathlib.Path.cwd()/'previews/hd50f_adapter_v1';bpy.ops.wm.open_mainfile(filepath=str(p/'px150xl_endcap_labels_v2.blend'))
body=bpy.data.objects['headerHD50F_vis'];mat=bpy.data.materials['PropaineX lettering'];font=bpy.data.fonts.load('C:/Windows/Fonts/arialbd.ttf')
for side,name in [(1,'PX150XL left model'),(-1,'PX150XL right model')]:
 old=bpy.data.objects[name];bpy.data.objects.remove(old,do_unlink=True)
 c=bpy.data.curves.new(name,'FONT');c.body='PX150XL';c.size=.285;c.align_x='CENTER';c.align_y='CENTER';c.extrude=.00015;c.font=font;c.materials.append(mat)
 o=bpy.data.objects.new(name,c);bpy.context.scene.collection.objects.link(o)
 # Diagonal follows the end-cap sweep: rear high, forward low, readable from each outer side.
 slope=math.atan(0.5);normal=Vector((side,0,0));right=Vector((0,side*math.cos(slope),side*math.sin(slope)));up=normal.cross(right).normalized()
 o.rotation_euler=Matrix((right,up,normal)).transposed().to_euler()
 bpy.context.view_layer.update()
 # Anchor the top of P while matching measured top edge: dz/dy=0.5 (26.565 degrees).
 xmin=min(v[0] for v in o.bound_box);top=max(v[1] for v in o.bound_box);ax=xmin+.08
 oldright=Vector((0,side*math.cos(math.radians(20)),side*math.sin(math.radians(20))));oldup=normal.cross(oldright).normalized()
 o.location=Vector((side*8.04,.43,.77))+(oldright-right)*ax+(oldup-up)*top
 bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.ops.object.convert(target='MESH');o=bpy.context.object
 for v in o.data.vertices:
  co=o.matrix_world@v.co;hit,pt,n,idx=body.ray_cast(Vector((side*9,co.y,co.z)),Vector((-side,0,0)))
  if hit:v.co=o.matrix_world.inverted()@(pt+n*.008)
scene=bpy.context.scene;scene.cycles.samples=24;scene.render.resolution_x=1400;scene.render.resolution_y=950;cam=scene.camera;cam.data.ortho_scale=3.4
bpy.ops.wm.save_as_mainfile(filepath=str(p/'px150xl_endcap_parallel_top_v1.blend'))
for side,label in [(1,'left'),(-1,'right')]:
 cam.location=(side*11.5,3.6,2.0);cam.rotation_euler=(Vector((side*7.65,.65,.8))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(p/f'px150xl_{label}_parallel_top_v1.png');bpy.ops.render.render(write_still=True)
(p/'PARALLEL_LABEL_NOTES.md').write_text('2026-10-28 (Codex): User requested 300% PX150XL lettering from rear end-cap bend down toward front. Mock-up uses 3x font size (.285 versus .095), center Blender y=.43,z=.77, parallel to measured top edge at 26.565 degrees; P top position anchored; original diagonal 20 degrees rising toward rear (+Y), text projected to both curved caps with 8 mm offset. Text remains readable from each outside face; review slope/position against user intent. Earlier previews preserved. Scratch only; runtime source unchanged.\n')
