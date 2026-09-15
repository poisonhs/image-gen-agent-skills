---
name: z-image-generation
description: Use when the user wants a free AI-generated image (生图, zimage, Z-Image, concept art, illustration, avatar) with no API key. Generates a PNG through the HuggingFace Z-Image-Turbo Space using a standard-library-only Python CLI, and saves it locally.
license: MIT
compatibility: Requires Python 3.8+ (standard library only) and network access to huggingface.co. Optional HuggingFace read token in ~/.hf_token raises the shared ZeroGPU quota.
allowed-tools: Bash(python3:*) Read
metadata:
  version: 1.0.0
  author: ali
  platforms: [linux, macos, windows]
  hermes:
    tags: [image-generation, zimage, huggingface, gradio, free]
---

# Z-Image Generation

Free, no-registration AI image generation via the official Z-Image-Turbo Space (`mrfakename/Z-Image-Turbo`, the backend behind zimage.design). 1024×1024 images in ~20s, no API key needed.

## When to Use

- User asks to generate/create/make an image and mentions zimage.design, Z-Image, or just wants a free AI image (zimage 生图 / 调用这个网站生图).
- Any task needing a quick free AI-generated image (social posts, concept art, avatars, illustrations).
- NOT for: paid/fast enterprise image gen, video, or local model inference.

## Usage

Run the script with a prompt:

```bash
python scripts/zimage.py "a red-haired girl in watercolor style, cherry blossoms falling, soft light" 
```

Image is saved to an output directory (default `./zimage_output`) and the absolute path is printed. Display the PNG to the user.

### Options

```bash
python scripts/zimage.py "prompt" \
  --width 1024 --height 1024 \   # 512-2048
  --steps 12 \                   # 1-20, default 9 (lower = faster)
  --seed 42 \                    # fixed seed = reproducible; omit for random
  --token hf_xxx \               # optional: HF token for larger ZeroGPU quota
  --out-dir ./my_images \
  --timeout 300                  # SSE poll timeout; Space can cold-start 30s-2min
```

- Fix the seed to reproduce the exact same image: `--seed 12345`.
- Random seed (default) gives a different image each run; the seed used is printed alongside the image path.
- **HF token (recommended when the Space is busy)**: set `HF_TOKEN` env or pass `--token hf_xxx`, or store the token in `~/.hf_token` (chmod 600, read automatically). Create a Read token at https://huggingface.co/settings/tokens. The public Space has a shared free ZeroGPU quota that frequently runs out (`ZeroGPU quota exceeded` error event); authentication gets a larger quota and much more reliable generation. Note: ZeroGPU quota is shared across ALL Spaces per caller (IP/account) — switching to another Z-Image Space does NOT bypass it; only an authenticated token does.

## How It Works

1. POST `https://mrfakename-z-image-turbo.hf.space/gradio_api/call/generate_image` with `{"data": [prompt, width, height, steps, seed, randomize]}` → returns an `event_id`.
2. Poll the SSE stream `.../call/generate_image/{event_id}` until `event: complete`.
3. Download the resulting PNG.

The script uses only the Python standard library — no third-party dependencies, works on any machine with Python 3.8+.

## Pitfalls

- **Cold start**: the free Space sleeps when idle; the first call may take 30s–2min. Increase `--timeout` if it fails. If you get a connection error or `{"error": ...}`, wait and retry once. The SSE stream can also end without a `complete` event when the Space is waking up mid-request — just re-run the same command (the script re-submits).
- **Rate limits**: free GPU quota is shared. Do not hammer it — 1–3s between bulk requests. Heavy abuse may get the public Space blocked.
- **Long waits**: for big resolutions or when the Space is cold, run the command in the background with a large `--timeout` (e.g. 600) so the poll isn't cut off.
- **Resolution**: 512–2048. Default 1024×1024. Steps 1–20 (default 9); low steps are faster, higher steps slightly better quality.
- **English prompts** generally render text better; the model supports Chinese prompts too.
- Network access to `huggingface.co` is required.

## Verification

After running, confirm the output exists as a valid PNG (e.g. `file output.png` shows `PNG image data, 1024 x 1024`) before reporting success to the user.

## 参考

- `references/resolutions.md` — 官方 33 组分辨率/比例预设表（用户指定比例时查此表，如 3:4 竖版 → 832x1248 或 1024x1536）
- `scripts/zimage.py` — 一键生图 CLI（纯标准库，自动读 `~/.hf_token`）