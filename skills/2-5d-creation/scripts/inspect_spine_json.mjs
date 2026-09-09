#!/usr/bin/env node

import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

const input = process.argv[2];
if (!input || input === "-h" || input === "--help") {
  console.log("Usage: node inspect_spine_json.mjs <skeleton.json>");
  process.exit(input ? 0 : 2);
}

const file = resolve(input);

const countObject = (value) => value && typeof value === "object" ? Object.keys(value).length : 0;

const maxTimelineTime = (value) => {
  let maximum = 0;
  const visit = (entry) => {
    if (Array.isArray(entry)) {
      for (const item of entry) visit(item);
      return;
    }
    if (!entry || typeof entry !== "object") return;
    if (typeof entry.time === "number") maximum = Math.max(maximum, entry.time);
    for (const child of Object.values(entry)) visit(child);
  };
  visit(value);
  return maximum;
};

const countTimelineFrames = (value) => {
  let count = 0;
  const visit = (entry) => {
    if (Array.isArray(entry)) {
      if (entry.length === 0 || entry.every((item) => item && typeof item === "object" && !Array.isArray(item))) {
        count += entry.length;
      } else {
        for (const item of entry) visit(item);
      }
      return;
    }
    if (!entry || typeof entry !== "object") return;
    for (const child of Object.values(entry)) visit(child);
  };
  visit(value);
  return count;
};

const normalizeSkins = (skins) => {
  if (Array.isArray(skins)) return skins;
  if (!skins || typeof skins !== "object") return [];
  return Object.entries(skins).map(([name, attachments]) => ({ name, attachments }));
};

const countAttachments = (skins) => {
  const types = {};
  let attachments = 0;
  let weightedMeshes = 0;

  for (const skin of normalizeSkins(skins)) {
    const slotMap = skin.attachments ?? skin;
    for (const slot of Object.values(slotMap ?? {})) {
      if (!slot || typeof slot !== "object") continue;
      for (const attachment of Object.values(slot)) {
        if (!attachment || typeof attachment !== "object") continue;
        const type = attachment.type ?? "region";
        types[type] = (types[type] ?? 0) + 1;
        attachments += 1;
        if (
          type === "mesh" &&
          Array.isArray(attachment.vertices) &&
          Array.isArray(attachment.uvs) &&
          attachment.vertices.length !== attachment.uvs.length
        ) weightedMeshes += 1;
      }
    }
  }

  return { attachments, attachmentTypes: types, weightedMeshes };
};

const summarizeAnimation = (name, animation) => ({
  name,
  durationSeconds: maxTimelineTime(animation),
  animatedBones: countObject(animation.bones),
  animatedSlots: countObject(animation.slots),
  transformConstraints: countObject(animation.transform),
  physicsConstraints: countObject(animation.physics),
  deformSkins: countObject(animation.deform),
  drawOrderFrames: Array.isArray(animation.draworder) ? animation.draworder.length : 0,
  eventFrames: Array.isArray(animation.events) ? animation.events.length : 0,
  timelineFrames: countTimelineFrames(animation),
});

try {
  const skeleton = JSON.parse(await readFile(file, "utf8"));
  const animations = Object.entries(skeleton.animations ?? {}).map(([name, animation]) =>
    summarizeAnimation(name, animation),
  );
  const bounds = skeleton.skeleton
    ? {
        x: skeleton.skeleton.x ?? 0,
        y: skeleton.skeleton.y ?? 0,
        width: skeleton.skeleton.width ?? 0,
        height: skeleton.skeleton.height ?? 0,
      }
    : undefined;

  console.log(JSON.stringify({
    file,
    spineVersion: skeleton.skeleton?.spine ?? null,
    bounds,
    bones: Array.isArray(skeleton.bones) ? skeleton.bones.length : 0,
    slots: Array.isArray(skeleton.slots) ? skeleton.slots.length : 0,
    skins: normalizeSkins(skeleton.skins).length,
    ikConstraints: Array.isArray(skeleton.ik) ? skeleton.ik.length : 0,
    transformConstraints: Array.isArray(skeleton.transform) ? skeleton.transform.length : 0,
    pathConstraints: Array.isArray(skeleton.path) ? skeleton.path.length : 0,
    physicsConstraints: Array.isArray(skeleton.physics) ? skeleton.physics.length : 0,
    ...countAttachments(skeleton.skins),
    animations,
  }, null, 2));
} catch (error) {
  console.error(`Failed to inspect Spine JSON: ${error.message}`);
  process.exit(1);
}
