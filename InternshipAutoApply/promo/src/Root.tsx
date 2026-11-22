import React from 'react';
import {Composition} from 'remotion';
import {CistyFilm} from './CistyFilm';
import {FPS, HEIGHT, TOTAL_FRAMES, WIDTH} from './timeline';

export const Root: React.FC = () => (
  <>
    <Composition id="CistyPromo" component={CistyFilm} durationInFrames={TOTAL_FRAMES} fps={FPS} width={WIDTH} height={HEIGHT} defaultProps={{music: true}} />
    <Composition id="CistyPromoClean" component={CistyFilm} durationInFrames={TOTAL_FRAMES} fps={FPS} width={WIDTH} height={HEIGHT} defaultProps={{music: false}} />
  </>
);
