# PX150 XL Windrower rear mount v6: D140XL-style side brackets + top clevis, open centre, no hoses.
# Coordinates are written in i3d space (x lateral, y up, z forward; header root = origin) and mapped to Blender.
import bpy, bmesh, sys
from mathutils import Vector

OUT = r"C:\Users\groov\GE_work\px150\mount\px150Mount_v7.i3d"


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


BACK = -0.33    # back face of the header frame (z)
POST_X = 1.13   # frame posts, both sides (measured from the GE render)
W = 0.08        # bracket half width (box-section post)
TOP = 1.42      # top of the back beam

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


GY = -0.05      # bottom of the socket
CW = 0.11       # half gap between the socket cheeks (to the cheek centre)
CT = 0.0125     # cheek half thickness

for side, sx in (("Left", 1), ("Right", -1)):
    x = sx * POST_X
    # box-section post up the back wall
    finish(poly_prism("mountPost" + side, [(TOP, BACK), (TOP, BACK - 0.14), (0.30, BACK - 0.14),
                                          (0.30, BACK), ], x - W, x + W), M_BLACK)
    box("mountCap" + side, (x, TOP + 0.025, BACK - 0.06), (2 * W + 0.03, 0.05, 0.18), M_BLACK)
    # long tapered arm running forward under the header from the foot of the post
    finish(poly_prism("mountArm" + side, [(0.34, BACK - 0.14), (0.22, BACK + 1.00), (0.13, BACK + 1.00),
                                         (GY, BACK - 0.08), (GY, BACK - 0.14)], x - W, x + W), M_BLACK)
    # clevis socket behind the foot: two cheeks (top back corner cut off), open at the back and top
    cheek = [(GY, BACK - 0.08), (0.26, BACK - 0.08), (0.26, BACK - 0.22), (0.11, BACK - 0.38), (GY, BACK - 0.38)]
    for k, ox in ((0, -1), (1, 1)):
        cx = x + ox * CW
        finish(poly_prism("mountCheek%d%s" % (k, side), cheek, cx - CT, cx + CT), M_BLACK)
    # floor plate with a round hole straight down
    floor = box("mountFloor" + side, (x, GY + 0.015, BACK - 0.23), (2 * CW, 0.03, 0.30), M_BLACK)
    cut_hole_y(floor, x, BACK - 0.27, 0.045, GY, GY + 0.03)
    # cross bolt through both cheeks, low down, keeper on the outer cheek
    cyl("mountBolt" + side, (x - CW - 0.04, GY + 0.10, BACK - 0.19), (x + CW + 0.04, GY + 0.10, BACK - 0.19), 0.02, M_BLACK)
    ox = x + sx * (CW + CT + 0.012)
    box("mountKeeper" + side, (ox, GY + 0.10, BACK - 0.19), (0.012, 0.07, 0.025), M_BLACK)

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


# top hitch point (D140XL): wedge block bolted on top of the back beam, low at the outer end, rising toward the
# middle; a pin sticks out sideways from the low end and a long flat-strap U link hangs from it down the beam's back face
HX0, HX1 = 0.05, 0.55          # block, x (header left side of centre)
HZ0, HZ1 = BACK + 0.02, BACK - 0.16
finish(prism_z("hitchBlock", [(HX1, TOP), (HX1, TOP + 0.11), (HX0 + 0.08, TOP + 0.21), (HX0, TOP + 0.21), (HX0, TOP)],
               HZ1, HZ0), M_BLACK)
for i, bx in enumerate((HX1 - 0.12, HX1 - 0.30)):
    cyl("hitchBolt%d" % i, (bx, TOP + 0.08 + i * 0.03, HZ1), (bx, TOP + 0.08 + i * 0.03, HZ1 - 0.03), 0.028, M_STEEL, seg=6)
PY, PZ = TOP + 0.06, HZ1 + 0.03      # pin, near the back face of the block
cyl("hitchPin", (HX1 - 0.02, PY, PZ), (HX1 + 0.20, PY, PZ), 0.03, M_STEEL)
cyl("hitchPinHead", (HX1 + 0.20, PY, PZ), (HX1 + 0.22, PY, PZ), 0.042, M_STEEL)
SB = TOP - 0.30                      # bottom of the link
SZ = HZ1 - 0.015                     # straps hang flat behind the block / beam face
for i, sxp in enumerate((HX1 + 0.04, HX1 + 0.16)):
    # flat strap: wraps over the pin, runs straight down the beam face
    box("hitchStrap%d" % i, (sxp, (PY + SB) / 2, SZ - 0.006), (0.028, PY - SB, 0.012), M_STEEL)
    box("hitchStrapTop%d" % i, (sxp, PY + 0.036, (SZ + PZ) / 2 + 0.01), (0.028, 0.012, abs(PZ - SZ) + 0.07), M_STEEL)
    box("hitchStrapFront%d" % i, (sxp, PY + 0.005, PZ + 0.04), (0.028, 0.07, 0.012), M_STEEL)
box("hitchStrapBottom", (HX1 + 0.10, SB, SZ - 0.006), (0.148, 0.012, 0.012), M_STEEL)

bpy.context.view_layer.update()

sys.path.insert(0, bpy.utils.user_resource('SCRIPTS', path="addons"))
import io_export_i3d.dcc as dccpkg
from io_export_i3d import i3d_export
from io_export_i3d.dcc import dccBlender as d
d.isNodeVisible = lambda n: bpy.data.objects[n].visible_get()
try:
    dccpkg.isNodeVisible = d.isNodeVisible
except Exception:
    pass
d.UISetAttrBool('i3D_exportUseSoftwareFileName', False)
d.UISetAttrString('i3D_exportFileLocation', OUT)
i3d_export.I3DExportAll()
from io_export_i3d.util import logUtil
print("EXPORT LOG:", getattr(logUtil.ActionLog, "message", ""))
