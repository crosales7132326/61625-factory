import React from 'react';
import {AbsoluteFill, Video, staticFile} from 'remotion';

interface VideoBackgroundProps {
  src?: string;
}

export const VideoBackground: React.FC<VideoBackgroundProps> = ({src = 'backgrounds/default.mp4'}) => {
  return (
    <AbsoluteFill>
      <Video
        src={staticFile(src)}
        loop
        muted
        style={{objectFit: 'cover', width: '100%', height: '100%'}}
      />
    </AbsoluteFill>
  );
};
