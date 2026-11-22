export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;

export const SHOTS = {
  opening: {from: 0, duration: 150, label: 'C mark stroke build'},
  filter: {from: 150, duration: 180, label: 'Type and filter'},
  station: {from: 330, duration: 150, label: 'Saved nearest station'},
  conversation: {from: 480, duration: 150, label: 'Tracked system conversation'},
  outro: {from: 630, duration: 180, label: 'UI to brand outro'},
} as const;

export const TOTAL_FRAMES = 810;
