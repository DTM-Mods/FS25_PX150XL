# PX150 XL Windrower Pro Edition - complete testing build

2026-10-28 (Codex). Current version **2.1.1.0**. This supersedes the earlier mechanical-only 2.0.0.0 status.

## Finished runtime
- px150xlWindrower.xml + px150xlWindrower.i3d + px150xlWindrower.i3d.shapes: integrated animated edited header, not the old HD50F visual mesh.
- Combine rear receiver, combine coupler, entire feed drum/fingers and support-wheel geometry physically removed. Main mesh rebuilt from the supported GIANTS Editor OBJ export; no shapes archive decoded.
- Preserved all 23 original single-weight animation bindings. Controlled-pose comparison against original: maximum remaining-vertex error 0.000014142 m; reelArm, reel/reelPart and knife motions verified in GIANTS Editor.
- Main frame and extensions dark graphite, own black bracket pair and steel pins/top hitch integrated. PropaineX beam lettering and 300% PX150XL labels parallel to outer end-cap tops integrated as actual geometry.
- M1240-only cutter/m1240 joint; lift heights 0.4/2.2, upper rotation offset 5 degrees. Lower bolts +/-1.274 at y=-0.274,z=-1.360056. Top reference now points at actual silver hitch pin (0,1.385,-1.325), not the lower D140XL contact point. Carrier top-link reach/appearance requires in-game verification.
- Type mower, COMBINE_MOWER converter, 15.2 m cutting width, 1.5 m center drop area. Independent header toggle. Grain swaths for wheat/barley/oat/canola/soybean; map crops depend on converter support. PW8 pickup conversion verified in native game XML.
- 45 kW at 470 RPM; demand chosen for 15.2 m swathing based on measured 35 kW/12.2 m D140XL. Working speed 10 km/h.
- Store category **specialHeaders**, own PropaineX brand. New rendered store picture. Own PX150 XL icon with saved PRO EDITION banner at the top. Title ends in Pro Edition.
- Unchanged base-game textures referenced via $data; editable copies retained in source workspace.

## Validation and distribution
- GIANTS TestRunner 0.9.23 **PASS**: source/validation/testrunner/testResult_FS25_PX150XL_tmp_20724_PASS.xml.
- Vehicle and modDesc schema checks passed; 109 mappings, 0 broken; final binary loaded and shaders checked in GIANTS Editor.
- ZIP: Testing_local/FS25_PX150XL.zip. 7 runtime files, 12,034,493 bytes. CRC and entry SHA-256 match source; notes, previews, tools and bracket archive excluded.
- SHA-256: BC374ECFF61D1AB80CDFBE7D096A33D34D3CD498FAFE5160A5913F8820CF9D0C
- No server upload or local mods installation, as requested destination was local testing.
- Actual in-game M1240 attachment, raised/lowered attitude, crop cutting, center swath and PW8 pickup **NOT YET TESTED**. Do not claim in-game verification.

## Rebuild references
- source/integration/rig_rest.obj + rig_encoded.obj: supported rest and diagnostic-pose OBJ exports.
- rig_binding.npz: recovered vertex-to-bone assignment; each bone translated by unique known offset in scratch model, restored immediately after export.
- rebuild_animated_mesh.py -> animated_edited_test.i3d. Original I3D hierarchy and node indices retained; new singleblendweights IndexedTriangleSet added using exported positions/normals/UVs.
- approved_mount_and_labels.i3d from official Blender exporter with binaryFiles=false, merged by assemble_final_asset.py; GIANTS Editor compiled final_complete_binary.i3d/.shapes, promoted to runtime.
- Final QA fixes: icon DXT1 no mipmaps, brand DXT5 no mipmaps, store DXT5 three mip levels, bilingual CDATA description/changelog, base-game texture references.
- source/mechanical/package_local.py packages runtime dependencies only. Re-running the old convert_windrower.py would overwrite the finished XML/model setup; use it only as historical source.

Standing preview preference: open comparisons in VS Code automatically. When using GIANTS Editor, arrange Editor left and VS Code/Codex right, keep Editor active for scripted input, and verify foreground before each input.

## 2.1.1.0 store-picture correction
2026-10-28 (Codex): image-only update; closer three-quarter render, less harsh lighting, bottom-anchored shop texture following native header image layout. Image bbox (8,290)..(504,508) on 512x512; DXT5 with 3 mips. Before/after opened in existing VS Code editor. Model geometry and joints unchanged. GIANTS TestRunner PASS. User screenshots show unsupported top hitch and floating PropaineX name; deferred square cross tube behind hitch is recorded in DEFERRED_REPAIRS.md and explicitly NOT applied. User screenshots confirm attachment only; harvesting behavior not verified.

## Configured mass change
2026-10-28 (Codex): User explicitly set PX150XL mass to 2.95 tonnes. Updated the sole runtime component mass from 4700 to 2950 kg in px150xlWindrower.xml. Verified XML readback; no other physics settings changed. Source-only change; existing Testing_local ZIP not rebuilt by this task.

## 2.1.2.0 crossbar integrated
2026-10-28 (Claude): User approved previews/crossbar_v1 and asked to add the bar. Runtime px150xlWindrower.i3d/.shapes now = crossbar_integrated_unoptimized.i3d converted with Blender exporter util/i3dConverter.exe (no GE GUI driving); build kept in source/integration/crossbar_build_v2/. Hierarchy diff vs 2.1.1.0 by index path: only new node 0|8 PX150XL_square_steel_crossbar (PX150XL_bracket_black, 0 1.24 -1.24) and PropaineX rear brand moved 0.65 1.23 -1.322 -> 0.65 1.24 -1.323; all i3dMappings unaffected. Pre-crossbar backup: source/integration/v2_1_1_before_crossbar/. modDesc 2.1.2.0 (changelog: crossbar + 2.95 t mass). GIANTS TestRunner PASS, 0 warnings: source/validation/testrunner/testResult_FS25_PX150XL_2_1_2_0_PASS.xml. NOT zipped (waiting for user). Not yet seen in game.
Next: user wants END CAPS in MacDon colour to match. End caps are part of headerHD50F_vis, single material headerHD50F_JOHNDEERE_GREEN1_mat (graphite 0.016 0.018 0.02) shared with the frame, so caps need their faces split onto a new material (mesh rebuild). MacDon colour source still to choose (probe mod read of M1240 vs user screenshot). Preview first.

2026-10-28 (Claude): 2.1.2.0 zipped by package_local.py (7 files, 12,057,341 bytes, SHA-256 419318D1F52DBAD5178E079066B15F0ED9F0E4E0B1DBCF64D201F0EE9648ED20) to Testing_local and, on user's say-so, mods\FS25_PX150XL.zip (replaced our 2.1.0.0; hash identical). No server upload (user named local destinations only).

## 2.1.3.0 lowered pitch + cut height
2026-10-28 (Claude): User: lowered header nose too steep, not cutting (too high). px150xlWindrower.xml inputAttacherJoint: added lowerRotationOffset="10" (positive = far end/front up, AttacherJoints.lua:1798-1803 rotateAboutLocalAxis of jointTransform z), distanceToGround lower 0.4 -> 0.1 (front tilt lifts cut line ~1.756*sin10 = 0.30 m). Upper unchanged. TestRunner PASS. Source only, not zipped. UNTESTED in game. Note: COMBINE_MOWER converter cuts grain only; user's test field looked like grass.

2026-10-28 (Claude): 2.1.3.0 zipped to Testing_local only (user's say-so); hash in source/mechanical/local_build_manifest.json.

2026-10-28 (Claude): User tested 2.1.3.0: lowering presses the header into the ground and lifts the M1240 front (0.1 too low). Proposed 0.25 (between 0.4 = knife ~0.2 m high and 0.1 = pressing); user said leave it for now. Unchanged: lowerRotationOffset 10, lower 0.1.

2026-10-28 (Codex): User authorized next cutting-height test. Changed distanceToGround lower from 0.1 to 0.25 m in px150xlWindrower.xml; lowerRotationOffset remains 10 degrees, upper height remains 2.2 m. Verified XML parse and attribute readback. UNTESTED in game. Source only; no packaging or copying requested.

2026-10-28 (Codex): Built 2.1.4.0 to Testing_local/FS25_PX150XL.zip at user request (local test only). Lower height 0.25 m, lower pitch offset 10 degrees unchanged. 7 files, 12,057,472 bytes; SHA-256 9749d3c1f98854d7a9c17a0c02af33b16a8abafecd4ccc1a80ebac55e689b13e. Verified archive CRC and every entry hash against source. UNTESTED in game.
