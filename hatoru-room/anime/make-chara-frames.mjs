// 部屋の静止画から、キャラクターだけが動く24コマを作り、4x6 のグリッド画像にする
// 使い方: node charanim.mjs <hatoru-room フォルダ> <出力フォルダ> [preview]
const { default: sharp } = await import('file:///C:/Users/81802/Desktop/claude-test/アプリ/おかたずけアプリ/node_modules/sharp/lib/index.js');
import fs from 'node:fs';
import path from 'node:path';

const [ROOM, OUT, PREVIEW] = process.argv.slice(2);
const N = 24;            // コマ数（200msごと → 4.8秒で1周）
const W = 1280, H = 853; // 元の静止画
const CW = 480, CH = 320; // 1コマ
const TAU = Math.PI * 2;

// 状態ごとの動き（座標は元画像 1280x853 の px）
// body: 体の楕円（中心 cx,cy・半径 rx,ry）。下端を固定して少し伸び縮みさせる（呼吸・ゆれ）
const SCENES = {
  sleeping: { body: { cx: 300, cy: 470, rx: 200, ry: 150 }, breath: 0.035, sway: 0, zzz: { x: 300, y: 345 }, glow: { x: 580, y: 300, r: 95 } },
  working: { body: { cx: 632, cy: 360, rx: 175, ry: 215 }, breath: 0.026, sway: 4, dots: { x: 800, y: 175 }, screen: { x: 505, y: 405, r: 70 } },
  thinking: { body: { cx: 664, cy: 690, rx: 150, ry: 155 }, breath: 0.026, sway: 3, thought: { x: 683, y: 140 } },
  researching: { body: { cx: 779, cy: 430, rx: 180, ry: 240 }, breath: 0.024, sway: 4, spark: { x: 905, y: 250 } },
};

const ease = (t) => (1 - Math.cos(TAU * t)) / 2; // 0→1→0 を1周

function ellipseMask(w, h, feather) {
  const rx = w / 2 - feather, ry = h / 2 - feather;
  return Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}">
    <defs><filter id="f" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="${feather / 2}"/></filter></defs>
    <rect width="100%" height="100%" fill="black"/>
    <ellipse cx="${w / 2}" cy="${h / 2}" rx="${rx}" ry="${ry}" fill="white" filter="url(#f)"/></svg>`);
}

// 体の楕円を、下端を固定して縦に s 倍・横に少しゆらして重ねる
async function bodyLayer(base, b, s, dx) {
  const left = Math.round(b.cx - b.rx), top = Math.round(b.cy - b.ry);
  const w = Math.round(b.rx * 2), h = Math.round(b.ry * 2);
  const nh = Math.round(h * s), nw = Math.round(w * (1 + (s - 1) * 0.35));
  const rgb = await sharp(base).extract({ left, top, width: w, height: h }).resize(nw, nh, { fit: 'fill' }).removeAlpha().toBuffer();
  const mask = await sharp(ellipseMask(nw, nh, 26)).greyscale().extractChannel(0).toBuffer();
  const rgba = await sharp(rgb).joinChannel(mask).png().toBuffer();
  return { input: rgba, left: Math.round(left - (nw - w) / 2 + dx), top: top - (nh - h) };
}

function svgLayer(body) {
  return { input: Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">${body}</svg>`), left: 0, top: 0 };
}

function overlays(sc, i) {
  const t = i / N;
  let s = '';
  if (sc.glow) { // ランプのあかりが、ほんのり明るくなったり暗くなったり
    const a = 0.10 + 0.12 * ease(t);
    s += `<defs><radialGradient id="g"><stop offset="0" stop-color="#ffd27a" stop-opacity="${a}"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient></defs>
      <circle cx="${sc.glow.x}" cy="${sc.glow.y}" r="${sc.glow.r * 2.2}" fill="url(#g)"/>`;
  }
  if (sc.zzz) { // Z が3つ、時間差で右上へ浮かびながら消える
    for (let k = 0; k < 3; k++) {
      const p = ((t + k / 3) % 1);
      const x = sc.zzz.x + p * 140, y = sc.zzz.y - p * 190;
      const size = 46 + p * 46, op = Math.min(1, p * 4) * (1 - p);
      s += `<text x="${x}" y="${y}" font-family="Arial Rounded MT Bold, Arial, sans-serif" font-weight="700" font-size="${size}" fill="#5b6fb0" fill-opacity="${op.toFixed(3)}" stroke="#ffffff" stroke-opacity="${(op * 0.8).toFixed(3)}" stroke-width="3" paint-order="stroke">Z</text>`;
    }
  }
  if (sc.screen) { // パソコンの画面が、打つたびに少しちらつく
    const a = 0.10 + 0.10 * (Math.sin(TAU * t * 6) * 0.5 + 0.5);
    s += `<defs><radialGradient id="sg"><stop offset="0" stop-color="#cfe6ff" stop-opacity="${a.toFixed(3)}"/><stop offset="1" stop-color="#cfe6ff" stop-opacity="0"/></radialGradient></defs>
      <circle cx="${sc.screen.x}" cy="${sc.screen.y}" r="${sc.screen.r * 1.6}" fill="url(#sg)"/>`;
  }
  if (sc.dots) { // 小さな吹き出しの「・・・」が順番に点く（入力中）
    const { x, y } = sc.dots;
    s += `<g opacity="0.95"><rect x="${x - 58}" y="${y - 30}" width="116" height="56" rx="28" fill="#ffffff" stroke="#e2d6c3" stroke-width="3"/>
      <path d="M ${x - 30} ${y + 22} l -16 22 l 30 -18 z" fill="#ffffff" stroke="#e2d6c3" stroke-width="3" stroke-linejoin="round"/>
      <rect x="${x - 30}" y="${y + 16}" width="40" height="8" fill="#ffffff"/>`;
    const lit = Math.floor(t * 8) % 4; // 0..3 個
    for (let k = 0; k < 3; k++) s += `<circle cx="${x - 30 + k * 30}" cy="${y - 2}" r="9" fill="${k < lit ? '#8a6b4a' : '#e8dccb'}"/>`;
    s += `</g>`;
  }
  if (sc.thought) { // 考えごとの雲の中で「・・・」→「？」が順番に出る
    const { x, y } = sc.thought;
    const phase = Math.floor(t * 4); // 4段階
    if (phase < 3) {
      for (let k = 0; k <= phase; k++) s += `<circle cx="${x - 40 + k * 40}" cy="${y + 5}" r="11" fill="#9a8466"/>`;
    } else {
      const sc2 = 1 + 0.08 * Math.sin(TAU * (t * 4 % 1));
      s += `<text x="${x}" y="${y + 30}" text-anchor="middle" font-family="Arial Rounded MT Bold, Arial, sans-serif" font-weight="700" font-size="${Math.round(84 * sc2)}" fill="#9a8466">?</text>`;
    }
  }
  if (sc.spark) { // ひらめきのキラッ（ときどき）
    const p = (t * 2) % 1;
    const op = Math.sin(Math.PI * p);
    const r = 38 + 18 * p;
    const { x, y } = sc.spark;
    const star = (cx, cy, rr) => `M ${cx} ${cy - rr} Q ${cx} ${cy} ${cx + rr} ${cy} Q ${cx} ${cy} ${cx} ${cy + rr} Q ${cx} ${cy} ${cx - rr} ${cy} Q ${cx} ${cy} ${cx} ${cy - rr} Z`;
    s += `<path d="${star(x, y, r)}" fill="#ffd34d" fill-opacity="${op.toFixed(3)}"/>
      <path d="${star(x + 34, y + 26, r * 0.55)}" fill="#ffd34d" fill-opacity="${(op * 0.8).toFixed(3)}"/>`;
  }
  return s ? svgLayer(s) : null;
}

fs.mkdirSync(OUT, { recursive: true });
for (const [state, sc] of Object.entries(SCENES)) {
  const base = await sharp(path.join(ROOM, `room-${state}.jpg`)).removeAlpha().toBuffer();
  const cells = [];
  for (let i = 0; i < N; i++) {
    const t = i / N;
    const s = 1 + sc.breath * ease(t);
    const dx = sc.sway * Math.sin(TAU * t);
    const comps = [await bodyLayer(base, sc.body, s, dx)];
    const ov = overlays(sc, i);
    if (ov) comps.push(ov);
    const full = await sharp(base).composite(comps).png().toBuffer();
    const frame = await sharp(full).resize(CW, CH).jpeg({ quality: 90 }).toBuffer();
    cells.push(frame);
  }
  const grid = path.join(OUT, `${state}-chara24.jpg`);
  await sharp({ create: { width: CW * 4, height: CH * 6, channels: 3, background: '#000' } })
    .composite(cells.map((b, i) => ({ input: b, left: (i % 4) * CW, top: Math.floor(i / 4) * CH })))
    .jpeg({ quality: 84, mozjpeg: true }).toFile(grid);
  console.log(state, grid, Math.round(fs.statSync(grid).size / 1024) + 'KB');
  if (PREVIEW) {
    // 確認用：0,6,12,18 コマ目を2x2で並べた画像
    await sharp({ create: { width: CW * 2, height: CH * 2, channels: 3, background: '#000' } })
      .composite([0, 6, 12, 18].map((k, j) => ({ input: cells[k], left: (j % 2) * CW, top: Math.floor(j / 2) * CH })))
      .toFile(path.join(PREVIEW, `prev-${state}.jpg`));
  }
}
