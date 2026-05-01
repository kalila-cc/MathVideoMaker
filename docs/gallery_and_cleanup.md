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
- `priority` 越高越靠前。
- `cover` 指向本地生成封面，不提交 Git；可用 `scripts/generate_cover.py` 生成并写回 metadata。
- `cover` 不填或文件不存在时会自动抽帧，主题视频会生成到 `topics/<topic>/exports/posters`。
- `chapters` 用于播放器下方章节进度条和点击跳转。
- 修改中文 metadata 时，避免通过 PowerShell here-string 或管道直接写入大段中文；优先使用 UTF-8 文件或 Python 脚本写入，并在写完后用 Python 读取确认标题、简介和章节不是乱码或问号。

生成封面：

```powershell
.\.venv\Scripts\python scripts\generate_cover.py --video topics\astroid-envelope\exports\final\LadderAstroidEnvelope_v6_preview_with_audio.mp4 --time 0.100 --out topics\astroid-envelope\exports\covers\LadderAstroidEnvelope_v6_cover.jpg --overwrite --update-metadata
```

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
