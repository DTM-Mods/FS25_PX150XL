# PX150 XL Windrower Pro Edition

Farming Simulator 25 windrower project by PropaineX, for the MacDon M1240. Requires the MacDon Pack.

Current build: **2.1.4.0**. Working width: 15.2 m. Mass: 2.95 t.

The lowered attachment height is set to **0.25 m**, with a **10 degree lower rotation offset**. The offset is not a measured angle relative to the ground. This height adjustment still needs in-game testing.

## Project contents

- Root XML, I3D and DDS files: runtime files and preserved header references.
- `source/`: build tools, integration work, mechanical snapshots and validation reports.
- `previews/`: visual previews and preserved Blender scenes.
- `Bracket_Information/`: mount-kit references and scripts.
- `MECHANICAL_STATUS.md`: detailed project and test history.

## Packaging

Run `python source/mechanical/package_local.py` to build `FS25_PX150XL.zip` in the sibling profile's `Testing_local` folder. The script collects runtime dependencies and verifies archive integrity and each file against the source. It excludes development files from the ZIP.

This repository includes development materials; do not ZIP the entire repository for installation. Referenced base-game files are provided by the game installation.
