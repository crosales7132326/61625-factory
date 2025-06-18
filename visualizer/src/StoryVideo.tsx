import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  staticFile,
} from 'remotion';

interface StoryVideoProps {
  storyText: string;
  audioFile: string;
}

export const StoryVideo: React.FC<StoryVideoProps> = ({storyText, audioFile}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  
  const words = storyText.split(' ');
  const wordsPerSecond = 2.5; // Adjust based on speech speed
  const framesPerWord = fps / wordsPerSecond;
  
  const backgroundOpacity = interpolate(frame, [0, 30], [0, 0.7], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {/* Background Video Placeholder */}
      <AbsoluteFill
        style={{
          background: 'linear-gradient(45deg, #1a1a2e, #16213e, #0f3460)',
          opacity: backgroundOpacity,
        }}
      />
      
      {/* Audio */}
      <Audio src={staticFile(audioFile)} />
      
      {/* Captions Container */}
      <AbsoluteFill
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          padding: '100px 60px',
        }}
      >
        <div
          style={{
            fontSize: '48px',
            fontWeight: 'bold',
            color: '#ffffff',
            textAlign: 'center',
            lineHeight: '1.4',
            textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
            fontFamily: 'Arial, sans-serif',
          }}
        >
          {words.map((word, index) => {
            const wordStartFrame = index * framesPerWord;
            const wordEndFrame = (index + 1) * framesPerWord;
            
            const isVisible = frame >= wordStartFrame && frame < wordEndFrame + 30;
            
            const bounceScale = interpolate(
              frame,
              [wordStartFrame, wordStartFrame + 10, wordStartFrame + 20],
              [1, 1.2, 1],
              {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              }
            );
            
            const isCurrentWord = frame >= wordStartFrame && frame < wordEndFrame;
            
            return (
              <span
                key={index}
                style={{
                  display: 'inline-block',
                  margin: '0 8px',
                  transform: isCurrentWord ? `scale(${bounceScale})` : 'scale(1)',
                  color: isCurrentWord ? '#ffff00' : '#ffffff',
                  opacity: isVisible ? 1 : 0.3,
                  transition: 'all 0.1s ease',
                }}
              >
                {word}
              </span>
            );
          })}
        </div>
      </AbsoluteFill>
      
      {/* Subtle overlay for better text readability */}
      <AbsoluteFill
        style={{
          background: 'linear-gradient(to bottom, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.1) 50%, rgba(0,0,0,0.3) 100%)',
        }}
      />
    </AbsoluteFill>
  );
};
