# 贝塞尔曲线 v1 低清预览时长记录

## 产物

- 旁白稿：`topics/bezier-curve-control/audio/bezier_curve_control_v1_narration.txt`
- 分段场景：`topics/bezier-curve-control/scenes/bezier_curve_control_v1.py`
- 低清预览音频、SRT、静音拼接预览和带音轨预览已在最终成片确认后清理。

## 章节对齐

低清渲染质量：`480p15`。最终带音轨预览时长约 `00:04:25.86`，包含视频流和 AAC 音频流。

| Scene | 内容 | 实际片段时长 | 累计结束 |
| --- | --- | ---: | ---: |
| `StoryHook` | 设计软件里的锚点和手柄问题 | 18.80s | 18.80s |
| `LinearInterpolation` | 两点线性插值和参数 `t` | 22.47s | 41.27s |
| `QuadraticConstruction` | 三点 de Casteljau 构造 | 23.73s | 65.00s |
| `CoefficientDerivation` | 展开二次公式并解释系数来源 | 27.93s | 92.93s |
| `QuadraticFormula` | 二次贝塞尔公式和权重 | 23.87s | 116.80s |
| `CubicConstruction` | 四点三次贝塞尔构造 | 25.13s | 141.93s |
| `WeightControl` | 控制点位移和权重响应 | 28.40s | 170.33s |
| `EndpointTangents` | 端点导数和手柄方向 | 27.60s | 197.93s |
| `SmoothJoin` | 两段曲线的平滑拼接 | 21.73s | 219.66s |
| `ProgrammingLinks` | CSS、SVG、Canvas 和动画缓动 | 46.20s | 265.86s |

## 本轮检查

- 旁白按章节拆成 9 个视觉段落，避免在声音里硬念长公式。
- SRT 关键边界和视频累计边界基本在 0.1 秒内。
- 抽帧联系表：`topics/bezier-curve-control/exports/final/BezierCurveControl_v1_contact_sheet.jpg`。
- 二次公式段局部检查帧：`topics/bezier-curve-control/exports/final/QuadraticFormula_labeled_check.jpg`。
- 二次公式段遮挡修复与得意黑检查帧：`topics/bezier-curve-control/exports/final/QuadraticFormula_no_overlap_smiley_check.jpg`。
- 系数来源新增段检查帧：`topics/bezier-curve-control/exports/final/CoefficientDerivation_check.jpg`。
- 三次系数提示检查帧：`topics/bezier-curve-control/exports/final/QuadraticFormula_cubic_coeff_check.jpg`。
- 编程段单帧检查：`topics/bezier-curve-control/exports/final/BezierCurveControl_v1_programming_frame.jpg`。

## 下一轮可精修点

- 如果想做正式版，可以给编程段增加一两个真实 API 输入到曲线变化的镜头，避免最后一段停留时间偏长。
- 权重条目前是低清预览可读级别，高清前可以进一步放大数值或减少小数。
- 封面还没有单独设计；低清预览确认后再制作桌面和移动端封面。
