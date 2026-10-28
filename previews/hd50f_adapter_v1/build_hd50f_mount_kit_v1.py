# M1240 mount kit (PropaineX): two black lift-arm brackets + silver top hitch (two plates + pin) for any header
# that should hitch to the MacDon M1240. Run:  blender -b -P build_m1240_mount_kit.py -- <out.i3d>
# Coordinates are i3d space of the HEADER'S MAIN COMPONENT (x side, y up, z forward). Fill in HEADER SETTINGS.
import sys
# PX150 XL Windrower rear mount v6: D140XL-style side brackets + top clevis, open centre, no hoses.
# Coordinates are written in i3d space (x lateral, y up, z forward; header root = origin) and mapped to Blender.
import bpy, bmesh, sys
from mathutils import Vector

OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else r"C:\Users\groov\GE_work\m1240MountKit.i3d"

# ---------------- HEADER SETTINGS (values below = PX150 XL / FD250 frame) ----------------
JOINT = (0.0, -0.274, -1.360056)  # header's M1240 input joint node position (D140XL-equivalent: 1.756 behind and 0.274
                               # below the cut line front, tilted back 18.72 deg; see FS25_Universal_Knowledge.md)
BACK = -1.15    # back face of the header's back wall (z) where the bracket posts sit
TOP = 1.30      # top of the back beam (y): posts reach up to it, top hitch sits on it
ATLAS_FLAT_UV = (0.0391, 0.4766)  # flat + clean spot in the header's _normal/_vmask atlas (FD250)
# ------------------------------------------------------------------------------------------


def i2b(x, y, z):  # i3d -> Blender (Blender Z up, Blender -Y = i3d +Z); checked with axisProbe after export
    return Vector((x, -z, y))


for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)


def mat(name, rgb):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*rgb, 1)
    return m


M_BLACK = mat("px150Mount_black_mat", (0.02, 0.02, 0.02))
M_RED = mat("px150Mount_red_mat", (0.45, 0.01, 0.02))
M_HOSE = mat("px150Mount_hose_mat", (0.01, 0.01, 0.012))
M_STEEL = mat("px150Mount_steel_mat", (0.55, 0.55, 0.56))

root = bpy.data.objects.new("px150Mount", None)
bpy.context.scene.collection.objects.link(root)


def link(name, me):
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def finish(obj, material):
    obj.data.materials.append(material)
    obj.parent = root
    me = obj.data
    while len(me.uv_layers) < 2:
        me.uv_layers.new(name="UV%d" % (len(me.uv_layers) + 1))
    obj["i3D_collision"] = False
    return obj


def poly_prism(name, profile_yz, x0, x1):
    """Extrude an outline (list of (y, z) in i3d space) across x from x0 to x1."""
    bm = bmesh.new()
    a = [bm.verts.new(i2b(x0, y, z)) for (y, z) in profile_yz]
    b = [bm.verts.new(i2b(x1, y, z)) for (y, z) in profile_yz]
    bm.faces.new(a[::-1])
    bm.faces.new(b)
    n = len(profile_yz)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return link(name, me)


def box(name, c, s, material):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = i2b(c[0] + v.co.x * s[0], c[1] + v.co.y * s[1], c[2] + v.co.z * s[2])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return finish(link(name, me), material)


def cyl(name, p0, p1, r, material, seg=16, keep=True):
    p0, p1 = i2b(*p0), i2b(*p1)
    d = p1 - p0
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=d.length)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = link(name, me)
    obj.location = (p0 + p1) / 2
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    bpy.context.view_layer.update()
    obj.data.transform(obj.matrix_world)
    obj.matrix_world.identity()
    return finish(obj, material) if keep else obj


def cut_hole(obj, center_yz, r, x0, x1):
    c = cyl("holeCutter", (x0 - 0.05,) + center_yz, (x1 + 0.05,) + center_yz, r, M_BLACK, seg=24, keep=False)
    mod = obj.modifiers.new("hole", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = c
    mod.solver = 'EXACT'
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    obj.modifiers.clear()
    old = obj.data
    obj.data = me
    bpy.data.meshes.remove(old)
    bpy.data.objects.remove(c, do_unlink=True)


def hose(name, pts, r=0.017):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = r
    cu.bevel_resolution = 3
    cu.resolution_u = 10
    cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = i2b(*p)
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    tmp = link(name + "_c", cu)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp, do_unlink=True)
    return finish(link(name, me), M_HOSE)


POST_X = 1.274  # = M1240 lift-arm ends (probe: D140XL bottomArmRef +-1.274 in joint space)
W = 0.08        # bracket half width (box-section post)

def cut_hole_y(obj, x, z, r, y0, y1):
    """Vertical round hole (along i3d y)."""
    c = cyl("holeCutterY", (x, y0 - 0.05, z), (x, y1 + 0.05, z), r, M_BLACK, seg=24, keep=False)
    mod = obj.modifiers.new("hole", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = c
    mod.solver = 'EXACT'
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    obj.modifiers.clear()
    old = obj.data
    obj.data = me
    bpy.data.meshes.remove(old)
    bpy.data.objects.remove(c, do_unlink=True)


BOLT_Y, BOLT_Z = JOINT[1], JOINT[2]  # M1240 lift-arm ends: joint height/depth, +-1.274 sideways (probe 2026-10-28)
GY = BOLT_Y - 0.10  # bottom of the socket
CW = 0.11       # half gap between the socket cheeks (to the cheek centre)
CT = 0.0125     # cheek half thickness

for side, sx in (("Left", 1), ("Right", -1)):
    x = sx * POST_X
    # box-section post up the back wall
    finish(poly_prism("mountPost" + side, [(TOP, BACK), (TOP, BACK - 0.14), (GY + 0.35, BACK - 0.14),
                                          (GY + 0.35, BACK), ], x - W, x + W), M_BLACK)
    box("mountCap" + side, (x, TOP + 0.025, BACK - 0.06), (2 * W + 0.03, 0.05, 0.18), M_BLACK)
    # long tapered arm running forward under the header from the foot of the post
    finish(poly_prism("mountArm" + side, [(GY + 0.39, BACK - 0.14), (0.22, BACK + 1.00), (0.13, BACK + 1.00),
                                         (GY, BACK - 0.08), (GY, BACK - 0.14)], x - W, x + W), M_BLACK)
    # clevis socket behind the foot: two cheeks (top back corner cut off), open at the back and top
    cheek = [(GY, BACK - 0.08), (GY + 0.31, BACK - 0.08), (GY + 0.31, BACK - 0.22), (GY + 0.16, BACK - 0.38), (GY, BACK - 0.38)]
    for k, ox in ((0, -1), (1, 1)):
        cx = x + ox * CW
        finish(poly_prism("mountCheek%d%s" % (k, side), cheek, cx - CT, cx + CT), M_BLACK)
    # floor plate with a round hole straight down
    floor = box("mountFloor" + side, (x, GY + 0.015, BACK - 0.23), (2 * CW, 0.03, 0.30), M_BLACK)
    cut_hole_y(floor, x, BACK - 0.27, 0.045, GY, GY + 0.03)
    # cross bolt through both cheeks, low down, keeper on the outer cheek
    cyl("mountBolt" + side, (x - CW - 0.04, BOLT_Y, BOLT_Z), (x + CW + 0.04, BOLT_Y, BOLT_Z), 0.02, M_BLACK)
    ox = x + sx * (CW + CT + 0.012)
    box("mountKeeper" + side, (ox, BOLT_Y, BOLT_Z), (0.012, 0.07, 0.025), M_BLACK)

def prism_z(name, profile_xy, z0, z1):
    """Extrude an outline (list of (x, y) in i3d space) along z from z0 to z1."""
    bm = bmesh.new()
    a = [bm.verts.new(i2b(x, y, z0)) for (x, y) in profile_xy]
    b = [bm.verts.new(i2b(x, y, z1)) for (x, y) in profile_xy]
    bm.faces.new(a[::-1])
    bm.faces.new(b)
    n = len(profile_xy)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return link(name, me)


# top hitch point (D140XL, reference/D140XL_top_hitch_rear.png + D140XL_rear_straight.png): in the middle of the back
# beam, two upright flat plates (thin side to side) up the beam's back face and standing above its top, a cross pin
# through both at the top with its ends sticking out
FACE = BACK - 0.16                   # back face of the back beam (block in v6-v8 sat flush here)
PT = 0.009                           # plate half thickness
PX = 0.065                           # plate centres at +-PX
PZ0, PZ1 = FACE + 0.05, FACE - 0.06  # plates: into the beam, out behind it
PY0, PY1 = TOP - 0.15, TOP + 0.13    # plates: bottom (stops above the beam's bottom edge, ~TOP-0.175), top
for i, px in enumerate((-PX, PX)):
    finish(poly_prism("hitchPlate%d" % i, [(PY1, PZ0), (PY1, PZ1 + 0.02), (PY1 - 0.02, PZ1), (PY0 + 0.02, PZ1),
                                          (PY0, PZ1 + 0.02), (PY0, PZ0)], px - PT, px + PT), M_STEEL)
PY, PZ = TOP + 0.085, FACE - 0.015   # pin
cyl("hitchPin", (-PX - 0.05, PY, PZ), (PX + 0.07, PY, PZ), 0.02, M_STEEL)
cyl("hitchPinHead", (-PX - 0.06, PY, PZ), (-PX - 0.045, PY, PZ), 0.03, M_STEEL, seg=6)

# finishing pass: rounded edges + real-scale UVs (1 m = 1 UV unit, box projection) so the frame's metal detail
# texture tiles like on the game's own parts instead of stretching into wood-like streaks
import math
for obj in [o for o in bpy.data.objects if o.type == 'MESH']:
    if not obj.name.startswith(("hitchPin",)):
        bev = obj.modifiers.new("bevel", 'BEVEL')
        bev.width = 0.006
        bev.segments = 2
        bev.limit_method = 'ANGLE'
        bev.angle_limit = math.radians(40)
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
        obj.modifiers.clear()
        old = obj.data
        obj.data = me
        bpy.data.meshes.remove(old)
    me = obj.data
    for poly in me.polygons:
        poly.use_smooth = True
    if hasattr(me, "set_sharp_from_angle"):
        me.set_sharp_from_angle(angle=math.radians(40))
    while len(me.uv_layers) < 2:
        me.uv_layers.new(name="UV%d" % (len(me.uv_layers) + 1))
    mw = obj.matrix_world
    # UV1 -> one flat, clean spot of the header's normal/wear atlas (FD250: block flat in both V orientations),
    # so no panel detail shows; UV2 -> real scale for the detail library texture
    for d in me.uv_layers[0].data:
        d.uv = ATLAS_FLAT_UV
    for uvl in list(me.uv_layers)[1:]:
        for poly in me.polygons:
            n = poly.normal
            ax = max(range(3), key=lambda i: abs(n[i]))
            for li in poly.loop_indices:
                co = mw @ me.vertices[me.loops[li].vertex_index].co
                u, v = [(co.y, co.z), (co.x, co.z), (co.x, co.y)][ax]
                uvl.data[li].uv = (u, v)

bpy.context.view_layer.update()


import pathlib
bpy.ops.wm.save_as_mainfile(filepath=str(pathlib.Path.cwd()/"previews/hd50f_adapter_v1/hd50f_mount_kit_v1.blend"))
