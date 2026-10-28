# Deferred repairs - PX150 XL

## Rear bracket cross tube and floating branding
2026-10-28 (Codex), requested by user after inspecting in-game screenshots of version 2.1.0.0.

**DEFERRED: user explicitly said not to fix this now.**

- Add one square steel cross tube spanning from the left rear bracket/brace to the right rear bracket/brace.
- Tube must run behind the top hitch point and connect the two braces, giving the upper hitch assembly solid support.
- In-game screenshots show the top silver hitch assembly hanging unsupported between the braces; the PropaineX name is also floating in open space (and reads reversed from the carrier side).
- Mount the top hitch and PropaineX branding on the cross tube so they are physically supported; check text faces the intended viewing side.
- Preserve existing bracket pin positions and M1240 mechanical attachment unless the user requests otherwise.
- Show a before/after preview in the VS Code editor pane when this repair is resumed.

Current active task: improve the shop/store picture. Do not include this structural repair in that image-only fix.

## Resumed for mock-up
2026-10-28 (Codex): User explicitly resumed the crossbar repair after approving the full revised store-card mock-up. Preview created in previews/crossbar_v1/. Proposed square tube is 160x160mm, spans2.548m between brace centers, 3mm edge bevel; center native i3d(0,1.24,-1.24). PropaineX text sits on rear tube face. Actual runtime main geometry used for preview. Runtime and ZIP remain unchanged pending preview review. Approved store picture must stay as approved.

## Done
2026-10-28 (Claude): Crossbar integrated into runtime as 2.1.2.0 (see MECHANICAL_STATUS.md).

## End caps in MacDon colour
2026-10-28 (Claude): **DEFERRED: user said not to worry about the colour right now.** Wanted: end caps painted MacDon colour to match. Caps share headerHD50F_vis material with the frame, so faces must be split onto a new material. Colour source not chosen (probe mod read of M1240 or user screenshot). Preview before/after first.
