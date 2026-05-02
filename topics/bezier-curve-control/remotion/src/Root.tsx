import "./index.css";
import { Composition } from "remotion";
import {
  BezierRemotionPreview,
  FPS,
  HEIGHT,
  TOTAL_FRAMES,
  WIDTH,
} from "./Composition";
import {
  PROGRAMMING_LINKS_FPS,
  PROGRAMMING_LINKS_FRAMES,
  PROGRAMMING_LINKS_HEIGHT,
  PROGRAMMING_LINKS_WIDTH,
  ProgrammingLinksNative,
  ProgrammingLinksOverlay,
} from "./ProgrammingLinksNative";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="BezierRemotionPreview"
        component={BezierRemotionPreview}
        durationInFrames={TOTAL_FRAMES}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="ProgrammingLinksNative1080"
        component={ProgrammingLinksNative}
        durationInFrames={PROGRAMMING_LINKS_FRAMES}
        fps={PROGRAMMING_LINKS_FPS}
        width={PROGRAMMING_LINKS_WIDTH}
        height={PROGRAMMING_LINKS_HEIGHT}
      />
      <Composition
        id="ProgrammingLinksOverlay1080"
        component={ProgrammingLinksOverlay}
        durationInFrames={PROGRAMMING_LINKS_FRAMES}
        fps={PROGRAMMING_LINKS_FPS}
        width={PROGRAMMING_LINKS_WIDTH}
        height={PROGRAMMING_LINKS_HEIGHT}
      />
    </>
  );
};
