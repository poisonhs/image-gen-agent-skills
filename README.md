# image-gen-agent-skills

A portable **Agent Skills** bundle — follows the [agentskills.io](https://agentskills.io/specification)
open standard, so the same `SKILL.md` folders install into Claude Code, Codex, Gemini CLI,
Cursor, GitHub Copilot, OpenCode, Windsurf, Cline, Hermes Agent and more.

[English](#whats-inside) · [中文说明](#中文说明)

---

## What's inside

| Skill | What it does | Runtime need |
| --- | --- | --- |
| `z-image-generation` | Free AI image generation via the HuggingFace `Z-Image-Turbo` Space, driven by a standalone Python CLI that saves a PNG locally. No API key. | Python 3.8+, stdlib only, network to `huggingface.co` |
| `asian-adult-image-prompts` | Modular prompt library (14 reference modules: scene, shot, wardrobe, coverage, lighting, pose, expression, film stock, makeup, props…) for adult-only Asian-inspired editorial / boudoir image prompts. | none (markdown references) |

> ⚠️ `asian-adult-image-prompts` is **adult content (18+)** for **fictional, consenting adult
> subjects only**. Do not use it to depict real people without consent, or anyone under 18.

## Install

```bash
tar -xzf image-gen-agent-skills.tar.gz      # or: git clone <this repo>
cd image-gen-agent-skills

./install.sh                 # auto-detect installed agents, install to each
./install.sh --all           # install to every known global location
./install.sh --agent claude,gemini,cursor
./install.sh --project ~/my-repo      # repo-local install (team-shared)
./install.sh --path ~/my/skills       # custom directory
./install.sh --list          # show agents and resolved paths
./install.sh --dry-run       # preview without writing
./install.sh --uninstall     # remove from the same targets
```

Re-running `./install.sh` is idempotent — each skill directory is replaced wholesale.

### Where skills land

`SKILL.md` is the open standard; agents differ only in *where* they look for it.

| Agent | Global (personal) | Project (repo) |
| --- | --- | --- |
| **universal** (`.agents`) | `~/.agents/skills/` | `.agents/skills/` |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Codex | `~/.codex/skills/` | `.agents/skills/` |
| Gemini CLI | `~/.gemini/skills/` | `.gemini/skills/` |
| Cursor | `~/.cursor/skills/` | `.cursor/skills/` |
| GitHub Copilot | `~/.copilot/skills/` | `.github/skills/` |
| OpenCode | `~/.config/opencode/skills/` | `.opencode/skills/` |
| Windsurf | — | `.windsurf/skills/` |
| Cline | `~/.cline/skills/` | `.cline/skills/` |
| Hermes Agent | `~/.hermes/skills/` | — |
| Mistral Vibe | `~/.vibe/skills/` | — |

Most agents read `.agents/skills/` and/or `.claude/skills/`, so a single copy in
`~/.agents/skills/` is picked up by Codex, Copilot, Cursor and OpenCode at once.

After installing, restart the agent session so it rescans the skills directory.

## Validate

```bash
python3 scripts/validate-skills.py skills/
```

Checks `name` / `description` constraints, keeps frontmatter inside the portable key set,
and warns when a skill directory name diverges from its `name` field.

## Quick use of the generator

```bash
python3 skills/z-image-generation/scripts/zimage.py "a cat in a sunlit kitchen" \
  --width 1024 --height 1536 --steps 12
```

Pass `--seed N` for reproducible output. Put a HuggingFace **read** token in `~/.hf_token`
to raise the shared free ZeroGPU quota (`--token hf_...` or `HF_TOKEN` env also work).

## Layout

```
image-gen-agent-skills/
├── install.sh                     # multi-agent installer (bash, no deps)
├── scripts/validate-skills.py     # spec validator (python3, stdlib only)
├── skills/
│   ├── z-image-generation/
│   │   ├── SKILL.md
│   │   ├── scripts/zimage.py      # the generator CLI
│   │   └── references/resolutions.md
│   └── asian-adult-image-prompts/
│       ├── SKILL.md
│       ├── agents/openai.yaml     # optional Codex UI metadata
│       └── references/upstream/   # 16 modules
└── README.md
```

---

## 中文说明

一套**跨 agent 通用**的技能包，遵循 [agentskills.io](https://agentskills.io/specification)
开放标准（`SKILL.md` 格式），同一份文件可直接装进 Claude Code、Codex、Gemini CLI、Cursor、
GitHub Copilot、OpenCode、Windsurf、Cline、Hermes Agent 等工具，无需改写。

**包含两个技能：**

| 技能 | 作用 | 依赖 |
| --- | --- | --- |
| `z-image-generation` | 免费 AI 生图。走 HuggingFace Z-Image-Turbo Space，纯标准库 Python CLI，无需 API key，出图存到本地。 | Python 3.8+，仅标准库，需能访问 huggingface.co |
| `asian-adult-image-prompts` | 成人向提示词模板库，14 个模块（场景 / 景别 / 裸露 / 服装 / 光影 / 姿势 / 表情 / 胶片 / 妆容 / 道具 / 人格卡等），组合出连贯的写真提示词。 | 无（纯 markdown 参考） |

> ⚠️ `asian-adult-image-prompts` 为**成人内容（18+）**，仅适用于虚构的成年角色设定。

**安装（自动检测已装的 agent）：**

```bash
./install.sh                    # 自动检测并安装到所有已安装的 agent
./install.sh --agent claude,gemini,cursor   # 指定目标
./install.sh --project ~/my-repo            # 装到某个仓库（团队共享）
./install.sh --list             # 查看支持的 agent 和落地路径
./install.sh --uninstall        # 从相同目标卸载
```

装完重启 agent 会话即可识别。`.agents/skills/` 是事实通用目录（Codex、Copilot、Cursor、
OpenCode 都读它），放一份就能覆盖多家。

**快速生图：**

```bash
python3 skills/z-image-generation/scripts/zimage.py "夕阳下的海边公路，胶片感" \
  --width 1024 --height 1536 --steps 12
```

建议在 `~/.hf_token` 放一个 HuggingFace **read** token（免费申请），可绕开共享的免费
ZeroGPU 配额耗尽问题。

## License

MIT for the bundle, `install.sh` and `validate-skills.py` — see [LICENSE](LICENSE).
`asian-adult-image-prompts` bundles material pinned in
`skills/asian-adult-image-prompts/references/source-map.md`; check that file for upstream
attribution before redistributing.
