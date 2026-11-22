import type {FC} from 'react';
import {CistyFilm, ConversationShot, FilterShot, OpeningShot, OutroShot, StationShot} from './CistyFilm';
import {FPS, HEIGHT, SHOTS, TOTAL_FRAMES, WIDTH} from './timeline';

const shot = (key: keyof typeof SHOTS, component: FC<Record<string, unknown>>) => ({
  id: key,
  label: SHOTS[key].label,
  from: SHOTS[key].from,
  duration: SHOTS[key].duration,
  component,
});

export const WORKBENCH = {
  name: 'Cisty · Apply with clarity',
  fps: FPS,
  width: WIDTH,
  height: HEIGHT,
  total: TOTAL_FRAMES,
  background: '#F7F3EC',
  shots: [
    shot('opening', OpeningShot as FC<Record<string, unknown>>),
    shot('filter', FilterShot as FC<Record<string, unknown>>),
    shot('station', StationShot as FC<Record<string, unknown>>),
    shot('conversation', ConversationShot as FC<Record<string, unknown>>),
    shot('outro', OutroShot as FC<Record<string, unknown>>),
  ],
  transitions: [],
  captions: [],
  overlays: [],
  sfx: [
    {from: 178, duration: 52, src: 'audio/sfx/fs-813214.mp3', volume: 0.55},
    {from: 330, duration: 8, src: 'audio/sfx/fs-878248.mp3', volume: 0.24},
    {from: 672, duration: 18, src: 'audio/sfx/fs-879272.mp3', volume: 0.18},
  ],
  music: [{from: 0, duration: TOTAL_FRAMES, src: 'audio/cat-walk.mp3', volume: 0.22}],
  order: ['captions', 'overlays'] as const,
  original: CistyFilm as FC<Record<string, unknown>>,
};
