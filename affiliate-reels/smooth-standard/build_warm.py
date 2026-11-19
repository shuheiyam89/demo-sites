#!/usr/bin/env python3
"""affiliate-warm 滑らか版の組み立て。
構成: カバー0.5 + before 5.5 + after 6.5 + 商品カード4.0(Claude版から流用) + エンド3.0(同) = 19.5秒
音楽: Relaxing Piano Music (Kevin MacLeod, CC BY 4.0)
"""
import subprocess, sys
from PIL import Image, ImageDraw, ImageFont

BASE = '/home/hatch/workspace/affiliate-reels'
SMOOTH = f'{BASE}/smooth'
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
W, H = 1080, 1920

BEFORE_CLIP = f'{SMOOTH}/media-generation-warm-before-clip-0-5279d671-9bb9-46b7-9879-0c1aeef750aa.mp4'
AFTER_CLIP = f'{SMOOTH}/media-generation-warm-after-clip-0-d7a7dd89-2279-4e2c-8fa8-f4b4917ae36f.mp4'
CLAUDE_MP4 = f'{BASE}/built/affiliate-warm.mp4'
MUSIC = f'{BASE}/music/relaxing-piano.mp3'

def font(size):
    return ImageFont.truetype(FONT, size)

def make_pr():
    img = Image.new('RGBA', (118, 68), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([2, 2, 116, 66], radius=14, fill=(255, 255, 255, 235))
    f = font(38)
    d.text((59, 34), 'PR', font=f, fill=(30, 30, 30, 255), anchor='mm')
    img.save(f'{SMOOTH}/pr.png')

def make_telop(text, name):
    f = font(54)
    tmp = Image.new('RGBA', (10, 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    bbox = d.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 44, 26
    img = Image.new('RGBA', (tw + pad_x * 2, th + pad_y * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=(th + pad_y * 2) // 2, fill=(255, 255, 255, 242))
    d.text((pad_x - bbox[0], pad_y - bbox[1]), text, font=f, fill=(25, 25, 25, 255))
    img.save(f'{SMOOTH}/{name}')

def make_cover():
    src = Image.open(f'{SMOOTH}/warm-before.jpg').convert('RGB')
    # fill 1080x1920 (cover-crop)
    scale = max(W / src.width, H / src.height)
    src = src.resize((round(src.width * scale), round(src.height * scale)))
    x = (src.width - W) // 2
    y = (src.height - H) // 2
    img = src.crop((x, y, x + W, y + H)).convert('RGBA')
    d = ImageDraw.Draw(img)
    f = font(96)
    lines = ['寒い夜のエアコン代、', 'もったいない']
    ty = 620
    for line in lines:
        d.text((W // 2, ty), line, font=f, fill=(255, 255, 255, 255),
               stroke_width=7, stroke_fill=(0, 0, 0, 255), anchor='ma')
        ty += 128
    pr = Image.open(f'{SMOOTH}/pr.png')
    img.alpha_composite(pr, (W - pr.width - 36, 48))
    img.convert('RGB').save(f'{SMOOTH}/cover.png')

def run(cmd):
    print('+', ' '.join(cmd[:3]), '...')
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:])
        sys.exit(1)

NORM = 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p'

make_pr()
make_telop('エアコンを強めても、まだ寒い…', 'telop1.png')
make_telop('羽織るだけで、ぬくぬく', 'telop2.png')
make_telop('そのままソファでくつろげる', 'telop3.png')
make_cover()

# cover segment
run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-i', f'{SMOOTH}/cover.png',
     '-t', '0.5', '-vf', 'format=yuv420p', '-r', '30', '-c:v', 'libx264', '-profile:v', 'high',
     f'{SMOOTH}/seg_cover.mp4'])

# before segment (5.5s) + PR + telop1
run(['ffmpeg', '-y', '-v', 'error', '-i', BEFORE_CLIP, '-i', f'{SMOOTH}/pr.png', '-i', f'{SMOOTH}/telop1.png',
     '-filter_complex',
     f'[0:v]{NORM}[v];[v][1:v]overlay=W-w-36:48[a];[a][2:v]overlay=(W-w)/2:H-h-330:enable=\'between(t,0.3,5.5)\'[out]',
     '-map', '[out]', '-t', '5.5', '-c:v', 'libx264', '-profile:v', 'high', '-crf', '18',
     f'{SMOOTH}/seg_before.mp4'])

# after segment (6.5s) + PR + telop2 -> telop3
run(['ffmpeg', '-y', '-v', 'error', '-i', AFTER_CLIP, '-i', f'{SMOOTH}/pr.png', '-i', f'{SMOOTH}/telop2.png', '-i', f'{SMOOTH}/telop3.png',
     '-filter_complex',
     f'[0:v]{NORM}[v];[v][1:v]overlay=W-w-36:48[a];[a][2:v]overlay=(W-w)/2:H-h-330:enable=\'between(t,0.3,3.4)\'[b];[b][3:v]overlay=(W-w)/2:H-h-330:enable=\'between(t,3.4,6.5)\'[out]',
     '-map', '[out]', '-t', '6.5', '-c:v', 'libx264', '-profile:v', 'high', '-crf', '18',
     f'{SMOOTH}/seg_after.mp4'])

# card + end segments from Claude's build (video only)
run(['ffmpeg', '-y', '-v', 'error', '-ss', '12.5', '-i', CLAUDE_MP4, '-t', '4.0', '-an',
     '-c:v', 'libx264', '-profile:v', 'high', '-crf', '18', '-vf', 'format=yuv420p,fps=30',
     f'{SMOOTH}/seg_card.mp4'])
run(['ffmpeg', '-y', '-v', 'error', '-ss', '16.5', '-i', CLAUDE_MP4, '-t', '3.0', '-an',
     '-c:v', 'libx264', '-profile:v', 'high', '-crf', '18', '-vf', 'format=yuv420p,fps=30',
     f'{SMOOTH}/seg_end.mp4'])

# concat
with open(f'{SMOOTH}/concat.txt', 'w') as fh:
    for s in ['seg_cover', 'seg_before', 'seg_after', 'seg_card', 'seg_end']:
        fh.write(f"file '{SMOOTH}/{s}.mp4'\n")
run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{SMOOTH}/concat.txt',
     '-c', 'copy', f'{SMOOTH}/video_only.mp4'])

# music mux
run(['ffmpeg', '-y', '-v', 'error', '-i', f'{SMOOTH}/video_only.mp4', '-i', MUSIC,
     '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
     '-af', 'afade=t=in:st=0:d=0.4,afade=t=out:st=18.0:d=1.5',
     '-c:a', 'aac', '-b:a', '160k', '-t', '19.5',
     f'{BASE}/built/affiliate-warm-smooth.mp4'])

print('DONE')
