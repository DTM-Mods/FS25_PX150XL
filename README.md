# PX150 XL Windrower Pro Edition

Farming Simulator 25 windrower project by PropaineX, for the MacDon M1240. Requires the MacDon Pack.

Current source: **2.5.2.0**. Working width: 15.2 m. Mass: 2.45 t.

2.5.2.0 corrects the base Vehicle.lua source path and binds multiplayer clearance updates to the current attachment. Offline network lifecycle, native-function and numerical tests pass; live multiplayer remains unverified. Built to Testing_local/FS25_PX150XL.zip only; all 10 runtime entries verified against source, ZIP CRC/layout passed, and all 13 non-GUI TestRunner modules passed (2 GUI modules skipped).

The lowered attachment height is set to **0.30 m**, with a **10 degree lower rotation offset**. The user confirmed this height works in game. The offset is not a measured angle relative to the ground.

This header includes a fixed **25% yield bonus on alfalfa, clover and field grass only** (alfalfa/clover only since 2.7.5.0, 15% since 2.7.6.0, field grass added and 25% since 2.8.2.0), applied to its own copies of those crops' conversion records; every other crop keeps the map's factor. Field grass gets the bonus on top of its grain-row amount. Alfalfa and clover are only cut on maps that add them to the COMBINE_MOWER converter (for example NF Marsch). Other implements retain their existing factors. The bonus has passed Lua isolation and calculation tests; in-game yield testing is pending.

## Project contents

- Root XML, I3D and DDS files: runtime files and preserved header references.
- `source/`: build tools, integration work, mechanical snapshots and validation reports.
- `previews/`: visual previews and preserved Blender scenes.
- `Bracket_Information/`: mount-kit references and scripts.
- `MECHANICAL_STATUS.md`: detailed project and test history.

## Packaging

Run `python source/mechanical/package_local.py` to build `FS25_PX150XL.zip` in the sibling profile's `Testing_local` folder. The script collects runtime dependencies and verifies archive integrity and each file against the source. It excludes development files from the ZIP.

This repository includes development materials; do not ZIP the entire repository for installation. Referenced base-game files are provided by the game installation.

Accessories and trim (2.4.0.0): one $250 shop color option uses the full native palette to change both end-cap stickers and the custom MacDon mounting bracket, sockets and upper hitch together; pins and keeper clips stay metallic steel. Default native MacDon Red; PropaineX orange remains selectable. Black model-number stripes, lettering, reel discs and other header materials stay fixed. TestRunner and compiled-model material isolation checks passed; shop interaction not yet tested in game.

Workflow terminology: "build it" approves and integrates changes into the working source/model used for future previews and edits. "Zip it" separately requests packaging. Current visual baseline: `previews/macdon_red_default_v1/macdon_red_default_preview.blend` (native MacDon red trim, corrected right-hand lettering, fixed steel pins and black reel discs); runtime source is authoritative for mechanics and shop configuration.

Lowered clearance (2.5.0.0): the existing 0.30 m / 10-degree configuration remains the reference for the front cutting height. A server-side fit adjusts native lift and pitch together for a 5 cm lowest rear-socket target on the attachment terrain, using temporary copies of the current carrier joint geometry. This runs once after stationary attachment, retains the original setup if no bounded solution exists, and does not continuously track changing terrain. Numerical/lifecycle tests and GIANTS TestRunner pass; physical M1240 behavior and actual clearance still require in-game testing.

Local testing ZIP: 2.5.1.0, 10 runtime files. Includes 2,450 kg mass, showroom placement/stability correction, centered right-end lettering and native MacDon Red default/palette entry. GIANTS TestRunner passes all modules, including EditorCheck and ShaderCheckEditor. ZIP CRC and every entry SHA-256 match source. Physical lowered-clearance and showroom behavior still require in-game verification.
