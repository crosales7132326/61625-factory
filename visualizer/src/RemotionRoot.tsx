import React from 'react';
import {Composition} from 'remotion';
import {StoryVideo} from './StoryVideo';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="StoryVideo"
        component={StoryVideo}
        durationInFrames={1800} // 60 seconds at 30fps
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          storyText: "Default story text for preview",
          audioFile: "default.wav"
        }}
      />
    </>
  );
};
