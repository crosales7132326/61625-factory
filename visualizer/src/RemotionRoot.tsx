import React from 'react';
import {Composition} from 'remotion';
import {StoryVideo} from './StoryVideo';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="StoryVideo"
        component={StoryVideo}
        durationInFrames={30 * 170} // cap at 2m50s for shorts
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          storyText: "",
          audioFile: ""
        }}
      />
    </>
  );
};
