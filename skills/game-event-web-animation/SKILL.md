---
name: game-event-web-animation
description: Design, implement, diagnose, or reproduce high-polish 2D game-event and H5 web animation with layered character art, Spine rigs, parallax scenes, particles, cinematic transitions, and responsive performance. Use for 原神式、二次元游戏大活动页、版本活动 H5、灵动角色立绘或类似网页动效复刻；do not use for ordinary marketing pages or isolated CSS micro-interactions.
---

# Game Event Web Animation

Build the illusion from many restrained, independently timed layers. Do not substitute one large whole-character scale tween for character animation.

## Boundaries

- Separate observed facts from inference when analyzing a game or reference. Extracted H5 assets can prove a web implementation, not the undisclosed engine pipeline of a game client.
- Preserve the user's chosen stack unless a change is necessary. PixiJS plus GSAP is a useful default for a new 2D event page; Spine is optional and requires suitable assets and a version-compatible runtime.
- Keep third-party IP out of this Skill. For local study, source-trace every borrowed asset and isolate it from publishable assets. Do not publish or redistribute it without rights.
- Match motion effort to source quality. A single flattened PNG can support parallax and whole-image motion, but cannot honestly reproduce independently deforming hair, clothing, face, and ornaments.
- Respect `prefers-reduced-motion`, provide a pause path for persistent motion, and keep loading failure recoverable.

## Choose the Character Path

Inspect the available source before coding:

For a flattened image that needs independent part motion, read
[references/single-image-pipeline.md](references/single-image-pipeline.md).
It provides an embedded See-through demo smoke-test adapter and the decomposition,
inpainting, rigging and evidence contracts. This branch remains experimental
and is not verified end to end; do not promise automated single-image rigging from it.

1. **Spine JSON/SKEL plus atlas:** use the matching Spine runtime and the authored animation. Read [references/spine-pipeline.md](references/spine-pipeline.md) and run the inspector before integration.
2. **Layered PSD/PNG parts:** rig body, face, front/back hair, sleeves, cloth tails, and ornaments as separate pivots or meshes. Use the motion values in [references/motion-system.md](references/motion-system.md).
3. **One transparent character image:** treat it as a fallback. Use restrained camera parallax and breathing, or derive a few authorized local study layers with masks. State the fidelity ceiling.

If a reference is available, first identify its composition, layer order, entrance beats, idle loops, interaction response, and transition grammar. If no reference exists, use a coherent original fantasy-event direction rather than copying recognizable IP design.

## Implement

Read [references/motion-system.md](references/motion-system.md) whenever building or substantially revising the effect.

- Define a normalized composition before animation: title safe zone, face safe zone, character bounds, navigation bounds, and mobile crop.
- Use a scene graph in this order: background, light/fog, rear particles, character, front particles, foreground frame, DOM interface, transition overlay.
- Run persistent scene motion from one delta-time ticker. Use GSAP or equivalent timelines for finite entrances, section transitions, and UI choreography.
- Give related parts different amplitudes, periods, and phase offsets. The root leads; hair ends, cloth, and ornaments follow later.
- Size characters from measured bounds and target screen occupancy, not raw texture dimensions. Re-layout on resize.
- Keep static and rigged modes behind one interface when comparison or fallback is valuable.
- Load heavy art before revealing the scene, show real progress when available, and recover to a static fallback if a rig fails.

## Verify

Read [references/acceptance.md](references/acceptance.md) for implementation or final delivery. A credible completion requires a production build plus real-browser evidence at desktop and mobile sizes; source existence or a clean typecheck alone is insufficient.

When a Spine JSON is available, inspect it with:

```powershell
node scripts/inspect_spine_json.mjs <path-to-skeleton.json>
```

Use the reported animation duration, animated-bone count, weighted-mesh count, and constraint types to decide what the source can actually do. Do not infer physics or facial animation that the data does not contain.
