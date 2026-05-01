# 中文数学科普动画工作台

这是一个面向中文数学科普动画的本地制作工作台。当前主线流程是：

1. 用 Manim 生成可复现的数学动画片段。
2. 用 edge-tts 生成中文旁白和 SRT 时间轴。
3. 用 FFmpeg 拼接片段、合成音轨、抽取预览封面。
4. 用本地网页检查视频标题、简介、封面、章节跳转和删除操作。

## 当前状态

- 当前主题：`topics/astroid-envelope/`
- 当前成片预览：`topics/astroid-envelope/exports/final/LadderAstroidEnvelope_v6_preview_with_audio.mp4`
- 当前封面：`topics/astroid-envelope/exports/covers/LadderAstroidEnvelope_v6_cover.jpg`
- 本地图库入口：`.\.venv\Scripts\python scripts\serve_videos.py`

项目已配置 `.venv`、Manim、edge-tts、本地 FFmpeg 和 MiKTeX。第一次接手时建议先运行：

```powershell
.\scripts\check_tools.ps1
```

## 项目结构

项目按“视频主题”聚合素材，不再把场景、音频和产物散放到根目录：

```text
topics/
  <topic>/
    scenes/          # Manim 场景源码和版本迭代
    audio/           # 旁白稿、TTS 音频、SRT
    docs/            # 该主题的大纲、推导和设计记录
    exports/
      manim/         # Manim 中间渲染输出
      final/         # 带音轨成片或低清预览
      covers/        # 手工封面
      posters/       # 网页自动抽帧 poster
```

通用脚本放在 `scripts/`，全局视频库索引放在 `data/videos.json`，项目 skills 放在 `.agents/skills/`。

## 快速开始

创建或刷新 Python 环境：

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
```

渲染一个无需 LaTeX 的烟雾测试：

```powershell
.\scripts\render_scene.ps1 -SceneFile topics\smoke-test\scenes\demo_no_latex.py -SceneName NoLatexSmokeTest
```

生成中文旁白和 SRT：

```powershell
.\.venv\Scripts\python scripts\make_voice.py --text-file topics\<topic>\audio\narration.txt --out topics\<topic>\audio\preview.mp3 --srt topics\<topic>\audio\preview.srt
```

把音轨合成进视频：

```powershell
.\.venv\Scripts\python scripts\add_audio.py --video topics\<topic>\exports\final\preview_silent.mp4 --audio topics\<topic>\audio\preview.mp3 --out topics\<topic>\exports\final\preview_with_audio.mp4 --overwrite
```

启动本地视频库：

```powershell
.\.venv\Scripts\python scripts\serve_videos.py
```

## 常用脚本

- `scripts/render_scene.ps1`：渲染单个 Manim Scene，并自动把 topic 场景输出到 `topics/<topic>/exports/manim`。
- `scripts/render_scenes_parallel.ps1`：并行渲染多个 Scene，低清预览默认 `MaxParallel 3` 较稳。
- `scripts/make_voice.py`：生成 MP3 和 SRT。
- `scripts/concat_videos.py`：用 FFmpeg 拼接章节片段。
- `scripts/add_audio.py`：把旁白合成到 MP4。
- `scripts/generate_cover.py`：从视频帧生成本地封面 JPG，并可写回 `data/videos.json`。
- `scripts/serve_videos.py`：启动本地视频库网页。
- `scripts/clean_generated_videos.py`：安全清理旧迭代视频、Manim 临时缓存和孤儿 poster。

## 文档地图

- [docs/workflow.md](docs/workflow.md)：从选题、旁白、渲染到合成预览的完整迭代流程。
- [docs/creative_quality_principles.md](docs/creative_quality_principles.md)：从用户反馈中沉淀出的通用创作质量原则。
- [docs/gallery_and_cleanup.md](docs/gallery_and_cleanup.md)：`data/videos.json` 元数据、本地图库、封面、删除和清理脚本。
- [docs/tooling_research.md](docs/tooling_research.md)：工具调研和取舍记录。
- [docs/storyboard_template.md](docs/storyboard_template.md)：新视频分镜模板。
- [topics/astroid-envelope/docs/design_notes.md](topics/astroid-envelope/docs/design_notes.md)：星形线视频的内容设计沉淀、已采纳改进和踩坑。
- [topics/astroid-envelope/docs/astroid_envelope_outline.md](topics/astroid-envelope/docs/astroid_envelope_outline.md)：星形线视频早期大纲。

## 项目 Skills

- `math-video-outline`：选题、大纲、开头钩子、比喻和观众理解风险。
- `manim-scene-iteration`：Manim 场景版本化、低清预览、封面帧和排版控制。
- `narration-tts-sync`：中文旁白、TTS 读音规避、SRT 和画面节奏同步。
- `render-preview-pipeline`：片段渲染、拼接、合成音轨、封面和最终渲染前验证。
- `video-gallery-maintenance`：本地视频库、元数据、封面、章节跳转和清理。
- `project-self-evolution`：把新踩坑和用户反馈沉淀回文档、脚本和 skills，保持项目自我迭代。
- `pre-commit-doc-sync`：提交前检查 diff、文档同步点和生成产物忽略情况，避免实现和文档脱节。

## 维护原则

- 新主题优先创建 `topics/<topic>/scenes`、`audio`、`docs`、`exports`。
- README 只保留入口信息；长流程、案例复盘和规范放进 `docs/` 或主题 `docs/`。
- 低清预览通过后再渲染高清，避免反复浪费时间。
- 重要成片在 `data/videos.json` 里维护标题、简介、封面和章节。
- 封面 JPG 属于可生成产物，不提交 Git；需要时用 `scripts/generate_cover.py` 生成。
- 删除文件优先使用项目脚本或网页按钮，不手动清理不确定的产物目录。
