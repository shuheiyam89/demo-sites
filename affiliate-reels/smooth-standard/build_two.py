#!/usr/bin/env python3
"""affiliate christmas/storage 滑らか版の組み立て（build_warm.py の一般化）。
構成: カバー0.5 + before 5.5 + after 6.5 + 商品カード4.0 + エンド3.0 = 19.5秒
"""
import subprocess, sys
from PIL import Image, ImageDraw, ImageFont

BASE = '/home/hatch/workspace/affiliate-reels'
SMOOTH = f'{BASE}/smooth'
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
W, H = 1080, 1920
NORM = 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p'

def font(size):
    return ImageFont.truetype(FONT, size)

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

def make_cover(before_img, lines, name):
    src = Image.open(f'{SMOOTH}/{before_img}').convert('RGB')
    scale = max(W / src.width, H / src.height)
    src = src.resize((round(src.width * scale), round(src.height * scale)))
    x = (src.width - W) // 2
    y = (src.height - H) // 2
    img = src.crop((x, y, x + W, y + H)).convert('RGBA')
    d = ImageDraw.Draw(img)
    f = font(96)
    ty = 620
    for line in lines:
        d.text((W // 2, ty), line, font=f, fill=(255, 255, 255, 255),
               stroke_width=7, stroke_fill=(0, 0, 0, 255), anchor='ma')
        ty += 128
    pr = Image.open(f'{SMOOTH}/pr.png')
    img.alpha_composite(pr, (W - pr.width - 36, 48))
    img.convert('RGB').save(f'{SMOOTH}/{name}')

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2500:])
        sys.exit(1)

def build(tag, before_clip, after_clip, claude_mp4, music, telops, hook_lines, cover_name, out_name):
    t1, t2, t3 = telops
    make_telop(t1, f'{tag}-telop1.png')
    make_telop(t2, f'{tag}-telop2.png')
    make_telop(t3, f'{tag}-telop3.png')
    make_cover(f'{tag}-before.jpg', hook_lines, cover_name)
    run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-i', f'{SMOOTH}/{cover_name}',
         '-t', '0.5', '-vf', 'format=yuv420p', '-r', '30', '-c:v', 'libx264', '-profile:v', 'high',
         f'{SMOOTH}/{tag}-seg_cover.mp4'])
    run(['ffmpeg', '-y', '-v', 'error', '-i', before_clip, '-i', f'{SMOOTH}/pr.png', '-i', f'{SMOOTH}/{tag}-telop1.png',
         '-filter_complex',
         f'[0:v]{NORM}[v];[v][1:v]overlay=W-w-36:48[a];[a][2:v]overlay=(W-w)/2:H-h-330:enable=\'between(t,0.3,5.5)\'[out]',
         '-map', '[out]', '-t', '5.5', '-c:v', 'libx264', '-profile:v', 'high', '-crf', '18',
         f'{SMOOTH}/{tag}-seg_before.mp4'])
    run(['ffmpeg', '-y', '-v', 'error', '-i', after_clip, '-i', f'{SMOOTH}/pr.png', '-i', f'{SMOOTH}/{tag}-telop2.png', '-i', f'{SMOOTH}/{tag}-telop3.png',
         '-filter_complex',
         f'[0:v]{NORM}[v];[v][1:v]overlay=W-w-36:48[a];[a][2:v]overlay=(W-w)/2:H-h-330:enable=\'between(t,0.3,3.4)\'[b];[b][3:v]overlay=(W-w)/2:H-h-330:enable=\'between(t,3.4,6.5)\'[out]',
         '-map', '[out]', '-t', '6.5', '-c:v', 'libx264', '-profile:v', 'high', '-crf', '18',
         f'{SMOOTH}/{tag}-seg_after.mp4'])
    run(['ffmpeg', '-y', '-v', 'error', '-ss', '12.5', '-i', claude_mp4, '-t', '4.0', '-an',
         '-c:v', 'libx264', '-profile:v', 'high', '-crf', '18', '-vf', 'format=yuv420p,fps=30',
         f'{SMOOTH}/{tag}-seg_card.mp4'])
    run(['ffmpeg', '-y', '-v', 'error', '-ss', '16.5', '-i', claude_mp4, '-t', '3.0', '-an',
         '-c:v', 'libx264', '-profile:v', 'high', '-crf', '18', '-vf', 'format=yuv420p,fps=30',
         f'{SMOOTH}/{tag}-seg_end.mp4'])
    with open(f'{SMOOTH}/{tag}-concat.txt', 'w') as fh:
        for s in ['seg_cover', 'seg_before', 'seg_after', 'seg_card', 'seg_end']:
            fh.write(f"file '{SMOOTH}/{tag}-{s}.mp4'\n")
    run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{SMOOTH}/{tag}-concat.txt',
         '-c', 'copy', f'{SMOOTH}/{tag}-video_only.mp4'])
    run(['ffmpeg', '-y', '-v', 'error', '-i', f'{SMOOTH}/{tag}-video_only.mp4', '-i', music,
         '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
         '-af', 'afade=t=in:st=0:d=0.4,afade=t=out:st=18.0:d=1.5',
         '-c:a', 'aac', '-b:a', '160k', '-t', '19.5',
         f'{BASE}/built/{out_name}'])
    print('BUILT', out_name)

build('christmas',
      f'{SMOOTH}/media-generation-christmas-before-clip-0-a534c76a-4d9d-4881-b171-fae58f4718df.mp4',
      f'{SMOOTH}/media-generation-christmas-after-clip-0-ef5d77ab-3412-4163-9b47-0e5271c3ad0b.mp4',
      f'{BASE}/built/affiliate-christmas.mp4',
      f'{BASE}/music/wish-background.mp3',
      ['ツリーはあるのに、なんだか地味…', '巻いて点けるだけで、この雰囲気', 'タイマー付きで、消し忘れにくい'],
      ['ツリーに巻くだけで', '一気にクリスマス'],
      'cover-christmas.png', 'affiliate-christmas-smooth.mp4')

build('storage',
      f'{SMOOTH}/media-generation-storage-before-clip-0-ff529be0-3938-49da-a5bd-2842bf62608e.mp4',
      f'{SMOOTH}/media-generation-storage-after-clip-0-439a80ad-65fa-4fa2-8f72-3442ac15386e.mp4',
      f'{BASE}/built/affiliate-storage.mp4',
      f'{BASE}/music/life-of-riley.mp3',
      ['衣類の山、どこにしまう…？', '5面が開くから、出し入れしやすい', 'キャスター付きで、そのまま移動'],
      ['衣類の山、', '5面開くボックスで解決'],
      'cover-storage.png', 'affiliate-storage-smooth.mp4')

print('ALL DONE')
