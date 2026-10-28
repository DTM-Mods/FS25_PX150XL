# M1240 mount kit (PropaineX)

Our own geometry (no DLC parts) that lets any header hitch to the MacDon M1240 like the D140XL does:
two black lift-arm brackets (post, tapered arm forward under the header, clevis socket with a cross bolt and a
round hole in the floor) and a silver top hitch (two upright plates with a pin across the top, on the back beam).
First used on the PX150 XL Windrower (FS25_PX150XL, 2026-10-28).

## Files
- `m1240MountKit_px150.i3d` + `.shapes`: the kit as built for the PX150 XL (FD250 frame). Root node `px150Mount`.
- `build_m1240_mount_kit.py`: Blender build script. Change HEADER SETTINGS at the top for another header, then
  `blender -b -P build_m1240_mount_kit.py -- <out.i3d>` (needs the GIANTS i3d exporter add-on enabled; don't use
  `--factory-startup`; the output folder must already exist, or nothing is written).
- `merge_m1240_mount_kit.lua`: GE script that links the kit under the header's main component and gives it the
  header's own black and steel materials. Edit the settings at the top first.

## Where the parts go (measured in game, 2026-10-28)
The M1240 meets a header at three points, in the header's input-joint space (x forward, y up, z sideways):
- lift-arm ends: (0, 0, +-1.27), so the bracket bolts sit at the joint's height and depth, 1.274 m out each side;
- top link end: (0.370, 1.122, 0).
So JOINT in the build script must be the position of the header's M1240 input joint node. The joint itself must
match the D140XL's: 1.756 m behind and 0.274 m below the front of the cut line, tilted back 18.72 deg
(details in FS25_Universal_Knowledge.md).

## Using it on a header
1. Give the header an M1240 input joint as above (`<inputAttacherJoint jointType="cutter">` with
   `<subType name="m1240" showWarning="false"/>`).
2. Measure the header's back wall (BACK) and back-beam top (TOP), set them and JOINT, run the build script.
3. Open a COPY of the header i3d in GE, set the merge script's settings, source it, File > Save, close GE.
4. Optional: `topReferenceNode` on the input joint at the hitch pin so the M1240's top link reaches it.
   On the PX150 XL the beam is about 0.68 m higher than the D140XL's top-link point, so the link would stretch.

## Known limits
- Brackets are plain boxes and prisms, simpler than the D140XL's.
- Material slots are borrowed from the header (PX150: fd250_vis slots 2 black, 3 steel). Another header needs its
  own slot numbers.
