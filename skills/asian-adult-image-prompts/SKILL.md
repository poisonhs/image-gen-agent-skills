---
name: asian-adult-image-prompts
description: Use when creating or refining adult-only, Asian-inspired editorial or boudoir image prompts from the bundled nsfw-prompt-templates-asian reference collection, especially when the request needs consistent scene, composition, wardrobe, lighting, pose, and visual-style choices.
license: MIT
compatibility: Markdown references only, no runtime dependencies. Adult content for fictional, consenting adult subjects only.
metadata:
  version: 2.0.0
  source: nsfw-prompt-templates-asian
  adult_only: true
---

# Asian Adult Image Prompts

Create coherent, adult-only image prompts from the bundled modular Asian visual-prompt collection. Extract only the details needed for the user's request; do not paste source passages into the response.


## Load References

Read `references/upstream/README.md` first, then load only the modules relevant to the request. See [source-map.md](references/source-map.md) for the pinned source revision and attribution details.

Do not load the whole collection for a simple request. Start with these files under `references/upstream/`:

| Need | Read |
| --- | --- |
| Scenario and narrative | `01-场景主题.md` |
| Shot, lens, device, composition | `02-景别构图.md` |
| Wardrobe and coverage | `03-裸露液体.md`, `04-服装专项.md` |
| Lighting and mood | `05-光影氛围.md` |
| Pose and expression | `06-姿势动作.md`, `07-表情眼神.md` |
| Film, makeup, hair, texture, props, persona | `08` through `14` as needed |

## Compose

1. Extract only choices that fit the user brief. Resolve contradictions before writing, such as a phone-camera look paired with high-end cinema wording, or incompatible clothing and coverage states.
2. Use one primary visual idea. Add at most three to five supporting details; do not turn every module into a tag dump.
3. Assemble the English prompt in this order: subject and adult status, scene, composition/camera, wardrobe and coverage, pose/action, expression, lighting, then optional style/details.
4. Keep the image prompt between 80 and 150 English words unless the user specifies another limit. Prefer concrete visual language over abstract mood labels.
5. Include a short negative prompt only when the target model supports it. Focus it on image defects and composition problems, not on a second scene.

## Output Format

Return exactly the requested format. When the user does not specify one, use:

```text
Brief: <one Chinese sentence>

Prompt:
<English image prompt>

Negative prompt:
<optional, model-agnostic exclusions>
```

Mention any material assumption in `Brief`. Do not expose a long chain of reasoning or copy large passages from the reference collection.

## Common Errors

| Error | Correction |
| --- | --- |
| Mixing incompatible camera quality signals | Match image quality language to the stated device or remove the device. |
| Contradictory wardrobe and coverage | Select one coherent state and describe it once. |
| Generic words such as `cinematic` or `sexy` doing all the work | Add a specific lens, light direction, material, posture, or expression. |
| Unclear age or consent | Stop and request confirmation of a fictional, consenting adult subject. |
| Copying the source repository into the response | Extract only the needed choices; do not reproduce source passages. |
