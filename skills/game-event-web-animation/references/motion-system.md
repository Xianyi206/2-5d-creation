# Motion System

Use this reference when designing or implementing the visual effect. Values are starting ranges, not a style mandate; tune them against the actual artwork and viewport.

## Separate Four Time Scales

1. **Entrance:** a finite 1.6–2.6 second reveal that establishes depth and hierarchy.
2. **Idle:** low-amplitude loops that can run indefinitely without attracting attention away from the interface.
3. **Interaction:** damped pointer or touch response that settles instead of tracking input rigidly.
4. **Transition:** a 450–850 ms full-frame wipe, light cut, or emblem beat that hides content replacement.

Do not put every property on one timeline or start every element simultaneously. A useful entrance order is background exposure, character reveal, title, supporting copy, action, then navigation.

## Scene Graph

```text
background plate                pointer travel 2–10 px
light, fog, distant atmosphere  pointer travel 6–16 px
rear particles                  slow fall and drift
character or character rig      pointer travel 12–28 px
front particles                 larger, faster, softer
foreground frame                pointer travel 24–44 px
DOM interface                   mostly screen-locked
transition overlay              above everything
```

Use one normalized pointer target in `[-0.5, 0.5]`. Smooth toward it with exponential damping rather than a linear per-frame fraction:

```ts
const damping = 1 - Math.exp(-dt / 0.18);
current += (target - current) * damping;
```

## Character Motion Grammar

The visible result should be the sum of small local motions:

| Part | Typical motion | Starting range | Relationship |
|---|---|---:|---|
| root/body | vertical breath | 1–4 px, 3.6–6 s | leads the system |
| chest | rotate/scale | 0.25–0.9°, 0.1–0.35% | follows root |
| head | counter-rotation | 0.15–0.6° | slightly later |
| front hair | rotation/deform | 0.5–2° | short period |
| long hair ends | rotation/deform | 1.5–4° | 80–240 ms lag |
| sleeves/cloth tails | rotation/shear | 1–3°, 4–7 s | slower and heavier |
| ornaments/ribbons | rotation | 2–5° | 120–350 ms lag |
| blink | close-hold-open | 100–180 ms total | random 2.8–6.5 s gap |
| gaze | local offset | 1–3 px | sparse, not continuous |

Avoid identical sine waves. Change period, phase, amplitude, and easing across chains. Keep the torso calmer than hair tips and ornaments. Add an occasional authored accent pose rather than making the idle loop permanently busy.

For weighted meshes, let bones carry the motion and use mesh deformation to preserve volume. For rigid PNG parts, place pivots at real joints and overlap artwork enough to avoid seams.

## Static-Art Fallback

With one flattened transparent image:

- restrict scale breathing to roughly 0.15–0.35%;
- use at most about 0.3–0.8° of rotation;
- add camera parallax, rim light, fog, and foreground particles around it;
- do not claim that hair or clothing is independently animated;
- when authorized, mask out two to six high-value secondary parts before adding more global motion.

The most valuable extracted parts are usually long hair, front hair, one sleeve or cloth tail, a foreground hand/weapon, and one ornament chain.

## Responsive Composition

Measure render bounds. A practical desktop starting point is a character target width of 48–62% and target height of 58–78% of the viewport, taking the smaller scale. On narrow screens, allow deliberate horizontal crop while keeping the face below the title and above bottom navigation.

Evaluate at least these safe zones:

- title and description never cross the face;
- face and hands do not sit behind navigation or status controls;
- the main silhouette does not touch both top and bottom edges during idle;
- transition geometry overscans enough to hide aspect-ratio changes;
- mobile cropping preserves the action line and the character's visual direction.

## Performance

- Cap renderer resolution around 1.5–2 device pixels unless evidence justifies more.
- Prefer compressed WebP/AVIF plates while keeping alpha assets at a quality that avoids edge halos.
- Reuse textures and particle sprites; avoid one DOM node per particle.
- Clamp large frame deltas and pause persistent updates when the page is hidden or motion is disabled.
- Profile before promising 60 fps. Reduce particle count, filter quality, render resolution, and oversized transparent bounds in that order.
