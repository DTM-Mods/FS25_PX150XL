# PX150 clearance network correction — 2026-11-02 (Codex)

User authorized fixing the stale clearance-event case identified in the offline audit.

Runtime change: scripts/PX150LoweredClearance.lua only. The previously authorized modDesc.xml Vehicle.lua correction remains present. No model, crop factor, solver target, mass, paint or animation changes.

- A counter identifies each attachment lifecycle; onPreAttach starts it and onPreDetach immediately invalidates it. Native Attachable.preAttach sets the active input joint before raising onPreAttach; this avoids counting smooth-attach completions at different times on different peers.
- Fit events carry the carrier, carrier joint index, input joint index and lifecycle counter. Apply only if the current attachment matches every field and the carrier still has this implement. Events never create detached state or queue a pose for a future attachment.
- Initial object streams synchronize the authoritative counter, attached identity and optional fitted pose. If native attachment reconstruction follows the stream, a matching initial snapshot is consumed once; detach clears it. Ordinary event packets cannot use that deferred path.
- Detach restores original height and pitch. Calibration math is unchanged; server update still calculates once and sends a bound fit event.

Validation PASS:

1. test_clearance_network.py: current fit, client-origin rejection, detached stale packet, same-carrier/same-joint reattach, different carrier, wrong input/joint, missing carrier/vehicle, full event serialization, authoritative counter sync for joining clients, next attachment after join, initial stream before or after reconstruction, unfitted/detached stream, original-setting restoration, and single server calibration/broadcast.
2. test_lowered_clearance.py: solver/front reference/5 cm target/bounds/fallback/temporary-node cleanup. Its old lifecycle mocks moved to the stronger network test above.
3. test_yield_bonus.py: 10% factor and shared converter isolation.
4. Updated deep audit native harness: actual game mower and attachment functions, Lua 5.1 load, references, 109 mappings and showroom guard pass. It now reports source changes separately from the installed ZIP and checks rejection of detached events.
5. GIANTS TestRunner: all 13 non-GUI modules PASS on a validation-only runtime mirror. EditorCheck/ShaderCheckEditor explicitly skipped. XML/I3D parses and exact runtime diff reviewed.

Offline tests use engine/network stubs; real multiplayer timing, initial object-reference availability and engine physics remain UNTESTED. A missing carrier reference is rejected rather than allowing an unbound update. The custom event/object-stream layout changed; server and clients must use the same rebuilt mod. No mixed-version compatibility is claimed.

Source only. No new ZIP, installation, upload or interaction with the running game. Version remains 2.5.1.0 pending the next explicitly requested build; bump before packaging. The runtime mirror here is a checker input, not an installation.
