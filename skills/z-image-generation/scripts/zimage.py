#!/usr/bin/env python3
"""One-shot Z-Image image generation via the Hugging Face Space Gradio API.

Free, no API key, no registration. Pure Python stdlib (3.8+).

Usage:
    python zimage.py "a cute corgi wearing sunglasses, neon city"
    python zimage.py "prompt" --width 768 --height 1024 --steps 12 --seed 42 --out-dir ./img

Prints the saved image path and the seed used.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SPACE = "mrfakename/Z-Image-Turbo"
BASE = "https://mrfakename-z-image-turbo.hf.space"
FN = "/generate_image"
UA = "zimage-cli/1.0"

# Optional HF token: pass --token, set HF_TOKEN env, or store in ~/.hf_token
# (chmod 600). Authentication gets a larger ZeroGPU quota and avoids
# "ZeroGPU quota exceeded" errors.
HF_TOKEN = os.environ.get("HF_TOKEN", "")
if not HF_TOKEN:
    try:
        with open(os.path.expanduser("~/.hf_token")) as f:
            HF_TOKEN = f.read().strip()
    except OSError:
        pass


def _headers(auth: bool = True):
    h = {"User-Agent": UA}
    if auth and HF_TOKEN:
        h["Authorization"] = f"Bearer {HF_TOKEN}"
    return h


def http_json(url: str, method: str = "GET", payload=None, timeout: int = 30):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={**_headers(), "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def poll_sse(url: str, timeout: int):
    """Read Gradio SSE stream; return (event, data) of the terminal event, or None."""
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=timeout) as r:
        event, data_lines = None, []
        for raw in r:
            line = raw.decode("utf-8", "replace").rstrip("\r\n")
            if line.startswith("event:"):
                event = line[6:].strip()
            elif line.startswith("data:"):
                data_lines.append(line[5:].strip())
            elif line == "":
                if event in ("complete", "error"):
                    return event, "\n".join(data_lines)
                event, data_lines = None, []
    return None, None


def download(url: str, dest: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        while True:
            chunk = r.read(65536)
            if not chunk:
                break
            f.write(chunk)


def main():
    ap = argparse.ArgumentParser(description="Generate an image with Z-Image (free, no key)")
    ap.add_argument("prompt", help="image description (English works best, Chinese supported)")
    ap.add_argument("--width", type=int, default=1024, help="512-2048 (default 1024)")
    ap.add_argument("--height", type=int, default=1024, help="512-2048 (default 1024)")
    ap.add_argument("--steps", type=int, default=9, help="inference steps 1-20 (default 9)")
    ap.add_argument("--seed", type=int, default=None, help="fixed seed for reproducibility; default random")
    ap.add_argument("--out-dir", default="zimage_output", help="output directory (default ./zimage_output)")
    ap.add_argument("--timeout", type=int, default=300, help="poll timeout seconds (default 300)")
    ap.add_argument("--token", default=None, help="Hugging Face token (or set HF_TOKEN env) for larger ZeroGPU quota")
    args = ap.parse_args()

    global HF_TOKEN
    if args.token:
        HF_TOKEN = args.token

    if not (512 <= args.width <= 2048 and 512 <= args.height <= 2048):
        print("[!] width/height must be 512-2048")
        sys.exit(1)

    randomize = args.seed is None
    seed = 42 if randomize else args.seed

    print(f"[*] Submitting: {args.prompt!r} ({args.width}x{args.height}, steps={args.steps})")
    try:
        resp = http_json(f"{BASE}/gradio_api/call{FN}", "POST",
                         {"data": [args.prompt, args.height, args.width, args.steps, seed, randomize]},
                         timeout=60)
    except urllib.error.HTTPError as e:
        print(f"[!] Submit failed HTTP {e.code}: {e.read().decode()[:300]}")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Submit failed (Space may be cold-starting; retry): {e}")
        sys.exit(1)

    event_id = resp.get("event_id")
    if not event_id:
        print(f"[!] No event_id: {resp}")
        sys.exit(1)
    print(f"[*] event_id={event_id}, waiting for result...")

    result = None
    err_msg = None
    try:
        event, raw = poll_sse(f"{BASE}/gradio_api/call{FN}/{event_id}", args.timeout)
        if event == "complete" and raw:
            result = json.loads(raw)
        elif event == "error":
            err_msg = raw
    except Exception as e:
        print(f"[!] Poll error: {e}")
        sys.exit(1)

    if err_msg:
        print(f"[!] Space returned an error event: {err_msg[:400]}")
        print("    Common cause: ZeroGPU free quota exhausted (try again later, or pass --token).")
        sys.exit(1)

    if not result:
        print("[!] Stream ended without a complete event. Try --timeout larger (cold start) or retry.")
        sys.exit(1)

    # Result: [{fileData...}, seed_used]
    file_data = result[0] if isinstance(result, list) else result
    seed_used = result[1] if isinstance(result, list) and len(result) > 1 else None
    url = file_data.get("url") if isinstance(file_data, dict) else None
    if not url:
        print(f"[!] No image URL in result: {json.dumps(result, ensure_ascii=False)[:400]}")
        sys.exit(1)

    os.makedirs(args.out_dir, exist_ok=True)
    name = urllib.parse.urlparse(url).path.split("/")[-1] or f"zimage_{int(time.time())}.png"
    dest = os.path.join(args.out_dir, name)
    print(f"[*] Downloading -> {dest}")
    download(url, dest)

    print(f"IMAGE_SAVED={os.path.abspath(dest)}")
    if seed_used is not None:
        print(f"SEED_USED={seed_used}")
    print("[*] Done. Display this image to the user.")


if __name__ == "__main__":
    main()
