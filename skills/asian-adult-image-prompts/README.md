# Asian Adult Image Prompts

为支持 Agent Skills 的 AI 客户端提供成年、虚构、亚洲风格 editorial 或 boudoir 图像提示词。它会组合场景、构图、服装、光线、姿势与表情，生成连贯的英文图像提示词，并内置上游模板快照。

## 安装

需要 Git，以及任意支持 Agent Skills 的客户端。将下面的 `SKILLS_DIR` 替换为该客户端的个人技能目录；目录位置以客户端文档为准。

首次安装：

```bash
SKILLS_DIR=/path/to/your/skills
mkdir -p "$SKILLS_DIR"
git clone https://github.com/poisonhs/asian-adult-image-prompts.git \
  "$SKILLS_DIR/asian-adult-image-prompts"
```

安装后重新启动或刷新所用客户端的技能列表。

例如，当前环境中的 Codex 可使用 `~/.agents/skills`，Claude Code 可使用 `~/.claude/skills`。其他客户端请使用其文档规定的技能目录。

如果该目录已经是本仓库的 Git 工作副本，更新即可：

```bash
git -C "$SKILLS_DIR/asian-adult-image-prompts" pull --ff-only
```

如果目录已存在但没有 `.git`，不要直接覆盖。先备份或移走旧目录，再执行首次安装命令，以保留后续的提交和更新能力。

## 使用

直接描述画面需求。支持 `$技能名` 显式调用的客户端可使用：

```text
使用 $asian-adult-image-prompts：
创作一张成年、虚构的亚洲女性时尚私房摄影提示词。
室内自然侧光，半身构图，深色丝绸睡袍，克制优雅。
输出英文 Prompt 和 Negative prompt。
```

也可以使用简短形式：

```text
$asian-adult-image-prompts
成年虚构人物，日系杂志风私房摄影，柔光，85mm 镜头。
```

未指定输出格式时，技能返回中文 Brief、英文 Prompt 和可选 Negative prompt。提示词默认控制在 80 至 150 个英文词之间。

## 仓库内容

- `SKILL.md`：技能的运行时指引。
- `agents/openai.yaml`：可选的 OpenAI/Codex 界面元数据；不影响其他 Agent Skills 客户端使用 `SKILL.md`。
- `references/upstream/`：完整 Markdown 快照，包括范例、14 个模块和 README。
- `references/source-map.md`：固定版本、归属和授权说明。

## 开发与校验

修改技能后运行：

```bash
test -f SKILL.md
git diff --check
```

这两个检查不依赖具体客户端。若本机安装了 Codex Skill Creator，可额外运行其 `quick_validate.py`。发布前确认 `SKILL.md`、`references/upstream/` 和 `references/source-map.md` 都在提交中；`agents/openai.yaml` 是可选元数据。

## 备注

该技能修改自 [nsfw-prompt-templates-asian](https://github.com/ShuaiHui/nsfw-prompt-templates-asian) 
