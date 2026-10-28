# PX150XL M1240 windrower: mechanical conversion

2026-10-28 (Codex), source version 2.0.0.0. Not zipped, installed, or tested in game.

## Runtime source
- modDesc.xml registers only px150xlWindrower.xml and requires pdlc_macDonPack.
- px150xlWindrower.xml is type mower with COMBINE_MOWER converter, a 15.2 m cutting area, 1.5 m center auxiliary swath-drop area, independent IMPLEMENT_EXTRA header toggle, lowered-only forward work, reel/belt/knife animation and grain cutter effects. No combine feeding spec, PTO input or combine coupler.
- px150xlWindrower.i3d is a hierarchy-preserving mechanical derivative of the original animated HD50F. Its shapes reference remains headerHD50F.i3d.shapes. Both files are required.
- M1240 joint: (0,-0.274,-1.360056), parent rotation (0,-90,0), child (0,0,+18.72). Lower/upper lift distances 0.4/2.2 m, upper offset 5 degrees. Bottom reference nodes +/-1.274 m. Top carrier reference is (0,0.907393,-1.369728).
- Cut line in input-joint frame: forward 1.751043 m, up -0.304072 m; agrees with measured D140XL (1.746,-0.304) to about 5 mm.
- Ground reference is on the cut line, not an old feeder adapter. Combine support-wheel physics/support animation removed so they cannot hold the cutting line up; support wheel bones hidden.
- Retains 130 kW power requirement of the 15.2 m source machine; D140XL reference is 35 kW for 12.2 m. This load requires carrier testing.
- Native wheat, barley, oat, canola, soybean swaths supported; additional crops depend on map converters. Pickup conversion checked against native PICKUPHEADER_GRAIN for all five.

## Validation
Vehicle and modDesc XML schema checks: 0 reported problems. 109 I3D mappings, 0 broken. 54 file references resolve. Shape file exists. Native crop/swath/pickup converters checked. Results in source/mechanical/validation.json.

## Outstanding, do not call verified in game
1. Actual M1240 hitch, raised/lowered pitch, cutting clearance, crop cutting, center swath and PW8 pickup need an in-game test. No game restart or mod installation performed.
2. Approved edited geometry/paint/bracket/branding remain Blender preview scenes. The mechanical runtime still uses the original animated HD50F main mesh; the edited static OBJ mesh cannot replace that skinned mesh without rebuilding its material subsets and animation bindings. Do not imply the approved appearance is already in the runtime source. No drum animation is configured, but original drum geometry still exists in runtime shapes.
3. Visible bracket kit top hitch on the beam differs from carrier's true top-link reference. The XML references carrier contact coordinates, not the higher preview silver pin. Resolve before a combined visual/mechanical build.
4. Shop image/icon are currently original HD50F placeholders.

The user authorized mechanical conversion, not packaging or installation. Keep source and previews; no ZIP until requested.
