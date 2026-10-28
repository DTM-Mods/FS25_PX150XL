# Preserved bracket information

2026-10-28 (Codex): User requested deletion of the old PX150 XL project to start over with a different header. Only bracket information, build scripts, reusable mount geometry and relevant mounting reference images were retained here. Verified against local project files; no new in-game test.

## Measured mounting points
In the header input-joint frame (x forward, y up, z sideways):
- Lower lift-arm connections: (0, 0, +/-1.274) m (carrier arms approximately +/-1.266 m).
- M1240 top-link endpoint: (0.370, 1.122, 0) m.
- D140XL joint sits 1.756 m behind and 0.274 m below the front cutting line, tilted back 18.72 degrees.
- Measured D140XL input settings: cutter joint, m1240 subtype, lower/upper distance 0.4/2.2 m, upperRotationOffset 5 degrees, lowerRotationOffset 0.

## Old-header coordinates: reference only
Old joint origin: (0, -0.274, -0.536), parent rotation (0, -90, 0), child rotation (0, 0, +18.72).
Axes: x_j=(0,0.321,0.947), y_j=(0,0.947,-0.321), z_j=(-1,0,0).
Lower bolts: (+/-1.274,-0.274,-0.536). Correct carrier top-link point: (0,0.907,-0.546).
The old silver top hitch on the back beam was about 0.68 m above the carrier top-link point. Do not blindly reuse that placement on the replacement header.
The old negative -18.72 joint tilt was incorrect. Fit the new header using its own dimensions and verify in game.

## Bracket appearance and build lessons
Two black smooth-metal lower brackets, plus silver two-plate top hitch with cross pin. Earlier designs and scripts are retained for reference, not approved final fit for a new header.
The reusable kit includes actual I3D and shapes, Blender generator and GE merge script.
Old FD250 materials needed UV1 collapsed to a clean normal/vmask atlas location (0.0391,0.4766), UV2 real-scale mapping, 6 mm bevels and smooth shading. Another header needs its own materials/UV treatment.
Reference images show the desired D140XL mounting and M1240 linkage connections.

The original shared kit remains at ../Library/_M1240MountKit/. Nothing outside this project folder was deleted or changed.
