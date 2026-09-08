# Spine Pipeline

Read this reference only when the source includes a Spine skeleton and atlas or when deciding whether Spine is appropriate.

## Inspect Before Integrating

Run `scripts/inspect_spine_json.mjs` on JSON skeletons. Record:

- Spine editor version;
- skeleton bounds;
- bones, slots, constraints, and skins;
- region versus mesh attachments and how many meshes are weighted;
- animation names, durations, animated bones, and timeline keyframes;
- whether physics constraints, deform timelines, slot timelines, or events exist.

These facts determine what the asset can reproduce. Many bones do not guarantee good motion; they only expose control points. A model with no physics constraint should not be described as physics-driven.

## Version and Atlas Rules

- Match the Spine Runtime **major.minor** to the export version. A 4.2 skeleton needs a 4.2 runtime; do not silently use the latest 4.3 runtime.
- Confirm whether the atlas is premultiplied alpha (PMA) or non-PMA and keep the export/runtime texture settings consistent.
- Keep `.json` or `.skel`, `.atlas`, and referenced texture pages together unless atlas URLs are rewritten deliberately.
- Treat texture bounds as a performance concern. Trim transparent padding before lowering visual quality.

## PixiJS 8 Pattern

For a Spine 4.2 source with PixiJS 8, use the compatible `@esotericsoftware/spine-pixi-v8` 4.2 line:

```ts
import { Assets } from "pixi.js";
import { AABBRectangleBoundsProvider, Spine } from "@esotericsoftware/spine-pixi-v8";

Assets.add({ alias: "character-data", src: "/character/character.json" });
Assets.add({ alias: "character-atlas", src: "/character/character.atlas" });
await Assets.load(["character-data", "character-atlas"]);

const character = Spine.from({
  skeleton: "character-data",
  atlas: "character-atlas",
  autoUpdate: false,
  boundsProvider: new AABBRectangleBoundsProvider(x, y, width, height),
});

character.state.setAnimation(0, animationName, true);
character.update(0);
```

Drive `character.update(dt)` from the application's single ticker. Skip the update when persistent motion is paused. This keeps the rig synchronized with scene motion and avoids competing tickers.

Calculate layout from the inspected skeleton bounds:

```ts
const scale = Math.min(targetWidth / bounds.width, targetHeight / bounds.height);
group.pivot.set(bounds.x + bounds.width / 2, bounds.y + bounds.height / 2);
group.scale.set(scale);
group.position.set(targetX, targetY);
```

Test the actual animation frame because dynamic attachments can exceed setup-pose bounds. Use a stable bounds provider when layout jitter would be visible.

## Runtime Behavior

- Use authored animation mixing for state changes; do not restart a looping idle on every UI interaction.
- Let the skeleton own local character motion. Add only minimal group-level camera parallax or rotation.
- If the model contains physics constraints, configure their authored parameters rather than layering unrelated sine waves over the same bones.
- If the model lacks blink or face tracks, add them only when the source rig exposes appropriate bones or slots and the art supports it.
- Keep a static-art fallback and report a recoverable warning if skeleton or atlas loading fails.

## Rights and Distribution

Spine Runtime evaluation and redistribution are not the same permission. Before publishing, review the current Esoteric Software runtime license and confirm the integrator's license position. Separately confirm rights for the skeleton, atlas textures, character, and source event. Local-study permission does not imply permission to upload a built site.

Store borrowed study assets under an explicitly named third-party directory and include a source record with original URL, owner, model version, use boundary, and retrieval date. Do not copy borrowed models into this Skill.
