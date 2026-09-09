# Single-image character pipeline

Use when the input is a flattened character illustration and the requested
motion requires independently moving components. The embedded remote adapter
currently supports only an official public demo sample. It is a smoke-test
adapter, not a verified end-to-end character creator.

## Current evidence boundary

The adapter has local contract tests for continuous queue handling, terminal
errors, local-only polling and explicit credential selection. These tests use
synthetic responses, not live inference. No end-to-end PSD decomposition,
generated layer validation, rigging or animated render is claimed by this
distribution. Authenticated inference is also unverified.

Keep a single raw queue stream open and preserve the full process_completed
error. A disconnected queue session is not assumed resumable. Endpoint
availability, authentication, API shape and compute allowance must be checked
against the service when it is actually used; this package makes no claim about
current public quota or service availability.

Do not describe this branch as validated image-to-puppet automation. Existing
Spine playback is a separate capability with a different input requirement.

## Embedded code versus external dependencies

Keep small adapters, output schemas, validation and preview code in `scripts/`
and `assets/`. Keep model weights and isolated Python environments in a chosen
external cache/workspace. Pin upstream revisions when acquiring them; record
versions and licenses. Avoid silently installing into the agent's own runtime.
Remote inference requires an available endpoint and permission to send the
chosen image; a public example needs no access to local user images.

Relevant upstreams:

- Decomposition: https://github.com/shitagaki-lab/see-through
- Official hosted demo: https://huggingface.co/spaces/24yearsold/see-through-demo
- Candidate downstream rigging: https://github.com/Wzhang3912/image2live2d
- Broader scene-layer decomposition: https://github.com/QwenLM/Qwen-Image-Layered

The downstream converter and local model execution have not been tested here.
Consult their current interfaces before integrating them; do not assume their
export formats can be read by Spine. Live2D, nijilive and Spine need different
runtimes or explicit conversion.

## Sample smoke test

From this skill's folder, choose a fresh external output directory:

```text
python scripts/seethrough_remote.py probe --out <test-directory>
python scripts/seethrough_remote.py run-sample --out <test-directory>
python scripts/seethrough_remote.py poll --out <test-directory>
```

Launch `run-sample` through the environment's background-runner mechanism: it
keeps its SSE connection open for up to five minutes and has a 45s socket timeout
(server heartbeats are normally 15s). On Windows use the governed isolated runner
and pass the intended Python executable by absolute path, since a background
worker's `python` may resolve to a different environment.

The commands use the Python standard library, fixed official endpoint, 768px
resolution, seed 42 and left/right limb splitting. Submission uses the service's
own sample. `poll` reads only the local job receipt and never connects to Gradio.
No command automatically retries a failed inference. Exit 2 means failure.
Credentials are used only when an environment-variable name is explicitly supplied
with `--hf-token-env HF_TOKEN`; the token is never saved to receipts. On Windows,
the explicitly selected variable is read from the process first, then the User
environment, allowing newly saved credentials without restarting the agent.
User environment variables are not encrypted secret storage. Redirects are
rejected to avoid forwarding authorization to another destination. Authenticated
inference has not yet been tested. Quota/authentication errors require a legitimate
available allowance or credential, not session rotation or repeated submission.

`RESULT_READY` only means a result descriptor was received. Downloading the PSD,
verifying its contents and producing a working rig are separate steps. Keep
`probe.json`, `job.json`, `events.jsonl`, and `result.json` as evidence, outside
the skill. A job ID or heartbeat is not successful decomposition.

## Full workflow when a working backend is available

1. Inspect the image and intended motion. Identify visible joints, front/back
   relations, flexible versus rigid parts, and occluded regions. Label inferred
   structure explicitly. A depth map does not recover a full 3D body.
2. Select decomposition granularity based on intended motion. Hair, face,
   sleeves, hands and ornaments may need extra subdivision beyond semantic
   model classes. Require independently completed hidden regions.
3. Export ordered RGBA layers plus metadata: source image hash, canvas size,
   pixel offsets, semantic role, draw order, parent, pivot and motion limits.
   Separate backend-provided depth/order from agent-assigned values.
4. Recompose the layers at rest and compare with the original. Inspect facial
   identity, silhouettes, dropped accessories, alpha edges and inpainted areas.
5. Generate/import deformation meshes and rig parameters. Move one component
   at a time through its intended range; check attachment gaps, texture stretch,
   triangle inversion and occlusion ordering. Decomposition alone is not rigging.
6. Drive the complete rig, then integrate it with the scene and use the existing
   browser acceptance checks. Preserve the original view and a bare-rig view
   for comparison. If only whole layers translate/rotate, call that a rigid-layer
   preview, not a weighted-mesh or physics result.

Report each boundary separately: backend reachable, decomposition returned,
layers visually accepted, local articulation accepted, combined motion accepted,
browser integration accepted. Claim only steps actually exercised.

Transport reference: Gradio 6.12.0 `queue_data_helper` and `simple_predict_get`,
https://github.com/gradio-app/gradio/blob/gradio%406.12.0/gradio/routes.py .
Use the full queue API when the simple API collapses server errors to null.
