import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path.cwd();out=r/'previews/right_label_center_v1'
bpy.ops.wm.open_mainfile(filepath=str(r/'previews/mount_fixed_steel_pins_v1/working_trim_with_steel_pins_v1.blend'))
scene=bpy.context.scene
scene.cycles.samples=16
scene.render.resolution_x=1000;scene.render.resolution_y=700;scene.render.resolution_percentage=100
cam=scene.camera;cam.data.ortho_scale=2.65
cam.location=(-12,2.8,1.7);cam.rotation_euler=(Vector((-7.9,.45,.8))-cam.location).to_track_quat('-Z','Y').to_euler()
left=bpy.data.objects['PX150XL left model'];right=bpy.data.objects['PX150XL right model']
def bounds(obj):
 q=[(obj.matrix_world@v.co).z-.5*(obj.matrix_world@v.co).y for v in obj.data.vertices]
 return min(q),max(q)
l=bounds(left);b=bounds(right);delta=sum(l)/2-sum(b)/2
scene.render.filepath=str(out/'before.png');bpy.ops.render.render(write_still=True)
body=bpy.data.objects['headerHD50F_vis']
for v in right.data.vertices:
 co=right.matrix_world@v.co;co.z+=delta
 hit,pt,n,idx=body.ray_cast(Vector((-9,co.y,co.z)),Vector((1,0,0)))
 assert hit
 v.co=right.matrix_world.inverted()@(pt+n*.008)
bpy.context.view_layer.update();a=bounds(right)
assert a[0]>.485 and a[1]<.720,(l,b,a)
(out/'measurements.json').write_text(json.dumps(dict(left_stripe_coordinates=l,right_before=b,right_after=a,vertical_shift=delta),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out/'right_label_centered_preview.blend'))
scene.render.filepath=str(out/'after.png');bpy.ops.render.render(write_still=True)
