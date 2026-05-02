# 本地图库与清理

这份文档记录 `scripts/serve_videos.py`、`data/videos.json` 和清理脚本的维护方式。

## 本地图库

启动网页：

```powershell
.\.venv\Scripts\python scripts\serve_videos.py
```

默认扫描：

- `topics/*/exports/final`
- 旧版根目录 `exports/final` 只作为迁移兜底

网页默认只展示完整视频或完整预览，不展示 `exports/manim/videos` 里的 Manim 分段草稿。需要调试单个 Scene 时，直接打开 Manim 输出目录或显式通过 `--video-root` 指定分段目录。

网页支持：

- 播放本地 MP4。
- 展示标题、简介、标签、状态、封面和章节进度。
- 点击章节跳转。
- 删除本地视频文件，同时清理自动 poster 和对应 metadata。

## 元数据

`data/videos.json` 是本地视频库的内容管理入口。建议每条重要成片或预览至少包含：

```json
{
  "videos": {
    "topics/astroid-envelope/exports/final/LadderAstroidEnvelope_v6_preview_with_audio.mp4": {
      "title": "棍子滑落为什么会扫出星形线？v6 低清预览",
      "description": "一句话说明这一版解决了什么问题，以及观众能看懂什么。",
      "topic": "微分与包络线",
      "tags": ["星形线", "包络线", "低清预览"],
      "status": "低清预览",
      "priority": 720,
      "cover": "topics/astroid-envelope/exports/covers/LadderAstroidEnvelope_v6_cover.jpg",
      "covers": {
        "desktop": "topics/astroid-envelope/exports/covers/LadderAstroidEnvelope_v6_cover.jpg",
        "mobile": "topics/astroid-envelope/exports/covers/LadderAstroidEnvelope_v6_cover.jpg"
      },
      "chapters": [
        {"title": "滑落棍子的场景", "start": 0.0, "end": 7.94},
        {"title": "外轮廓到底是什么", "start": 7.94, "end": 20.8}
      ]
    }
  }
}
```

说明：

- 键可以使用视频相对路径，也可以使用文件名作为兜底匹配。
- 默认展示顺序按 `modified` 更新时间降序；`priority` 只作为更新时间相同时的次级排序和人工标记。
- 默认只生成一张移动端优先封面；`cover` 指向这张图。为了兼容宽窄屏读取逻辑，`covers.desktop` 与 `covers.mobile` 可以同时指向同一张图。
- 只有用户明确要求多平台差异版时，才分别生成电脑端封面和手机端/双列信息流封面。
- 封面图不提交 Git；可用 `scripts/generate_cover.py` 生成封面并写回 metadata。
- Remotion 预览目录里的 `public/audio` 和 `public/segments` 通常是旁白和 Manim 分段的本地镜像素材，不提交 Git；需要复现时按主题脚本或渲染流程重新生成。
- `covers`/`cover` 不填或文件不存在时会自动抽帧，主题视频会生成到 `topics/<topic>/exports/posters`。
- `chapters` 用于播放器下方章节进度条和点击跳转。
- 修改中文 metadata 时，避免通过 PowerShell here-string 或管道直接写入大段中文；优先使用 UTF-8 文件或 Python 脚本写入，并在写完后用 Python 读取确认标题、简介和章节不是乱码或问号。
- 最终成片条目要使用面向发布的标题、简介、状态和标签；不要继续保留 `v10`、`低清预览`、`字体试用`、平台规格等迭代语义。
- 同一主题最终版确认后，删除或移除旧预览、分段预览和静音母版的 metadata，避免图库把过期版本当作当前视频展示。

生成封面：

```powershell
.\.venv\Scripts\python scripts\generate_cover.py --video topics\astroid-envelope\exports\final\LadderAstroidEnvelope_v6_preview_with_audio.mp4 --time 0.100 --out topics\astroid-envelope\exports\covers\LadderAstroidEnvelope_v6_cover.jpg --overwrite --update-metadata
```

## 分段预览

如果只改了片头、片尾或单个 Manim scene，不必先拼出完整 MP4。可以在 `data/videos.json` 新增一个没有实体文件的逻辑条目，并用 `segments` 列出本地 MP4 片段：

```json
{
  "videos": {
    "topics/example/exports/final/example_segmented_preview": {
      "title": "示例分段预览",
      "status": "分段低清预览",
      "priority": 900,
      "cover": "topics/example/exports/covers/example_cover.jpg",
      "audio": "topics/example/audio/example_preview.mp3",
      "audioDelay": 2.0,
      "segments": [
        {"title": "片头", "path": "topics/example/exports/manim/videos/intro/480p15/Intro.mp4"},
        {"title": "正文", "path": "topics/example/exports/manim/videos/main/480p15/Main.mp4"}
      ]
    }
  }
}
```

- `segments` 可以指向 `exports/manim/videos` 下的 scene 输出，但必须显式写入 metadata，图库不会自动扫出所有草稿片段。
- 分段条目会按片段总时长显示为一个完整视频，章节未填写时自动使用每个 segment 的 `title` 生成跳转按钮。
- 如果 Manim 分段本身没有音轨，可给分段条目配置 `audio` 指向旁白 MP3；`audioDelay` 表示这条音频在虚拟完整时间轴中延迟多少秒开始播放，用来避开无旁白片头或抵消音频文件自带静默。
- 分段条目只串接播放，不会生成新 MP4，也不会在网页里提供删除源片段的按钮。
- 真正发布前仍要执行完整 concat/mux/final render 验证，分段预览只用于快速检查局部改动和整体节奏。

## 工具阻塞与处理

- `scripts/serve_videos.py --stop` 在 Windows 上可能因为陈旧 PID 报 `WinError 87`；先用 `Get-NetTCPConnection -LocalPort 8765 -State Listen` 查实际监听进程，必要时再 `Stop-Process -Id <pid> -Force`，随后重新启动服务。
- 当前环境可能没有全局 `ffprobe`；用 `.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe -hide_banner -i <video>` 读取时长、分辨率、帧率和音频流。
- Playwright 包可能存在但浏览器二进制未安装；不要临时运行安装命令，优先用已安装的 Chrome/Edge `executablePath` 做网页验证。
- 如果 `rg` 在 Windows 会话中临时返回 `Access is denied`，用 `Select-String` 兜底搜索，不要卡在工具本身。

## 清理脚本

预览将删除哪些旧产物：

```powershell
.\.venv\Scripts\python scripts\clean_generated_videos.py --preset old-astroid-iterations --preset manim-partials --delete-orphan-posters --prune-metadata
```

确认无误后执行：

```powershell
.\.venv\Scripts\python scripts\clean_generated_videos.py --preset old-astroid-iterations --preset manim-partials --delete-orphan-posters --prune-metadata --execute
```

常用预设：

- `old-astroid-iterations`：删除星形线 v2-v5 和最早版本的旧迭代视频，保留当前 v6。
- `manim-partials`：删除 Manim 的 `partial_movie_files` 缓存。
- 需要清理分段草稿时，可额外使用 `--glob "topics/<topic>/exports/manim/videos/*"`；默认会先 dry-run，确认后再加 `--execute`。

安全边界：

- 脚本只允许操作旧版 `exports/*` 输出目录或 `topics/<topic>/exports/*` 输出目录。
- 不会删除 `topics/<topic>/scenes`、`audio`、`docs` 等源码和素材目录。
- 默认 dry-run，不加 `--execute` 不会真正删除文件。
- 主题最终清理时，目标状态通常是只保留 `topics/<topic>/exports/final/<final>.mp4`、`topics/<topic>/exports/covers/<final>_cover.jpg`，以及有复用价值的最终旁白稿和 SRT。执行递归删除前必须确认解析后的绝对路径仍在该主题目录内。
