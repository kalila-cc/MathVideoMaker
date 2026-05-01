# 中文数学科普动画工具调研

检索日期：2026-05-01

## 推荐结论

主线工具链建议定为：

| 环节 | 首选工具 | 作用 | 选择理由 |
| --- | --- | --- | --- |
| 数学动画 | Manim Community Edition | 公式、坐标系、几何、函数、矩阵、证明动画 | Python 驱动、可复现、适合 3Blue1Brown 风格的精确数学可视化 |
| 视频编码 | FFmpeg | 渲染、转码、拼接、抽帧、压缩 | 通用底层工具，Manim/Motion Canvas/剪辑流程都常依赖 |
| 公式排版 | MiKTeX / XeLaTeX | `MathTex` 和复杂公式 | Windows 上易安装，支持按需安装 LaTeX 包 |
| 中文旁白 | edge-tts 起步，Azure Speech 进阶 | 生成普通话 MP3 和字幕 | edge-tts 成本低、脚本化方便；Azure Speech 更稳定、可控、有商业支持 |
| 最终剪辑 | 剪映/CapCut + DaVinci Resolve 二选一 | 字幕样式、音效、转场、调色、封面包装 | 剪映适合中文平台和快速成片；DaVinci 更专业、适合长期资产沉淀 |
| 音频处理 | Audacity | 降噪、剪切、响度微调 | 免费、跨平台、够用 |
| 辅助图形 | GeoGebra + Inkscape | 几何草图、SVG 图形资产 | GeoGebra 适合数学探索；SVG 资产可导入 Manim |

建议先不要把 Motion Canvas、Remotion、Blender 放进第一周的必备工具。它们很有价值，但会分散注意力。等 Manim 主流程跑通后，再按视频风格逐步加入。

## 当前项目落地约定

项目现在按主题组织素材和产物，避免把不同视频的脚本、音频和渲染结果混在根目录：

```text
topics/<主题 slug>/
  scenes/          # Manim 场景源码和版本迭代
  audio/           # 旁白稿、TTS 音频、SRT
  docs/            # 该主题的大纲、推导说明、设计记录
  exports/
    manim/         # Manim 中间渲染输出
    final/         # 带音轨成片或低清预览
    covers/        # 手工封面
    posters/       # 网页自动抽帧 poster
```

通用脚本保留在 `scripts/`。渲染脚本会根据 `topics/<主题>/scenes/...` 自动把 Manim 输出定位到同主题的 `exports/manim`；网页服务默认只扫描 `topics/*/exports/final`，避免把 Manim 分段草稿混进片库。如果直接调用 `manim`，请显式传入 `--media_dir topics/<主题>/exports/manim`，不要重新写入根目录 `exports/`。

## 核心工具对比

| 工具 | 强项 | 短板 | 适合场景 | 本项目定位 |
| --- | --- | --- | --- | --- |
| Manim CE | 精确数学对象、公式变换、坐标/函数/几何动画、批量渲染 | 初装依赖 FFmpeg/LaTeX；设计感需自己打磨 | 数学证明、函数直觉、线性代数、概率模拟 | 主力 |
| Motion Canvas | TypeScript、实时预览、时间线/音频同步友好、界面动效漂亮 | 数学专用能力不如 Manim；需要前端生态 | 科普包装、讲解型动效、代码/界面类动画 | 第二阶段可选 |
| Remotion | React 组件化视频、字幕/模板/批量生成能力强 | 不是数学动画专用；复杂几何要自己造轮子 | 系列包装、批量短视频、数据驱动模板 | 可选 |
| Blender | 3D、材质、镜头、Grease Pencil | 学习成本高；数学公式流程不轻 | 三维几何、空间想象、封面级视觉 | 可选重型工具 |
| GeoGebra | 交互式几何和函数探索快 | 成片动画控制弱 | 验证想法、导出几何草图 | 辅助 |
| 剪映/CapCut | 中文 TTS、智能字幕、模板、平台适配快 | 工程化和版本管理弱 | 快速剪辑、字幕、短视频包装 | 首选剪辑 |
| DaVinci Resolve | 剪辑、调色、Fusion、Fairlight 一体化 | 上手比剪映慢 | 长视频、精修、统一视觉资产 | 进阶剪辑 |

## 安装与准备清单

### 必备

1. Python 3.11：本机已安装。
2. Git：本机已安装。
3. FFmpeg：已安装到项目本地 `tools/ffmpeg/bin/ffmpeg.exe`。
4. MiKTeX：已通过 winget 安装 MiKTeX 25.12，`latex`、`xelatex`、`dvisvgm` 已验证可用。
5. Python 依赖：已安装到 `.venv`，包含 Manim 和 edge-tts。

### 推荐

1. 剪映专业版或 CapCut Desktop：用于中文 TTS、智能字幕、包装和快速发布。
2. Audacity：用于录音、降噪和响度微调。
3. GeoGebra：用于快速构造几何、函数图像和互动验证。

### 可选

1. Motion Canvas：当我们需要更强的画面节奏、UI 风格和音频同步。
2. Remotion：当我们要批量生成固定模板视频、片头片尾、动态字幕。
3. Blender：当我们要做三维几何或高质感封面动画。
4. Typst：当我们需要比 LaTeX 更快的现代排版资产，但 Manim 主流程仍以 LaTeX 为主。

## 推荐制作流程

1. 选题：用一句话写清楚“观众看完会多一个什么直觉”。
2. 建主题目录：新建 `topics/<主题 slug>/scenes`、`audio`、`docs` 和 `exports`。
3. 分镜：填 `docs/storyboard_template.md`，每 5-15 秒一个认知点。
4. 动画：用 Manim 做核心数学片段，优先低清片段级导出。
5. 旁白：用 `scripts/make_voice.py` 在主题 `audio/` 下生成 MP3 + SRT，后续可换真人录音。
6. 合成：用 `scripts/concat_videos.py` 拼接静音片段，再用 `scripts/add_audio.py` 写入 `topics/<主题>/exports/final`。
7. 预览：用 `scripts/serve_videos.py` 在网页里检查标题、简介、封面、章节跳转和音轨。
8. 精修与导出：低清预览通过后再渲染高质量版本；横版建议 1920x1080，短视频可另做 1080x1920 重排。

## 资料来源

- Manim Community 文档：<https://docs.manim.community/en/stable/>
- Manim Windows 安装：<https://docs.manim.community/en/stable/installation/windows.html>
- FFmpeg 文档：<https://ffmpeg.org/documentation.html>
- MiKTeX 下载：<https://miktex.org/download>
- Motion Canvas Quickstart：<https://motioncanvas.io/docs/quickstart/>
- Remotion 文档：<https://www.remotion.dev/docs/>
- Typst 文档：<https://typst.app/docs/>
- DaVinci Resolve：<https://www.blackmagicdesign.com/products/davinciresolve>
- CapCut Desktop：<https://www.capcut.com/tools/desktop-video-editor>
- 剪映官网：<https://www.capcut.cn/>
- Azure Speech TTS：<https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech>
- edge-tts：<https://github.com/rany2/edge-tts>
- Whisper：<https://github.com/openai/whisper>
- Audacity：<https://www.audacityteam.org/>
- GeoGebra：<https://www.geogebra.org/>
- Shotcut：<https://shotcut.org/>
