# 视频制作迭代流程

这份文档记录项目的标准制作闭环。README 只保留入口命令，具体流程在这里维护。

## 基本原则

- 从生活场景或直观问题开场，不要一上来抛公式、定理或“第几章”。
- 旁白按段落组织，每个段落对应一个 Scene 或一个章节进度点。
- 复杂视频拆成多个 Manim Scene，先低清预览，再高清渲染。
- 画面、旁白和章节进度都以 SRT 时间轴为校准基准。
- 每个主题的源码、音频和产物都留在 `topics/<topic>/` 内。
- 每个主题必须有当前大纲；钩子、章节、推导路线、视觉计划或产物状态变化时，同步更新 `topics/<topic>/docs/*_outline.md`。

## 推荐步骤

1. 用 `video-topic-bootstrap` 建主题目录并创建当前大纲。
2. 写清楚选题钩子：观众看完会多一个什么直觉。
3. 用 `math-video-outline` 审阅或改写大纲：确认钩子、章节、推导路线和视觉计划。
4. 写旁白草稿：一段旁白对应一个视觉节拍；如果旁白改变章节或推导顺序，先更新大纲。
5. 用 `narration-script-review` 审阅旁白：先检查章节、口语感、开头钩子、比喻、多音字和公式读法。
6. 生成低清配音和 SRT：先拿配音长度反推画面节奏。
7. 拆分 Manim 场景：每个章节独立渲染，方便局部重做。
8. 低清渲染预览：优先使用 `-ql` 验证叙事、推导、配音和画面同步。
9. 按 SRT 校准停顿：对照每个场景实际时长，微调 `self.wait(...)`；章节边界变化时更新大纲。
10. 拼接片段并合成音轨：输出到 `topics/<topic>/exports/final`。
11. 从短封面帧生成本地封面 JPG，输出到 `topics/<topic>/exports/covers`。
12. 进本地网页检查：标题、简介、封面、章节跳转、音轨和预览体验。
13. 低清版确认后，再渲染最终高清版。
14. 高清发布前后按 `docs/final_release_checklist.md` 做验收和清理，避免复用旧高清文件或误删新成片；最终成片、封面和字幕路径同步写回大纲。

## 常用命令

生成旁白：

生成前先让 `narration-script-review` 审阅旁白稿；只有结论为 `Ready for TTS`，或阻塞问题已修正后，再执行命令。

```powershell
.\.venv\Scripts\python scripts\make_voice.py --text-file topics\<topic>\audio\narration.txt --out topics\<topic>\audio\preview.mp3 --srt topics\<topic>\audio\preview.srt --rate +14%
```

并行渲染章节：

```powershell
.\scripts\render_scenes_parallel.ps1 -SceneFile topics\<topic>\scenes\<scene_file>.py -SceneNames CoverFrame,StoryHook,MainProof -MaxParallel 3
```

拼接静音片段：

```powershell
.\.venv\Scripts\python scripts\concat_videos.py --out topics\<topic>\exports\final\preview_silent.mp4 --overwrite <clip1.mp4> <clip2.mp4> <clip3.mp4>
```

合成音轨：

```powershell
.\.venv\Scripts\python scripts\add_audio.py --video topics\<topic>\exports\final\preview_silent.mp4 --audio topics\<topic>\audio\preview.mp3 --out topics\<topic>\exports\final\preview_with_audio.mp4 --overwrite
```

生成本地封面并写回 metadata：

```powershell
.\.venv\Scripts\python scripts\generate_cover.py --video topics\<topic>\exports\final\preview_with_audio.mp4 --time 0.100 --out topics\<topic>\exports\covers\preview_cover.jpg --overwrite --update-metadata
```

启动预览网页：

```powershell
.\.venv\Scripts\python scripts\serve_videos.py
```

## 主题专用命令

不要把某个视频的“当前命令”长期放在这份通用流程文档里；它们很快会随着版本、旁白文件名和片头方式过期。主题专用命令应放在该主题 `topics/<topic>/docs/design_notes.md`、独立脚本，或最终发布时临时记录在任务日志中。

## 版本化方式

项目采用“版本化暂存 + 持续微调”，不是每次从零生成新代码。

- 先复制上一版稳定场景作为新版本。
- 只在新版本上微调节奏、推导、排版和文案。
- 上一版保留作可回退和对比基线。
- 源码版本可以保留；旧视频产物可以用清理脚本删除。
