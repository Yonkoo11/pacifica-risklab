import React from 'react';
import { Composition } from 'remotion';
import { HookScene } from './HookScene';
import { CascadeScene } from './CascadeScene';
import { CompareScene } from './CompareScene';

export const Root: React.FC = () => {
  return (
    <>
      <Composition
        id="Hook"
        component={HookScene}
        durationInFrames={90}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="Cascade"
        component={CascadeScene}
        durationInFrames={330}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="Compare"
        component={CompareScene}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
