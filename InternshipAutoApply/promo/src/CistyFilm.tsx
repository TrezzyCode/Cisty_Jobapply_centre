import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import {SHOTS, TOTAL_FRAMES} from './timeline';

const C = {
  ivory: '#F7F3EC',
  paper: '#FFFDF9',
  ink: '#2B2724',
  muted: '#756C66',
  accent: '#B75334',
  soft: '#EED8CB',
  line: '#DFD2C6',
};
const FONT = '"Segoe UI", system-ui, -apple-system, sans-serif';
const EASE = Easing.bezier(0.23, 1, 0.32, 1);
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const ramp = (frame: number, start: number, duration: number, easing = EASE) =>
  interpolate(frame, [start, start + duration], [0, 1], {...clamp, easing});

const sceneOpacity = (frame: number, duration: number) =>
  interpolate(frame, [0, 4, duration - 5, duration - 1], [0.15, 1, 1, 0.15], clamp);

const WarmStage: React.FC<{children?: React.ReactNode}> = ({children}) => (
  <AbsoluteFill style={{background: C.ivory, color: C.ink, fontFamily: FONT, overflow: 'hidden'}}>
    <AbsoluteFill style={{background: 'radial-gradient(circle at 79% 10%, rgba(183,83,52,.11), transparent 34%), radial-gradient(circle at 12% 86%, rgba(117,88,72,.08), transparent 38%)'}} />
    <svg width="1920" height="1080" style={{position: 'absolute', inset: 0, opacity: 0.34}}>
      <path d="M-80 875 C 330 720, 560 980, 930 790 S 1510 840, 2020 620" fill="none" stroke={C.accent} strokeWidth="2" />
      {[310, 720, 1110, 1510].map((x, i) => <circle key={i} cx={x} cy={[810, 857, 754, 744][i]} r="6" fill={C.ivory} stroke={C.accent} strokeWidth="2" />)}
    </svg>
    {children}
  </AbsoluteFill>
);

const CistyMark: React.FC<{size?: number; progress?: number; fill?: boolean}> = ({size = 300, progress = 1, fill = true}) => {
  const draw = Math.max(0, Math.min(1, progress));
  return (
    <svg width={size} height={size} viewBox="0 0 1000 1000" style={{overflow: 'visible', filter: 'drop-shadow(0 28px 50px rgba(104,54,35,.16))'}}>
      <path
        d="M800 120H320C190 120 120 190 120 320v360c0 130 70 200 200 200h480c55 0 95-30 110-75l-70-155c-15 50-40 80-100 80H350c-50 0-80-30-80-80V350c0-50 30-80 80-80h390c60 0 85 30 100 80l70-155c-15-45-55-75-110-75Z"
        pathLength={1}
        fill={fill ? C.accent : 'none'}
        fillOpacity={fill ? ramp(draw, 0.62, 0.3) : 0}
        stroke={C.accent}
        strokeWidth={fill ? 18 : 30}
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeDasharray="1 1"
        strokeDashoffset={1 - draw}
      />
    </svg>
  );
};

const Headline: React.FC<{eyebrow: string; title: string; body?: string; align?: 'left' | 'center'}> = ({eyebrow, title, body, align = 'left'}) => (
  <div style={{textAlign: align, maxWidth: 1160}}>
    <div style={{fontSize: 32, fontWeight: 700, letterSpacing: '.14em', textTransform: 'uppercase', color: C.accent}}>{eyebrow}</div>
    <div style={{fontSize: 64, fontWeight: 720, lineHeight: 1.05, letterSpacing: '-.04em', marginTop: 18, whiteSpace: 'pre-line'}}>{title}</div>
    {body ? <div style={{fontSize: 32, lineHeight: 1.3, color: C.muted, marginTop: 16}}>{body}</div> : null}
  </div>
);

const ProductFrame: React.FC<{src: string; transform?: string; opacity?: number}> = ({src, transform = 'none', opacity = 1}) => (
  <div style={{position: 'absolute', left: 92, top: 70, width: 1736, height: 976, borderRadius: 34, overflow: 'hidden', border: `1px solid ${C.line}`, boxShadow: '0 46px 110px rgba(67,46,33,.18)', background: C.paper, transform, opacity, transformOrigin: '50% 50%'}}>
    <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', display: 'block'}} />
    <div style={{position: 'absolute', inset: 0, boxShadow: 'inset 0 1px rgba(255,255,255,.9)', pointerEvents: 'none'}} />
  </div>
);

export const OpeningShot: React.FC = () => {
  const f = useCurrentFrame();
  const draw = ramp(f, 12, 64);
  const markIn = ramp(f, 6, 20);
  const copy = ramp(f, 72, 24);
  const hold = sceneOpacity(f, SHOTS.opening.duration);
  return (
    <WarmStage>
      <AbsoluteFill style={{opacity: hold}}>
        <div style={{position: 'absolute', left: 440, top: 260, transform: `scale(${0.94 + 0.06 * markIn})`}}><CistyMark size={360} progress={draw} /></div>
        <div style={{position: 'absolute', left: 850, top: 310, opacity: copy, transform: `translateY(${18 * (1 - copy)}px)`}}>
          <div style={{fontSize: 142, lineHeight: 1, fontWeight: 740, letterSpacing: '-.06em'}}>Cisty</div>
          <div style={{fontSize: 36, color: C.muted, marginTop: 28}}>Your internship search,<br />in one calm workspace.</div>
          <div style={{fontSize: 32, color: C.accent, letterSpacing: '.18em', marginTop: 26, textTransform: 'uppercase'}}>by Trez</div>
        </div>
      </AbsoluteFill>
    </WarmStage>
  );
};

export const FilterShot: React.FC = () => {
  const f = useCurrentFrame();
  const typed = Math.max(0, Math.min('Meridian'.length, Math.floor((f - 28) / 4) + 1));
  const filtered = ramp(f, 84, 16);
  const camera = ramp(f, 0, SHOTS.filter.duration);
  const focus = ramp(f, 14, 14) * (1 - ramp(f, 112, 12));
  const pointer = ramp(f, 64, 18);
  return (
    <WarmStage>
      <AbsoluteFill style={{opacity: sceneOpacity(f, SHOTS.filter.duration)}}>
        <ProductFrame src="captures/applications-all.png" transform={`scale(${1.015 + camera * 0.025}) translateY(${camera * 7}px)`} opacity={1 - filtered} />
        <ProductFrame src="captures/applications-filtered.png" transform={`scale(${1.015 + camera * 0.025}) translateY(${camera * 7}px)`} opacity={filtered} />
        <div style={{position: 'absolute', left: 1220, top: 88, width: 560, height: 46, borderRadius: 14, background: 'rgba(255,253,249,.96)', border: `2px solid rgba(183,83,52,${0.2 + focus * 0.55})`, boxShadow: `0 0 0 6px rgba(183,83,52,${focus * 0.12})`, display: 'flex', alignItems: 'center', padding: '0 18px', fontSize: 24}}>
          <span>{'Meridian'.slice(0, typed)}</span><span style={{width: 2, height: 26, background: C.accent, marginLeft: 3, opacity: f < 92 ? 1 : Math.floor(f / 7) % 2}}> </span>
        </div>
        <div style={{position: 'absolute', left: 132, top: 132, padding: '30px 36px', borderRadius: 28, background: 'rgba(255,253,249,.92)', border: `1px solid ${C.line}`, boxShadow: '0 28px 70px rgba(70,48,34,.14)', opacity: ramp(f, 6, 18), transform: `translateY(${18 * (1 - ramp(f, 6, 18))}px)`}}>
          <Headline eyebrow="Search with context" title={'Import once.\nFilter what matters.'} body="Industry · region · transit line" />
        </div>
        <div style={{position: 'absolute', left: 1740 - 280 * pointer, top: 168 + 250 * pointer, fontSize: 54, color: C.ink, transform: `rotate(-18deg) scale(${1 - 0.08 * ramp(f, 84, 5)})`, filter: 'drop-shadow(0 5px 6px rgba(50,35,25,.25))'}}>↖</div>
      </AbsoluteFill>
    </WarmStage>
  );
};

const FactCard: React.FC<{label: string; value: string; cue: number; x: number}> = ({label, value, cue, x}) => {
  const f = useCurrentFrame();
  const p = ramp(f, cue, 24, Easing.bezier(0.25, 0.9, 0.3, 1.08));
  return (
    <div style={{position: 'absolute', left: x, top: 720, width: 330, height: 210, borderRadius: 28, background: 'rgba(255,253,249,.96)', border: `1px solid ${C.line}`, boxShadow: `0 ${28 * (1 - p) + 14}px ${60 - 24 * p}px rgba(65,44,30,.18)`, padding: '26px 30px', transform: `perspective(900px) translateY(${-100 * (1 - p)}px) rotateX(${16 * (1 - p)}deg) scale(${0.96 + 0.04 * p})`, opacity: ramp(f, cue, 7)}}>
      <div style={{fontSize: 32, letterSpacing: '.08em', textTransform: 'uppercase', color: C.accent, fontWeight: 700}}>{label}</div>
      <div style={{fontSize: 42, fontWeight: 700, marginTop: 15, letterSpacing: '-.03em'}}>{value}</div>
    </div>
  );
};

export const StationShot: React.FC = () => {
  const f = useCurrentFrame();
  const z = ramp(f, 0, SHOTS.station.duration);
  return (
    <WarmStage>
      <AbsoluteFill style={{opacity: sceneOpacity(f, SHOTS.station.duration)}}>
        <ProductFrame src="captures/station-detail.png" transform={`translateX(${-80 * z}px) scale(${1.02 + 0.06 * z})`} />
        <div style={{position: 'absolute', left: 120, top: 108, padding: '28px 34px', borderRadius: 28, background: 'rgba(255,253,249,.94)', border: `1px solid ${C.line}`, boxShadow: '0 28px 70px rgba(70,48,34,.14)', opacity: ramp(f, 4, 18)}}>
          <Headline eyebrow="Route intelligence" title={'Nearest station,\nalready calculated.'} body="Saved automatically. Recalculate to overwrite." />
        </div>
        <FactCard label="Nearest station" value="Ampang Park" cue={26} x={700} />
        <FactCard label="Straight-line" value="240 m" cue={38} x={1050} />
        <FactCard label="Verified walk" value="3 min" cue={49} x={1400} />
      </AbsoluteFill>
    </WarmStage>
  );
};

const MessagePill: React.FC<{cue: number; top: number; kicker: string; body: string; accent?: boolean}> = ({cue, top, kicker, body, accent}) => {
  const f = useCurrentFrame();
  const p = ramp(f, cue, 24, Easing.bezier(0.3, 1.12, 0.45, 1));
  return (
    <div style={{position: 'absolute', left: 160, top, width: 710, minHeight: 132, padding: '24px 28px', borderRadius: 26, background: accent ? C.accent : 'rgba(255,253,249,.96)', color: accent ? '#fff' : C.ink, border: `1px solid ${accent ? C.accent : C.line}`, boxShadow: '0 24px 60px rgba(62,43,30,.16)', transform: `translateY(${44 * (1 - p)}px) scale(${0.88 + 0.12 * p})`, opacity: ramp(f, cue, 10)}}>
      <div style={{fontSize: 32, fontWeight: 750, letterSpacing: '.12em', textTransform: 'uppercase', opacity: .82}}>{kicker}</div>
      <div style={{fontSize: 36, lineHeight: 1.2, marginTop: 10, fontWeight: 620}}>{body}</div>
    </div>
  );
};

export const ConversationShot: React.FC = () => {
  const f = useCurrentFrame();
  const z = ramp(f, 0, SHOTS.conversation.duration);
  return (
    <WarmStage>
      <AbsoluteFill style={{opacity: sceneOpacity(f, SHOTS.conversation.duration)}}>
        <ProductFrame src="captures/conversation.png" transform={`translateX(${-175 * z}px) scale(${1.02 + 0.08 * z})`} />
        <div style={{position: 'absolute', left: 102, top: 80, width: 840, padding: '28px 34px 32px', borderRadius: 28, background: 'rgba(255,253,249,.94)', border: `1px solid ${C.line}`, boxShadow: '0 28px 70px rgba(70,48,34,.14)', opacity: ramp(f, 5, 18)}}>
          <Headline eyebrow="One private thread" title={'Follow every reply.\nOnly the ones Cisty sent.'} />
        </div>
        <MessagePill cue={42} top={470} kicker="You sent" body="Application for Software Internship" />
        <MessagePill cue={56} top={620} kicker="They replied" body="Interview invitation received" accent />
        <MessagePill cue={70} top={770} kicker="System only" body="Unrelated inbox mail stays private" />
      </AbsoluteFill>
    </WarmStage>
  );
};

export const OutroShot: React.FC = () => {
  const f = useCurrentFrame();
  const collapse = ramp(f, 0, 42, Easing.in(Easing.cubic));
  const bloom = ramp(f, 36, 34, Easing.bezier(0.2, 1.12, 0.35, 1));
  const shift = ramp(f, 78, 24);
  const word = 'Cisty';
  return (
    <WarmStage>
      <AbsoluteFill style={{opacity: sceneOpacity(f, SHOTS.outro.duration)}}>
        <div style={{position: 'absolute', left: 960, top: 500, width: 1736, height: 976, borderRadius: 34, overflow: 'hidden', border: `1px solid ${C.line}`, boxShadow: '0 40px 100px rgba(67,46,33,.16)', transform: `translate(-50%,-50%) scale(${1 - 0.9 * collapse}, ${1 - 0.96 * collapse})`, opacity: 1 - ramp(f, 28, 18)}}>
          <Img src={staticFile('captures/conversation.png')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        </div>
        <div style={{position: 'absolute', left: 960 - 300 * shift, top: 470, transform: `translate(-50%,-50%) scaleX(${0.04 + 0.96 * bloom})`, opacity: ramp(f, 34, 8)}}>
          <CistyMark size={330} progress={1} />
        </div>
        <div style={{position: 'absolute', left: 900, top: 380, display: 'flex', opacity: shift}}>
          {word.split('').map((ch, i) => {
            const p = ramp(f, 90 + i * 4, 18, Easing.bezier(0.25, 1.08, 0.35, 1));
            return <span key={i} style={{display: 'inline-block', fontSize: 154, lineHeight: 1, fontWeight: 740, letterSpacing: '-.065em', transform: `scale(${1.7 - 0.7 * p})`, transformOrigin: '50% 80%', filter: p < .98 ? `blur(${(1 - p) * 12}px)` : undefined, opacity: ramp(f, 90 + i * 4, 7)}}>{ch}</span>;
          })}
        </div>
        <div style={{position: 'absolute', left: 900, top: 575, width: 690, opacity: ramp(f, 118, 22), transform: `translateY(${16 * (1 - ramp(f, 118, 22))}px)`}}>
          <div style={{fontSize: 42, color: C.muted}}>Apply with clarity.</div>
          <div style={{fontSize: 32, color: C.accent, letterSpacing: '.18em', textTransform: 'uppercase', marginTop: 24}}>by Trez</div>
        </div>
      </AbsoluteFill>
    </WarmStage>
  );
};

export const CistyFilm: React.FC<{music?: boolean}> = ({music = true}) => (
  <AbsoluteFill style={{backgroundColor: C.ivory}}>
    <Sequence from={SHOTS.opening.from} durationInFrames={SHOTS.opening.duration}><OpeningShot /></Sequence>
    <Sequence from={SHOTS.filter.from} durationInFrames={SHOTS.filter.duration}><FilterShot /></Sequence>
    <Sequence from={SHOTS.station.from} durationInFrames={SHOTS.station.duration}><StationShot /></Sequence>
    <Sequence from={SHOTS.conversation.from} durationInFrames={SHOTS.conversation.duration}><ConversationShot /></Sequence>
    <Sequence from={SHOTS.outro.from} durationInFrames={SHOTS.outro.duration}><OutroShot /></Sequence>
    <Sequence from={178} durationInFrames={52}><Audio src={staticFile('audio/sfx/fs-813214.mp3')} endAt={52} volume={0.55} /></Sequence>
    <Sequence from={330} durationInFrames={8}><Audio src={staticFile('audio/sfx/fs-878248.mp3')} volume={0.24} /></Sequence>
    <Sequence from={672} durationInFrames={18}><Audio src={staticFile('audio/sfx/fs-879272.mp3')} volume={0.18} /></Sequence>
    {music ? <Audio src={staticFile('audio/cat-walk.mp3')} startFrom={120} endAt={120 + TOTAL_FRAMES} volume={(frame) => interpolate(frame, [0, 30, TOTAL_FRAMES - 45, TOTAL_FRAMES], [0, .22, .22, 0], clamp)} /> : null}
  </AbsoluteFill>
);
