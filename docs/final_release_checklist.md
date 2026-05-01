# 高清成片发布检查清单

这份文档沉淀最终高清成片阶段的工程经验。它关注“已经看起来没问题之后，如何避免最后一步翻车”。

## 最近踩到的问题

- 旧高清文件可能已经过时：低清预览修掉的视觉问题，不会自动同步到旧的 1080p 成片。最终发布必须从当前 Manim 源码重新渲染，而不是复用旧 MP4。
- 清理顺序必须保守：先生成新成片并完成技术验收，再删除旧视频、silent master、Manim 分段和旧封面。
- 中文 metadata 容易被 PowerShell 管道污染：不要用 PowerShell here-string 直接向 Python stdin 写入大量中文 JSON 字段；优先使用已有 UTF-8 文件、Python 脚本文件，或在临时脚本中用 Unicode escape。写完后必须用 Python 读取并检查标题是否仍是可读中文。
- 本地 FFmpeg 工具包目前只有 `ffmpeg.exe`，没有 `ffprobe.exe`。验证媒体信息时用 `ffmpeg -hide_banner -i <video>` 读取 `Duration`、`Stream`、分辨率、帧率和音轨。
- `ffmpeg -i` 只探测不输出时可能返回非零状态，但 stderr 里的媒体信息仍然有效。自动化脚本不要只用退出码判断探测失败。
- 最终图库只应展示完整成片。Manim 分段、silent master、旧预览和调试日志不应该出现在本地网页里。

## 发布步骤

1. 确认低清预览已经通过，且当前源码不含已否定的动效或旧文案。
2. 用高清参数重新渲染当前版本的所有正片 Scene 和片尾 Scene。
3. 按确定顺序拼接所有高清 Scene，生成临时 silent master。
4. 用当前旁白音轨合成最终 MP4。
5. 从短封面帧生成 cover JPG，并写回 `data/videos.json`。
6. 更新 metadata：标题、简介、标签、状态、优先级、封面和章节。
7. 验证最终 MP4 的分辨率、帧率、时长和音轨。
8. 预览网页确认只展示最终成片，章节跳转和封面正常。
9. dry-run 清理旧产物，确认清单无误后再执行删除。
10. 删除旧视频后再次验证 `data/videos.json` 和图库 API。

## 技术验收

推荐检查项：

- 分辨率：B 站发布版应为 `1920x1080`。
- 帧率：当前高清发布目标为 `60fps`。
- 音轨：最终 MP4 必须有 AAC 音轨。
- 时长：视频时长应覆盖正片加片尾，且旁白不会在画面结束后继续播放。
- 封面：`posterUrl` 应指向显式生成的 cover，而不是黑屏自动抽帧。
- 图库：`scripts/serve_videos.py --list` 只返回应展示的完整视频。

## 安全清理规则

- 永远先 dry-run，再加 `--execute`。
- 只清理 `topics/<topic>/exports/*` 或旧版 `exports/*` 下的生成物。
- 不删除 `scenes/`、`audio/`、`docs/`、`assets/` 等源码和素材。
- 旧 metadata 要通过 `--prune-metadata` 清掉，孤儿 poster 用 `--delete-orphan-posters` 清掉。
- 如果只保留最新成片，同时清理旧封面，确保新成片的 cover 文件仍存在。
