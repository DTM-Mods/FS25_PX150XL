import bpy,pathlib
p=pathlib.Path.cwd()/'previews/hd50f_adapter_v1'
bpy.ops.wm.open_mainfile(filepath=str(p/'textured_preview_no_fingers_v1.blend'))
with bpy.data.libraries.load(str(p/'hd50f_mount_kit_v1.blend'),link=False) as (src,dst):dst.objects=src.objects
for o in dst.objects:
 if o is not None:bpy.context.scene.collection.objects.link(o)
for m in bpy.data.materials:
 if m.name.startswith('px150Mount') and m.use_nodes:
  s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Metallic'].default_value=.75 if 'steel' in m.name else .35;s.inputs['Roughness'].default_value=.32
scene=bpy.context.scene;scene.render.filepath=str(p/'hd50f_with_brackets_v1.png')
bpy.ops.wm.save_as_mainfile(filepath=str(p/'hd50f_with_brackets_v1.blend'));bpy.ops.render.render(write_still=True)
(p/'BRACKET_FIT_NOTES.md').write_text('2026-10-28 (Codex): Saved user bracket generator adapted to HD50F preview. Black lower bracket pair at x +/-1.274 m; JOINT=(0,-0.274,-1.360056) derived from HD50F cutting line z=0.395944 minus D140XL reference 1.756 m. BACK=-1.15, TOP=1.30 m are preliminary visual fit values. Silver top hitch retained on back beam as in saved design. Its height is NOT yet verified against carrier top-link endpoint; M1240 fit and ground clearance UNTESTED. Regenerated own kit geometry from preserved script; original kit unchanged. Scratch scene hd50f_with_brackets_v1.blend; render hd50f_with_brackets_v1.png. Production I3D/XML unchanged pending preview review.\n')
