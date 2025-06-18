import React from 'react';
import {
  AbsoluteFill,
  Audio,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {VideoBackground} from './VideoBackground';

interface StoryVideoProps {
  storyText: string;
  audioFile: string;
}

export const StoryVideo: React.FC<StoryVideoProps> = ({storyText, audioFile}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const words = storyText.split(' ');
  const wordsPerSecond = 2.5;
  const framesPerWord = fps / wordsPerSecond;

  return (
    <AbsoluteFill>
      <VideoBackground />
      {audioFile && <Audio src={staticFile(audioFile)} />}
      <AbsoluteFill
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          padding: '120px',
          textAlign: 'center',
        }}
      >
        <div
          style={{
            fontSize: 64,
            fontWeight: 'bold',
            lineHeight: 1.2,
            color: '#fff',
            textShadow: '0 0 20px #000',
          }}
        >
          {words.map((word, i) => {
            const start = i * framesPerWord;
            const end = (i + 1) * framesPerWord;
            const opacity = interpolate(
              frame,
              [start, start + 5, end - 5, end],
              [0, 1, 1, 0],
              {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              },
            );
            const scale = interpolate(
              frame,
              [start, start + 5, end],
              [0.8, 1, 1],
              {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
            );
            return (
              <span
                key={i}
                style={{
                  marginRight: '0.35em',
                  opacity,
                  transform: `scale(${scale})`,
                  display: 'inline-block',
                }}
              >
                {word}
              </span>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
