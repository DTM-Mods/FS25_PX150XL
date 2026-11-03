# PX150 XL 2.5.1.0 offline deep audit — 2026-11-02 (Codex)

Scope: working runtime source, installed ZIP, installed game's readable Lua source and loose base-game XML, current and archived local logs. No game controls, screenshots, session changes, mod installation, packaging, upload or runtime fixes. The user clarified that the running game must remain untouched.

Follow-up 2026-11-02 (Codex): this report describes the original audit. The user subsequently authorized the Vehicle.lua declaration fix and stale clearance-event correction in working source. See ../clearance_network_fix/STATUS.md for implementation and verification. test_native.py/native_results.json now exercise current source, including detached-event rejection, and report the two source/installed differences; original audit findings below remain historical evidence.

## Findings

### 1. Confirmed runtime load error: inherited Vehicle.lua resolves inside the mod

Current log.txt line 485:

`Error: Can't load resource 'C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/mods/FS25_PX150XL/dataS/scripts/vehicles/Vehicle.lua'.`

Six log files identifying version 2.5.1.0 contain this error (including the current log). See log_evidence.json.

modDesc.xml declares `<type name="px150Windrower" parent="mower">` without an explicit className or filename. Native TypeManager.loadTypeFromXML takes the parent's className/filename (lines 143–147), passes the filename through Utils.getFilename with modDir (158), then addType calls source(filename, customEnvironment) (95). The log establishes the actual engine resolution into the mod directory. The runtime archive contains no such resource. Utils.getFilename is an engine binding with an empty Lua declaration in this source export; its implementation was not guessed or replaced as evidence.

Severity: confirmed startup error, not a proven complete vehicle failure. The same log subsequently registers the type and loads the header I3D. TestRunner does not catch it. A correction should explicitly preserve the base Vehicle class and resolve its source from the game; it must be validated against native resolution before shipping. No correction applied in this audit.

### 2. Confirmed animation data defects: two 27 mm discontinuities

px150xlWindrower.xml, knifeAnimation, at t=0.5:

| Node | Previous endTrans Z | Next startTrans Z | Difference |
|---|---:|---:|---:|
| canolaKnifesRight01 | -0.085 m | -0.058 m | +0.027 m |
| canolaKnifesRight02 | +0.085 m | +0.058 m | -0.027 m |

The consecutive keyframes disagree at the shared time. Both mismatches also occur in the installed base-game headerHD50F.xml: these were inherited. This confirms inconsistent animation data, not the precise rendered appearance at that boundary. The animation runs at speedScale=8 when turned on. Visual severity was not tested.

### 3. Reproduced conditional network lifecycle risk: stale clearance event

PX150ClearanceEvent.run checks only that the sender is the server and the vehicle exists. It does not verify attachment, carrier identity, or attachment generation. It creates px150Clearance and calls C.apply even after onPreDetach has cleared the fit state. C.apply can change the detached header's input joint before finding that there is no carrier.

test_native.py delivers a server-origin event to a detached header with an available input joint: lowerDistanceToGround changes from 0.30 to 0.60 m. Non-server-origin events are correctly ignored. The ordinary stream/reattach tests also pass.

Classification: confirmed behavior under the supplied ordering, potential multiplayer defect. Actual occurrence depends on event/detachment ordering; no live multiplayer reproduction or packet ordering claim. A robust correction would tie fit events to the current attachment and handle initial join data separately.

## Verified behavior and boundaries

- Installed mods/FS25_PX150XL.zip: 10 entries, CRC clean, root modDesc.xml, forward slash entry names; every entry equals working source byte for byte. SHA-256: `7f199f478980b7b1c380c94d0c2ad393c4fd6dd79b5bf17401ea95931259b044`.
- Fresh GIANTS TestRunner 0.9.23 run: all 13 non-GUI modules succeed. EditorCheck and ShaderCheckEditor explicitly SKIPPED, despite the tool reporting SUCCESS for those skipped modules. The tool's update check could not connect; installed validation still completed.
- All three runtime Lua scripts compile/load under Lua 5.1 with required engine globals stubbed.
- Existing test_yield_bonus.py and test_lowered_clearance.py pass. These include converter isolation, non-unit/map factors, numerical fitting, bounded fallback, temporary-node cleanup, stream/reattach reference handling and detach reset. They do not simulate actual game physics.
- New test_native.py executes the game's actual Mower.processMowerArea, AttacherJoints.calculateAttacherJointMoveUpperLowerAlpha, and AttacherJoints.updateAttacherJointRotation functions. Density, transform, engine and network boundaries are controlled stubs; the tested game Lua functions themselves are unchanged.
- Native mower calculation produces exactly 1.10 times the baseline liters on server and nearby client for the controlled input, preserves shared map factors, and respects the distant-client early return.
- Native attachment functions consume fitted distance/angle correctly. C.apply marks the joint frame invalid. This does not establish actual collision clearance or carrier stability.
- Shop script changes dynamic bodies to kinematic only for showroom objects; purchased/non-showroom objects and static bodies are preserved in the controlled test.
- All 109 unique vehicle I3D mappings resolve into the current scene. Explicit runtime filename/texture/external-shapes/image attributes resolve, including loose $data assets and the native PNG-to-DDS fallback used by the shop image.
- Archived 2.5.1.0 logs contain eight successful calibration messages, e.g. lower=0.2384 m / offset=16.087 degrees; no PX150 calibration warnings in the scanned matching-version logs. These messages report solver outputs, not measured physical clearance. Current log alone does not show calibration.
- Current log's repeated FarmInventory.lua:538 `sptOwner` update failures identify another mod. They are not assigned to PX150XL. Other mods' deprecated configuration API errors are likewise not attributed to this mod without evidence.

Native boundary limitation: Mower.processMowerArea caps each pending drop buffer at 1000 L. A controlled large-input test reproduces truncation (1031.25 calculated -> 1000 buffered). This is native game behavior, not evidence that ordinary PX150 operation loses yield. A fixed +10% conversion factor does not guarantee +10% ground-deposited/picked-up liters under buffer saturation or other density limits.

Translation quality: px150_functionWindrower, px150_turnOn and px150_turnOff have English text only. This is incomplete German localization; it is not a missing English key or a demonstrated runtime failure.

## Not established by this audit

Rendered geometry, shader compilation, binary mesh integrity inside the engine, measured ground clearance on changing terrain, collision stability, actual shop controls, purchase/save/reload, crop-density/ground deposition and PW8 pickup in the engine, AI operation, other-mod interaction and live multiplayer timing. The encrypted MacDon DLC was not extracted. No assertion that every possible error has been found: these are the findings from the stated executable checks and source review.

## Re-run

From the project root:

```
python source/validation/test_yield_bonus.py
python source/validation/test_lowered_clearance.py
python source/validation/deep_20261102/test_native.py
```

Native function snapshots used by test_native.py are under gameSource/, read from profile/debugger/gameSource.zip. Results are native_results.json. TestRunner output and log evidence are retained beside this report. This audit added only validation artifacts; runtime files remain unchanged.
