# John Deere HD50F working source

2026-10-28 (Codex): Copied the installed base-game HD50F into this project at the user's request. Original game files unchanged. Prior project removed; Bracket_Information retained.

Source: G:/SteamLibrary/steamapps/common/Farming Simulator 25/data/vehicles/johnDeere/headerHD50F/

Complete header folder copied, including I3D, binary shapes (copied without decoding), XML, DDS textures and shop image. Additional vehicle-specific textures referenced by the model were copied into textures/ and the model references localized. XML now opens the local model and shop image. Standard game shaders, detail-library materials, wheels, lights, sounds and combine shop combinations retain their $data references; these are engine/shared assets, not a separate header model dependency.

Verified: XML and I3D parse, all localized vehicle textures exist, copied shapes SHA-256 matches the installed original. Appearance/behavior unchanged intentionally; UNTESTED in game and GIANTS Editor. No modDesc or ZIP created yet.

Original working width 15.2 m, type cutter, mass 4700 kg, one physics component. Start future mounting work from this model, not the deleted FD250.
