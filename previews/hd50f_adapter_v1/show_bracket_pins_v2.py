import bpy,pathlib
p=pathlib.Path.cwd()/'previews/hd50f_adapter_v1'
bpy.ops.wm.open_mainfile(filepath=str(p/'hd50f_with_brackets_v1.blend'))
bpy.data.objects['Neutral ground'].location.z=-.58
steel=bpy.data.materials.get('px150Mount_steel_mat')
for name in ['mountBoltLeft','mountBoltRight','mountKeeperLeft','mountKeeperRight']:
 o=bpy.data.objects[name];o.data.materials.clear();o.data.materials.append(steel)
scene=bpy.context.scene;scene.render.filepath=str(p/'hd50f_bracket_pins_visible_v2.png')
bpy.ops.wm.save_as_mainfile(filepath=str(p/'hd50f_bracket_pins_visible_v2.blend'));bpy.ops.render.render(write_still=True)
(p/'BRACKET_PIN_REVIEW.md').write_text('2026-10-28 (Codex): CORRECTION to bracket fit preview: previous floor z=-0.07 hid lower sockets/pins at z=-0.274. New preview ground z=-0.58 exposes them. Existing mountBoltLeft/Right and keeper materials changed to steel for visibility. No bracket geometry flipped; under-header support arms run forward and sockets extend rearward toward carrier. Pin centers remain (+/-1.274,1.360056,-0.274) Blender coordinates. This does not establish proper operating clearance or M1240 fit. User suspects reversed brackets; clearer view supplied for review before changing orientation. Runtime source unchanged.\n')
