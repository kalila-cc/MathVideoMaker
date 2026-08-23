# 摩擦放大设计记录

## 2026-05-06 初版选题决定

- 主题从“两本书一页页交错为什么拉不开”提升为“摩擦如何被几何结构放大”。
- 两本书作为第一现场和主钩子，码头绳子作为更干净的连续模型，用来给出绞盘方程。
- 标题暂定“为什么越拉，反而越拉不开？”，避免局限在“一绕、一夹”的表述。
- 尾声可以点到皮带传动、登山保护器、绳结、鞋带等同类案例，但不展开新推导。
- 叙事重点不是接触面积，而是“拉力改变方向 -> 产生正压力 -> 正压力带来摩擦 -> 多层或多角度累积放大”。

## 后续制作注意

- 写旁白前要先确认两本书模型的数学深度：只讲趋势，还是给出一个简化递推。
- 若引入绞盘方程，需要避免公式突然出现；先用一小段绳子的受力图解释 `d\theta` 的作用。
- 画面里三类力箭头要严格区分：外拉力、正压力、摩擦力。
- 不要把真实书页实验讲成一个完全理想化、可精确预测的单公式问题。真实纸张弯曲、粗糙度、页数、压痕和装订方式都会影响结果。

## 2026-05-06 制作稿 v1

- 旁白文件：`topics/friction-amplification/audio/friction_amplification_v1_narration.txt`
- 书页段落采用“局部机制 + 页数趋势”，不展示闭式公式，避免把真实书页实验讲得过度精确。
- 数学高潮交给码头绕柱绳模型：先解释小角度转向产生正压力，再显示绞盘方程 `T_\text{heavy}/T_\text{light}=e^{\mu\theta}`。
- TTS 语速先按项目默认 `--rate +14%`，生成后以 SRT 总时长反推 Manim 场景节奏。

## 2026-05-06 v1 产物

- 场景源文件：`topics/friction-amplification/scenes/friction_amplification_v1.py`
- TTS 音频：`topics/friction-amplification/audio/friction_amplification_v1.mp3`
- 字幕文件：`topics/friction-amplification/audio/friction_amplification_v1.srt`
- 最终视频：`topics/friction-amplification/exports/final/FrictionAmplification_1080p60.mp4`
- 封面：`topics/friction-amplification/exports/covers/FrictionAmplification_v1_1080p60_cover.jpg`
- 低清关键帧 QA 曾发现多层阻力条残影，已改为 `Indicate` 动画并重渲染。

## 2026-05-06 v2 反馈修正

- 用户反馈：动画整体偏静态，码头绳子不像真正绕柱。
- 修正原则：每段长旁白至少绑定一个语义动作，例如拉力箭头、局部扫光、页数趋势点、公式或机制链高亮；不能只靠总时长等待。
- 码头绳子改为清晰的俯视柱体绕行图：显示柱面、接触带、绕行弧段、两端切向绳身、轻拉端/重载端、`d\theta` 与法向压力。
- 当前场景源文件：`topics/friction-amplification/scenes/friction_amplification_v2.py`
- 当前最终视频：`topics/friction-amplification/exports/final/FrictionAmplification_1080p60.mp4`
- 当前封面：`topics/friction-amplification/exports/covers/FrictionAmplification_v2_1080p60_cover.jpg`
