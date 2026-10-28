import bpy,pathlib,math
p=pathlib.Path.cwd()/'previews/hd50f_adapter_v1'
bpy.ops.wm.open_mainfile(filepath=str(p/'hd50f_bracket_pins_visible_v2.blend'))
# Dark painted frame based on saved D140XL reference images; retain steel pins and rubber.
m=bpy.data.materials['John Deere painted green'];s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(.016,.018,.020,1);s.inputs['Roughness'].default_value=.34
m.name='PX150XL dark graphite paint'
for o in list(bpy.data.objects):
 if o.name.startswith('logos_decals'):bpy.data.objects.remove(o,do_unlink=True)
white=bpy.data.materials.new('PropaineX lettering');white.use_nodes=True;s=white.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(.88,.88,.85,1);s.inputs['Roughness'].default_value=.42
fontpath=pathlib.Path('C:/Windows/Fonts/arialbd.ttf');font=bpy.data.fonts.load(str(fontpath)) if fontpath.exists() else None
def lettering(name,text,location,size,max_width):
 c=bpy.data.curves.new(name,'FONT');c.body=text;c.size=size;c.align_x='CENTER';c.align_y='CENTER';c.extrude=.00015
 if font:c.font=font
 o=bpy.data.objects.new(name,c);bpy.context.scene.collection.objects.link(o);o.location=location;o.rotation_euler=(math.pi/2,0,math.pi);c.materials.append(white)
 bpy.context.view_layer.update()
 if o.dimensions.x>max_width:o.scale*=max_width/o.dimensions.x
 return o
# Place new labels on the rear beam and rear side panels, facing the carrier.
lettering('PropaineX rear brand','PropaineX',(0,1.322,1.18),.095,.65)
lettering('PX150XL left model','PX150XL',(2.05,1.28,.95),.105,.80)
lettering('PX150XL right model','PX150XL',(-2.05,1.28,.95),.105,.80)
scene=bpy.context.scene;scene.render.filepath=str(p/'px150xl_dark_branding_v1.png')
bpy.ops.wm.save_as_mainfile(filepath=str(p/'px150xl_dark_branding_v1.blend'));bpy.ops.render.render(write_still=True)
(p/'PAINT_BRANDING_NOTES.md').write_text('2026-10-28 (Codex): User requested D140XL colors, then specified replacement branding PropaineX and model PX150XL. Scratch scene px150xl_dark_branding_v1.blend uses dark graphite frame paint sampled by visual interpretation of saved D140XL reference images; steel pins/hitch and black rubber retained. Existing logos_decals objects removed; new PropaineX beam lettering and PX150XL rear panel labels added as preview text objects. No MacDon/DLC textures copied. Render colors/materials are approximate, verified Blender only, UNTESTED in game. Runtime source unchanged pending visual review.\n')
