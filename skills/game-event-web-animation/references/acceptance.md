# Acceptance and Evidence

Use this checklist for an implementation or substantial revision. Adapt commands to the project's existing stack.

## Functional

- The loader reaches completion and the interface becomes usable.
- The intended animation exists and loops without a visible reset pop.
- Section changes cannot overlap into a corrupted state.
- Motion pause or `prefers-reduced-motion` stops or substantially reduces persistent movement.
- A rig-loading failure falls back to a usable static character.
- Keyboard focus remains visible and controls have accessible names.

## Visual

Capture settled frames at, at minimum:

- 1440 × 900 desktop;
- 390 × 844 mobile.

Check title/face/navigation collisions, deliberate crop, foreground occlusion, contrast, and transition overscan. Compare a rigged frame with a paused or static frame when character liveliness is part of the task. Subjective art-direction acceptance remains with the user.

## Runtime and Build

- Run the repository's typecheck, lint, tests, and production build that apply.
- Inspect browser console errors and failed network requests.
- Confirm document `scrollWidth` and `scrollHeight` do not exceed the viewport for a full-screen experience.
- Exercise resize after load; do not verify only a fresh page at each size.
- Check that animation time uses delta seconds and clamps long frames.
- Note the delivered asset and bundle sizes. Do not promise a frame rate without profiling on representative hardware.

## Motion Quality

Watch at least one complete idle cycle and several transition repetitions:

- no shared mechanical cadence across every secondary part;
- no seam exposure between layered PNG parts;
- no mesh collapse or texture squares;
- no one-frame flash at animation loop boundaries;
- no large whole-character breathing that competes with the title;
- particles do not form obvious synchronized rows or reset together.

## Delivery Receipt

Report:

- what character path was used and why;
- source and rights boundary for every non-original asset;
- key implementation files;
- build and browser evidence actually observed;
- remaining uncertainty, especially undisclosed reference technology or subjective fidelity;
- how to run the local result and how to remove borrowed study assets before publication.
