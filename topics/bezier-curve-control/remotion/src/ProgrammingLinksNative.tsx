import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";

export const PROGRAMMING_LINKS_WIDTH = 1920;
export const PROGRAMMING_LINKS_HEIGHT = 1080;
export const PROGRAMMING_LINKS_FPS = 60;
export const PROGRAMMING_LINKS_SECONDS = 46.18;
export const PROGRAMMING_LINKS_FRAMES = Math.round(
  PROGRAMMING_LINKS_SECONDS * PROGRAMMING_LINKS_FPS,
);

const colors = {
  bg: "#07111F",
  panel: "rgba(13, 23, 39, 0.94)",
  panelStroke: "#2A3A50",
  ink: "#F8F4E3",
  muted: "#AAB4C2",
  blue: "#7DD3FC",
  mint: "#5EEAD4",
  amber: "#F6B73C",
  rose: "#FF5C7A",
  purple: "#A78BFA",
};

type Point = {
  x: number;
  y: number;
};

type CssState = {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
};

const ease = Easing.bezier(0.45, 0, 0.2, 1);

const seconds = (frame: number) => frame / PROGRAMMING_LINKS_FPS;

const valueAt = (
  sec: number,
  stops: Array<[time: number, value: number]>,
) => {
  if (sec <= stops[0][0]) {
    return stops[0][1];
  }

  for (let i = 0; i < stops.length - 1; i += 1) {
    const [startTime, startValue] = stops[i];
    const [endTime, endValue] = stops[i + 1];

    if (sec <= endTime) {
      return interpolate(sec, [startTime, endTime], [startValue, endValue], {
        easing: ease,
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
    }
  }

  return stops[stops.length - 1][1];
};

const fade = (sec: number, start: number, duration = 0.55) =>
  interpolate(sec, [start, start + duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

const cssNumber = (value: number) => {
  if (Math.abs(value) < 0.005) {
    return "0";
  }

  if (Math.abs(value - 1) < 0.005) {
    return "1";
  }

  return value.toFixed(2).replace(/^0/, "");
};

const cssStateAt = (sec: number): CssState => ({
  x1: valueAt(sec, [
    [0, 0.42],
    [1.0, 0.42],
    [4.8, 0.22],
    [9.0, 0.66],
    [14.0, 0.32],
    [24.0, 0.42],
    [32.0, 0.18],
    [42.5, 0.42],
  ]),
  y1: valueAt(sec, [
    [0, 0],
    [1.0, 0],
    [4.8, 0.36],
    [9.0, 0.08],
    [14.0, 0],
    [32.0, 0.54],
    [42.5, 0],
  ]),
  x2: valueAt(sec, [
    [0, 0.58],
    [1.0, 0.58],
    [4.8, 0.88],
    [9.0, 0.56],
    [14.0, 0.82],
    [24.0, 0.58],
    [32.0, 0.92],
    [42.5, 0.58],
  ]),
  y2: valueAt(sec, [
    [0, 1],
    [1.0, 1],
    [4.8, 0.72],
    [9.0, 0.96],
    [14.0, 0.78],
    [32.0, 0.62],
    [42.5, 1],
  ]),
});

const markerAt = (sec: number) =>
  valueAt(sec, [
    [0, 0],
    [1.0, 0],
    [6.0, 1],
    [10.0, 0.18],
    [23.0, 0.82],
    [31.0, 0.92],
    [37.0, 0.18],
    [43.0, 1],
    [46.0, 0],
  ]);

const cubic = (points: [Point, Point, Point, Point], t: number): Point => {
  const mt = 1 - t;
  return {
    x:
      mt * mt * mt * points[0].x +
      3 * mt * mt * t * points[1].x +
      3 * mt * t * t * points[2].x +
      t * t * t * points[3].x,
    y:
      mt * mt * mt * points[0].y +
      3 * mt * mt * t * points[1].y +
      3 * mt * t * t * points[2].y +
      t * t * t * points[3].y,
  };
};

const pathFrom = (points: [Point, Point, Point, Point]) =>
  `M ${points[0].x} ${points[0].y} C ${points[1].x} ${points[1].y}, ${points[2].x} ${points[2].y}, ${points[3].x} ${points[3].y}`;

const cssPoint = (state: CssState, index: number): Point => {
  const origin = { x: 180, y: 780 };
  const width = 650;
  const height = 500;

  const source = [
    { x: 0, y: 0 },
    { x: state.x1, y: state.y1 },
    { x: state.x2, y: state.y2 },
    { x: 1, y: 1 },
  ][index];

  return {
    x: origin.x + source.x * width,
    y: origin.y - source.y * height,
  };
};

const cardTop = 205;
const cardHeight = 610;

const Panel: React.FC<{
  x: number;
  y: number;
  width: number;
  height: number;
  children: React.ReactNode;
}> = ({ x, y, width, height, children }) => (
  <div
    style={{
      position: "absolute",
      left: x,
      top: y,
      width,
      height,
      border: `1px solid ${colors.panelStroke}`,
      borderRadius: 16,
      background: colors.panel,
      boxShadow: "none",
    }}
  >
    {children}
  </div>
);

const ParamRow: React.FC<{
  label: string;
  value: number;
  color: string;
}> = ({ label, value, color }) => (
  <div
    style={{
      display: "grid",
      gridTemplateColumns: "64px 1fr 64px",
      alignItems: "center",
      columnGap: 14,
      fontFamily: "Consolas, SFMono-Regular, monospace",
      fontSize: 24,
      color: colors.ink,
    }}
  >
    <div style={{ color }}>{label}</div>
    <div
      style={{
        height: 14,
        borderRadius: 999,
        background: "rgba(125, 211, 252, 0.14)",
        overflow: "hidden",
        boxShadow: "inset 0 0 0 1px rgba(125, 211, 252, 0.20)",
      }}
    >
      <div
        style={{
          width: `${Math.max(0, Math.min(1, value)) * 100}%`,
          height: "100%",
          borderRadius: 999,
          background: color,
        }}
      />
    </div>
    <div style={{ color: colors.ink, textAlign: "right" }}>{cssNumber(value)}</div>
  </div>
);

const MappingLine: React.FC<{
  label: string;
  value: string;
  color: string;
}> = ({ label, value, color }) => (
  <div
    style={{
      display: "flex",
      alignItems: "baseline",
      justifyContent: "space-between",
      gap: 28,
      padding: "12px 22px",
      borderTop: "1px solid rgba(125, 211, 252, 0.14)",
      fontFamily:
        '"Smiley Sans", "Microsoft YaHei", Consolas, SFMono-Regular, monospace',
    }}
  >
    <div style={{ color, fontSize: 24 }}>{label}</div>
    <div style={{ color: colors.ink, fontSize: 25 }}>{value}</div>
  </div>
);

const PointLabel: React.FC<{
  point: Point;
  label: string;
  color: string;
  dx?: number;
  dy?: number;
}> = ({ point, label, color, dx = 0, dy = 0 }) => (
  <text
    x={point.x + dx}
    y={point.y + dy}
    fill={color}
    fontFamily="'Times New Roman', Times, serif"
    fontSize={30}
    fontStyle="italic"
    textAnchor="middle"
  >
    {label}
  </text>
);

const Sub: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <span
    style={{
      display: "inline-block",
      fontSize: "0.62em",
      lineHeight: 0,
      position: "relative",
      top: "0.22em",
    }}
  >
    {children}
  </span>
);

const Sup: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <span
    style={{
      display: "inline-block",
      fontSize: "0.62em",
      lineHeight: 0,
      position: "relative",
      top: "-0.48em",
    }}
  >
    {children}
  </span>
);

const ProgrammingLinksCards: React.FC = () => {
  const frame = useCurrentFrame();
  const sec = seconds(frame);
  const css = cssStateAt(sec);
  const t = markerAt(sec);

  const cssPoints = [0, 1, 2, 3].map((index) =>
    cssPoint(css, index),
  ) as [Point, Point, Point, Point];
  const cssMarker = cubic(cssPoints, t);
  const p1LabelDy = cssPoints[1].y > 720 ? -18 : 34;
  const p2LabelDy = cssPoints[2].y < 350 ? 42 : -18;
  const cubicText = `cubic-bezier(${cssNumber(css.x1)}, ${cssNumber(css.y1)}, ${cssNumber(css.x2)}, ${cssNumber(css.y2)});`;

  return (
    <>
      <Panel x={80} y={cardTop} width={820} height={cardHeight}>{null}</Panel>

      <Panel x={1020} y={cardTop} width={820} height={cardHeight}>
        <div
          style={{
            position: "absolute",
            left: 46,
            right: 46,
            top: 36,
          }}
        >
          <div
            style={{
              color: colors.amber,
              fontSize: 27,
              marginBottom: 10,
            }}
          >
            CSS 速度函数
          </div>
          <div
            style={{
              color: colors.ink,
              fontSize: 30,
              lineHeight: 1.25,
              whiteSpace: "nowrap",
              fontFamily: "Consolas, SFMono-Regular, monospace",
            }}
          >
            {cubicText}
          </div>
          <div
            style={{
              marginTop: 18,
              color: colors.amber,
              fontSize: 29,
            }}
          >
            四个参数对应两个控制点
          </div>
          <div
            style={{
              marginTop: 17,
              display: "grid",
              gap: 12,
            }}
          >
            <ParamRow label="x1" value={css.x1} color={colors.blue} />
            <ParamRow label="y1" value={css.y1} color={colors.mint} />
            <ParamRow label="x2" value={css.x2} color={colors.rose} />
            <ParamRow label="y2" value={css.y2} color={colors.purple} />
          </div>
          <div
            style={{
              marginTop: 18,
              border: "1px solid rgba(125, 211, 252, 0.16)",
              background: "rgba(5, 16, 29, 0.34)",
            }}
          >
            <MappingLine
              label="P1"
              value={`(${cssNumber(css.x1)}, ${cssNumber(css.y1)})`}
              color={colors.blue}
            />
            <MappingLine
              label="P2"
              value={`(${cssNumber(css.x2)}, ${cssNumber(css.y2)})`}
              color={colors.rose}
            />
            <MappingLine
              label="端点"
              value="P0=(0,0), P3=(1,1) 固定"
              color={colors.amber}
            />
          </div>
        </div>
      </Panel>

      <svg
        width={PROGRAMMING_LINKS_WIDTH}
        height={PROGRAMMING_LINKS_HEIGHT}
        style={{ position: "absolute", inset: 0 }}
      >
        <line
          x1={180}
          y1={780}
          x2={830}
          y2={780}
          stroke={colors.blue}
          strokeWidth={5}
        />
        <line
          x1={180}
          y1={780}
          x2={180}
          y2={280}
          stroke={colors.blue}
          strokeWidth={5}
        />
        <line
          x1={cssPoints[0].x}
          y1={cssPoints[0].y}
          x2={cssPoints[1].x}
          y2={cssPoints[1].y}
          stroke={colors.blue}
          strokeWidth={4}
        />
        <line
          x1={cssPoints[2].x}
          y1={cssPoints[2].y}
          x2={cssPoints[3].x}
          y2={cssPoints[3].y}
          stroke={colors.blue}
          strokeWidth={4}
        />
        <path
          d={pathFrom(cssPoints)}
          fill="none"
          stroke={colors.amber}
          strokeLinecap="round"
          strokeWidth={12}
        />
        {cssPoints.map((point, index) => (
          <circle
            key={`css-dot-${index}`}
            cx={point.x}
            cy={point.y}
            r={index === 0 || index === 3 ? 13 : 12}
            fill={index === 0 || index === 3 ? colors.amber : colors.blue}
          />
        ))}
        <circle cx={cssMarker.x} cy={cssMarker.y} r={13} fill={colors.rose} />
        <PointLabel point={cssPoints[0]} label="P₀" color={colors.amber} dx={-12} dy={34} />
        <PointLabel point={cssPoints[1]} label="P₁" color={colors.blue} dy={p1LabelDy} />
        <PointLabel point={cssPoints[2]} label="P₂" color={colors.blue} dy={p2LabelDy} />
        <PointLabel point={cssPoints[3]} label="P₃" color={colors.amber} dx={28} dy={-20} />
      </svg>

    </>
  );
};

export const ProgrammingLinksNative: React.FC = () => {
  const frame = useCurrentFrame();
  const sec = seconds(frame);
  const formulaOpacity = fade(sec, 21.5, 0.8);

  return (
    <AbsoluteFill
      style={{
        background: colors.bg,
        color: colors.ink,
        fontFamily: '"Smiley Sans", "Microsoft YaHei", sans-serif',
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: colors.bg,
        }}
      />

      <div
        style={{
          position: "absolute",
          top: 42,
          left: 0,
          width: "100%",
          textAlign: "center",
        }}
      >
        <div style={{ fontSize: 54, lineHeight: 1.05 }}>
          编程里的贝塞尔曲线
        </div>
        <div
          style={{
            color: colors.muted,
            fontSize: 29,
            marginTop: 12,
            letterSpacing: 0,
          }}
        >
          程序通常存控制点，再按公式算路径
        </div>
      </div>

      <ProgrammingLinksCards />

      <div
        style={{
          position: "absolute",
          left: 90,
          right: 90,
          bottom: 34,
          opacity: formulaOpacity,
          textAlign: "center",
          textShadow: "0 3px 18px rgba(0, 0, 0, 0.72)",
        }}
      >
        <div
          style={{
            fontFamily: "'Times New Roman', Times, serif",
            fontStyle: "italic",
            fontSize: 46,
            color: colors.ink,
          }}
        >
          B(t) = (1−t)<Sup>3</Sup>P<Sub>0</Sub> + 3(1−t)
          <Sup>2</Sup>tP<Sub>1</Sub> + 3(1−t)t<Sup>2</Sup>P
          <Sub>2</Sub> + t<Sup>3</Sup>P<Sub>3</Sub>
        </div>
        <div style={{ marginTop: 10, color: colors.muted, fontSize: 27 }}>
          存下控制点，运行时按公式算出曲线上的位置。
        </div>
        <div style={{ marginTop: 6, color: colors.amber, fontSize: 26 }}>
          CSS 缓动、图形路径和交互动画，底层都在复用这套控制点规则。
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const ProgrammingLinksOverlay: React.FC = () => (
  <AbsoluteFill
    style={{
      background: "transparent",
      color: colors.ink,
      fontFamily: '"Smiley Sans", "Microsoft YaHei", sans-serif',
      overflow: "hidden",
    }}
  >
    <ProgrammingLinksCards />
  </AbsoluteFill>
);
