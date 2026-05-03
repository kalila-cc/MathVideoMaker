# 咖啡杯焦散线 v1 大纲

## 基本信息

- 标题：杯子里的心形光斑，是怎么来的？
- 主题 slug：`coffee-cup-caustic`
- 目标观众：对日常现象好奇、能接受少量公式的中文科普观众。
- 预览长度：v1 约 1 分 30 秒；v2 预计约 2 分钟，重点补足几何推导。
- 核心问题：为什么圆杯内壁反射阳光后，会出现一条像心形的亮线？
- 一句话结论：这条亮线不是单独一束光，而是一族反射光线的包络线；在理想圆杯模型里，它是一条肾形线。
- 工作目录：`topics/coffee-cup-caustic/`
- v1 场景文件：`topics/coffee-cup-caustic/scenes/coffee_cup_caustic_v1.py`
- v2 场景文件：`topics/coffee-cup-caustic/scenes/coffee_cup_caustic_v2.py`
- v1 旁白文件：`topics/coffee-cup-caustic/audio/coffee_cup_caustic_v1_narration.txt`
- v2 旁白文件：`topics/coffee-cup-caustic/audio/coffee_cup_caustic_v2_narration.txt`
- v2 低清预览：`topics/coffee-cup-caustic/exports/final/CoffeeCupCaustic_v2_preview_with_audio.mp4`

## 观众承诺

看完后，观众会把杯子里的亮线理解成“很多反射光线共同擦出来的边界”，并知道它为什么会和包络线、焦散线、肾形线联系起来。

## 分镜结构

| 时间 | 章节标题 | 画面 | 旁白意图 | 数学重点 | 风险与处理 |
| --- | --- | --- | --- | --- | --- |
| 0:00-0:11.6 | 杯中亮线 | 圆杯俯视图，几束光反射后出现亮线 | 从生活现象开场，不先讲公式 | 暂不命名 | 不能提前说“肾形线”，先让亮线可见 |
| 0:11.5-0:33.7 | 定位反射点 | 圆心 `O`、半径 `R`、角度 `\theta`、反射点 `P(\theta)` 和投影虚线 | 把变量绑定到画面 | `P(\theta)=(R\cos\theta,R\sin\theta)` | 先定位点，不急着说反射方程 |
| 0:33.7-0:58.9 | 反射方向 | 法线 `OP`、切线、入射方向、反射方向和向量式 | 解释方向为什么由 `\theta` 决定 | 反射向量 | 旁白不逐项念公式，只说明式子的角色 |
| 0:58.9-1:12.5 | 写出光线 | 点 `P(\theta)`、方向 `d`、直线族方程 | 从几何对象过渡到方程 | 反射光线方程 | 单独成段，避免和反射定律挤在一起 |
| 1:12.5-1:28.1 | 光线族 | 反射点沿杯壁移动，许多反射线叠加 | 让观众先看见“边界变亮” | 一族直线 | “焦散线”只在亮边界出现后命名 |
| 1:28.1-1:47.4 | 包络条件 | 两条相邻光线共同擦过同一点，右侧显示条件 | 解释怎么从直线族找边界 | `F=0` 与 `F_\theta=0` | 明确对 `\theta` 求偏导时固定屏幕上的点 |
| 1:47.4-1:59.5 | 肾形线 | 参数式出现，完整曲线在圆杯里描出 | 给出理想模型的结果 | 肾形线参数式 | 不逐项硬推，避免认知负荷过高 |
| 1:59.5-2:15.2 | 现实回声 | 圆杯、斜光、粗糙杯壁的对比 | 说明真实杯子会变形但机制相同 | 反射线族的包络 | 收尾必须回到完整亮线，而不是停在公式 |

## 屏幕公式

- 反射点：`P(\theta)=(R\cos\theta, R\sin\theta)`
- 入射方向：`\vec{i}=(1,0)`
- 法线方向：`\vec{n}=(\cos\theta,\sin\theta)`
- 反射方向：`\vec{d}=\vec{i}-2(\vec{i}\cdot\vec{n})\vec{n}=(-\cos 2\theta,-\sin 2\theta)`
- 反射光线族：`F(x,y,\theta)=x\sin(2\theta)-y\cos(2\theta)-R\sin\theta=0`
- 包络条件：`F(x,y,\theta)=0`，`\frac{\partial F}{\partial\theta}(x,y,\theta)=0`
- 肾形线参数式：`x=R(\frac{3}{2}\cos\theta-\cos^3\theta)`，`y=R\sin^3\theta`

## 制作检查

- 开头从杯中亮线开始，不说公式和定理。
- “焦散线”和“包络线”都在可见证据之后再出现。
- 变量 `R`、`\theta`、`P(\theta)` 都绑定到杯壁、角度和反射点。
- 中文标题、说明和标签统一使用项目本地得意黑 / Smiley Sans 字体资产；公式继续使用 `MathTex` 的 Times 系数学排版。
- 旁白不念复杂公式；公式只在画面上作为结构说明。
- 低清预览先验证叙事、画面和音轨，再考虑高清渲染。
