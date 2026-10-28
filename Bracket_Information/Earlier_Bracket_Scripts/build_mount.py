# PX150 XL Windrower rear mount: two hook brackets, coupler block, hydraulic hoses.
# Coordinates are written in i3d space (x lateral, y up, z forward; header root = origin) and mapped to Blender.
import bpy, bmesh, sys
from mathutils import Vector

OUT = r"C:\Users\groov\GE_work\px150\mount\px150Mount_v3.i3d"


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
T = 0.035       # bracket plate half thickness

for side, sx in (("Left", 1), ("Right", -1)):
    x = sx * POST_X
    # tall plate: deep at the bottom, shallow at the top; squared cradle hook with a chamfered lip at the bottom
    prof = [(1.36, BACK), (1.36, BACK - 0.16), (0.55, BACK - 0.30),
            (0.22, BACK - 0.30), (0.22, BACK - 0.36),
            (0.30, BACK - 0.42), (0.30, BACK - 0.48),
            (-0.10, BACK - 0.48), (-0.10, BACK - 0.06),
            (0.08, BACK - 0.06), (0.08, BACK)]
    plate = finish(poly_prism("mountPlate" + side, prof, x - T, x + T), M_BLACK)
    cut_hole(plate, (0.92, BACK - 0.13), 0.075, x - T, x + T)  # round lightening hole: our own touch
    box("mountSaddle" + side, (x, 0.04, BACK - 0.27), (0.11, 0.05, 0.36), M_BLACK)
    box("mountStripe" + side, (x + sx * (T + 0.002), 1.02, BACK - 0.235), (0.004, 0.86, 0.025), M_RED)
    box("mountFitting" + side, (x, 1.39, BACK - 0.08), (0.10, 0.06, 0.09), M_STEEL)
    cyl("mountFittingNipple" + side, (x, 1.40, BACK - 0.13), (x, 1.40, BACK - 0.20), 0.016, M_STEEL)

# hydraulic coupler block on the top beam, centre
box("couplerBlock", (0, 1.40, BACK - 0.10), (0.36, 0.12, 0.14), M_BLACK)
box("couplerPlate", (0, 1.40, BACK - 0.18), (0.40, 0.15, 0.02), M_STEEL)
for i, cx in enumerate((-0.14, -0.05, 0.05, 0.14)):
    cyl("couplerNipple%d" % i, (cx, 1.40, BACK - 0.19), (cx, 1.40, BACK - 0.26), 0.018, M_STEEL)
    box("couplerCap%d" % i, (cx, 1.40, BACK - 0.27), (0.045, 0.045, 0.02), M_RED if i in (0, 3) else M_STEEL)

# hoses: coupler -> over the top -> down into each bracket fitting (the M1240 feed), and coupler -> reel lift
for side, sx in (("Left", 1), ("Right", -1)):
    x = sx * POST_X
    cx = sx * 0.14
    hose("hoseFeed" + side, [(cx, 1.40, BACK - 0.27), (cx + sx * 0.12, 1.47, BACK - 0.36),
                             (x * 0.6, 1.52, BACK - 0.32), (x, 1.50, BACK - 0.24), (x, 1.42, BACK - 0.20)])
    cx2 = sx * 0.05
    hose("hoseReel" + side, [(cx2, 1.52, BACK - 0.03), (cx2 + sx * 0.10, 1.60, BACK + 0.12),
                             (sx * 0.14, 1.66, 0.12), (sx * 0.07, 1.70, 0.21)], r=0.014)
    box("reelFitting" + side, (sx * 0.07, 1.71, 0.24), (0.06, 0.05, 0.06), M_STEEL)
    box("hoseClamp" + side, (x, 1.30, BACK - 0.20), (0.07, 0.03, 0.05), M_STEEL)

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
