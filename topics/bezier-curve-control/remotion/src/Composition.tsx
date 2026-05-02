import {
  AbsoluteFill,
  Audio,
  OffthreadVideo,
  Sequence,
  staticFile,
} from "remotion";

export const WIDTH = 1280;
export const HEIGHT = 720;
export const FPS = 15;

const chapters = [
  {
    title: "锚点和手柄的疑问",
    file: "StoryHook.mp4",
    seconds: 18.8,
  },
  {
    title: "两点线性插值",
    file: "LinearInterpolation.mp4",
    seconds: 22.47,
  },
  {
    title: "三点构造过程",
    file: "QuadraticConstruction.mp4",
    seconds: 23.67,
  },
  {
    title: "系数从哪里来",
    file: "CoefficientDerivation.mp4",
    seconds: 27.93,
  },
  {
    title: "二次公式和权重",
    file: "QuadraticFormula.mp4",
    seconds: 23.87,
  },
  {
    title: "四点三次贝塞尔",
    file: "CubicConstruction.mp4",
    seconds: 25.13,
  },
  {
    title: "控制点位移响应",
    file: "WeightControl.mp4",
    seconds: 28.4,
  },
  {
    title: "端点导数和手柄",
    file: "EndpointTangents.mp4",
    seconds: 27.53,
  },
  {
    title: "两段曲线平滑拼接",
    file: "SmoothJoin.mp4",
    seconds: 21.67,
  },
  {
    title: "编程里的贝塞尔曲线",
    file: "ProgrammingLinks.mp4",
    seconds: 46.2,
  },
];

const toFrames = (seconds: number) => Math.round(seconds * FPS);
const segmentFrames = chapters.map((chapter) => toFrames(chapter.seconds));
const starts = segmentFrames.reduce<number[]>((acc, duration, index) => {
  acc.push(index === 0 ? 0 : acc[index - 1] + segmentFrames[index - 1]);
  return acc;
}, []);

const TIMELINE_FRAMES = segmentFrames.reduce((sum, duration) => sum + duration, 0);
export const TOTAL_FRAMES = Math.max(TIMELINE_FRAMES, toFrames(265.86));

export const BezierRemotionPreview = () => {
  return (
    <AbsoluteFill className="bezier-stage">
      <div className="ambient ambient-a" />
      <div className="ambient ambient-b" />
      <div className="grid-layer" />

      <div className="top-bar">
        <div>
          <div className="eyebrow">REMOTION PACKAGE PREVIEW</div>
          <div className="film-title">贝塞尔曲线：几个点如何控制一条线？</div>
        </div>
      </div>

      <div className="screen-frame">
        {chapters.map((item, index) => {
          const start = starts[index];
          const duration =
            index === chapters.length - 1
              ? TOTAL_FRAMES - start
              : segmentFrames[index];

          return (
            <Sequence key={item.file} from={start} durationInFrames={duration}>
              <OffthreadVideo
                className="segment-video"
                muted
                src={staticFile(`segments/${item.file}`)}
              />
            </Sequence>
          );
        })}
      </div>

      <Audio src={staticFile("audio/narration.mp3")} />
    </AbsoluteFill>
  );
};
