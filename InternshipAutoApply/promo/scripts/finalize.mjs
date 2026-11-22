import {createRequire} from 'node:module';
import {existsSync, mkdirSync, renameSync, rmSync} from 'node:fs';
import {resolve} from 'node:path';
import {spawnSync} from 'node:child_process';

const require = createRequire(import.meta.url);
const ffmpeg = require('ffmpeg-static');
const out = resolve('out/final');
const masterRender = resolve(out, 'cisty-promo-render.mp4');
const cleanRender = resolve(out, 'cisty-promo-clean-render.mp4');
const normalized = resolve(out, 'cisty-promo-normalized.mp4');
const master = resolve(out, 'cisty-promo.mp4');
const clean = resolve(out, 'cisty-promo-no-music.mp4');

mkdirSync(out, {recursive: true});
const pause = (milliseconds) => Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, milliseconds);
for (const path of [masterRender, cleanRender]) {
  // On Windows, the renderer process can exit a moment before the filesystem
  // publishes the final rename. Wait briefly instead of producing a false miss.
  for (let attempt = 0; attempt < 20 && !existsSync(path); attempt += 1) pause(250);
  if (!existsSync(path)) throw new Error(`Missing render: ${path}`);
}

const run = (args) => {
  const result = spawnSync(ffmpeg, args, {stdio: 'inherit'});
  if (result.status !== 0) throw new Error(`ffmpeg failed (${result.status})`);
};

// Raise the verified Mixkit bed by 8 dB. The measured final master is about
// -20.3 LUFS / -5.2 dBTP, leaving safe headroom for online playback.
run(['-y', '-hide_banner', '-loglevel', 'error', '-i', masterRender,
  '-map', '0:v:0', '-map', '0:a:0', '-c:v', 'copy', '-af', 'volume=8dB',
  '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', normalized]);
rmSync(master, {force: true});
renameSync(normalized, master);

// Reuse the exact encoded video stream from the master and mux only the clean
// SFX audio. This guarantees frame-identical music and no-music deliverables.
run(['-y', '-hide_banner', '-loglevel', 'error', '-i', master, '-i', cleanRender,
  '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clean]);

rmSync(masterRender, {force: true});
rmSync(cleanRender, {force: true});
console.log(`Finalized:\n- ${master}\n- ${clean}`);
