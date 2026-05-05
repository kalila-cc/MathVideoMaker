# 贝塞尔曲线 Remotion 局部渲染

这个目录只用于贝塞尔曲线视频中的编程段局部画面。Manim 仍负责整片背景、标题、公式和主数学动画；Remotion 只负责代码/参数关系这类局部动态内容，再按需要导出片段或透明层参与合成。

## 常用命令

```powershell
npm install
npm run dev
npx remotion render
```

## 维护约定

- 不把 Remotion 模板 README 当作项目说明保留。
- `node_modules/`、本地预览素材和渲染产物不提交。
- 如果 Remotion 输出替换了某个 Manim 分段，必须同步更新 `data/videos.json` 的 `segments` 路径或最终拼接清单，避免图库继续播放旧片段。
- 背景、标题、底部公式和全片字体系统仍由 Manim 统一控制。
