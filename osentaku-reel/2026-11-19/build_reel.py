#!/usr/bin/env python3
import subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W,H,FPS=720,1280,30
D='/home/hatch/workspace/instagram/osentaku-reel-1119'
SANS='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
SERIF='/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'
TEAL=(43,111,196); INK=(32,48,58)
def font(p,size): return ImageFont.truetype(p,size)
def ease(t): return t*t*(3-2*t)

# lockup (icon + name) for watermark and endcard
icon=Image.open(D+'/icon-192.png').convert('RGBA')
lk=Image.new('RGBA',(790,192),(0,0,0,0))
lk.paste(icon,(0,0),icon)
d=ImageDraw.Draw(lk); f=font(SANS,104)
d.text((210,96),'おせんたく',font=f,fill=(35,70,120,255),anchor='lm')
lk.save(D+'/lockup.png')
wm=lk.resize((190,int(190*lk.height/lk.width)),Image.LANCZOS)
wm.putalpha(wm.getchannel('A').point(lambda v:int(v*0.65)))
def watermark(img):
    img=img.convert('RGB'); img.paste(wm,(16,16),wm); return img

def cover_img(still, W_, H_):
    return still.resize((W_,H_),Image.LANCZOS)
before_still=Image.open(D+'/before.png').convert('RGB').resize((W,H),Image.LANCZOS)
after_still=Image.open(D+'/after.png').convert('RGB').resize((W,H),Image.LANCZOS)
stain=Image.open(D+'/stain.png').convert('RGB')

def telop(img, lines, y=130, size=37, bottom=False):
    d=ImageDraw.Draw(img,'RGBA'); f=font(SANS,size)
    for i,line in enumerate(lines):
        tw=d.textlength(line,font=f); x=(W-tw)/2; yy=y+i*(size+16)
        d.rectangle([x-18,yy-10,x+tw+18,yy+size+12],fill=(0,0,0,110))
        d.text((x,yy),line,font=f,fill=(255,255,255,255))
    return img

def big_word(img, word, color):
    d=ImageDraw.Draw(img,'RGBA'); f=font(SERIF,110)
    tw=d.textlength(word,font=f); x=(W-tw)/2; y=520
    d.text((x+4,y+4),word,font=f,fill=(255,255,255,160))
    d.text((x,y),word,font=f,fill=color+(255,))
    return img

def clip_frames(path,dur):
    cmd=['ffmpeg','-v','error','-i',path,'-t',str(dur),'-vf',f'scale={W}:{H},fps={FPS}','-f','rawvideo','-pix_fmt','rgb24','-']
    p=subprocess.Popen(cmd,stdout=subprocess.PIPE); frames=[]; need=W*H*3
    while True:
        buf=p.stdout.read(need)
        if len(buf)<need: break
        frames.append(Image.frombytes('RGB',(W,H),buf))
    p.wait(); return frames

print('decoding',flush=True)
bf=clip_frames(D+'/media-generation-osentaku-1119-beforeclip-0-bb61f693-ef0e-4044-b965-84665e0ba19d.mp4',5.2)
af=clip_frames(D+'/media-generation-osentaku-1119-afterclip-0-61718ea8-71c0-4940-ae0a-2e54a706481a.mp4',6.0)
print(len(bf),len(af),flush=True)
def get(fr,i): return fr[min(i,len(fr)-1)].copy()

# phone cut base
def make_phone():
    bg=stain.resize((W,H),Image.LANCZOS).filter(ImageFilter.GaussianBlur(18))
    bg=ImageEnhance.Brightness(bg).enhance(0.85)
    img=bg.copy(); d=ImageDraw.Draw(img,'RGBA')
    x0,y0,x1,y1=105,120,615,1160
    d.rounded_rectangle([x0-10,y0-10,x1+10,y1+10],radius=58,fill=(20,20,20,255))
    d.rounded_rectangle([x0,y0,x1,y1],radius=50,fill=(255,255,255,255))
    # white band with icon + name
    ic=icon.resize((84,84),Image.LANCZOS)
    img.paste(ic,(x0+28,y0+24),ic)
    d.text((x0+128,y0+66),'おせんたく',font=font(SANS,52),fill=(35,70,120,255),anchor='lm')
    # stain photo area
    ph=stain.resize((x1-x0-36,660),Image.LANCZOS)
    img.paste(ph,(x0+18,y0+140))
    # shutter button
    cx,cy=(x0+x1)//2,y1-95
    d.ellipse([cx-52,cy-52,cx+52,cy+52],outline=(120,120,120,255),width=6)
    d.ellipse([cx-38,cy-38,cx+38,cy+38],fill=(230,230,230,255))
    return img
phone_img=make_phone(); phone_img.save(D+'/phone.png')

# result cards
def make_card(chip,text):
    cw_,ch_=540,128
    card=Image.new('RGBA',(cw_+16,ch_+16),(0,0,0,0)); d=ImageDraw.Draw(card)
    d.rounded_rectangle([8,8,cw_+8,ch_+8],radius=26,fill=(0,0,0,70))
    d.rounded_rectangle([0,0,cw_,ch_],radius=26,fill=(255,255,255,255))
    fchip=font(SANS,27); tw=d.textlength(chip,font=fchip)
    d.rounded_rectangle([26,24,26+tw+28,24+44],radius=22,fill=TEAL+(255,))
    d.text((26+14,46),chip,font=fchip,fill=(255,255,255),anchor='lm')
    size=29; ftext=font(SANS,size)
    while d.textlength(text,font=ftext)>cw_-52 and size>19:
        size-=2; ftext=font(SANS,size)
    d.text((26,96),text,font=ftext,fill=INK+(255,),anchor='lm')
    return card
cards=[(make_card('見立て','汗・皮脂の黄ばみ・ワイシャツ'),(40,250)),
       (make_card('手順','ぬるま湯に浸す→叩く→通常洗濯'),(140,530)),
       (make_card('使うもの','酸素系漂白剤と洗濯洗剤'),(40,810))]
backdrop=stain.resize((W,H),Image.LANCZOS)
backdrop=ImageEnhance.Brightness(backdrop).enhance(0.78).filter(ImageFilter.GaussianBlur(1.2)).convert('RGBA')
def result_frame(i):
    fr=backdrop.copy(); starts=[9,36,63]
    for (card,(x,y)),st in zip(cards,starts):
        if i<st: continue
        p=min((i-st)/12.0,1.0)
        if p<1.0:
            c=card.copy(); c.putalpha(c.getchannel('A').point(lambda v:int(v*p)))
            fr.paste(c,(x,y+int((1-p)*16)),c)
        else: fr.paste(card,(x,y),card)
    d=ImageDraw.Draw(fr); note='※色物・柄物には使わない／目立たない所で試す'; f=font(SANS,22); tw=d.textlength(note,font=f); d.rectangle([(W-tw)/2-10,1180,(W+tw)/2+10,1222],fill=(0,0,0,120)); d.text(((W-tw)/2,1188),note,font=f,fill=(255,255,255,255))
    return watermark(fr.convert('RGB'))

segs=[]
# cover 0.5s
for i in range(15):
    img=Image.new('RGB',(W,H))
    img.paste(before_still.crop((0,0,W//2,H)),(0,0)); img.paste(after_still.crop((W//2,0,W,H)),(W//2,0))
    d=ImageDraw.Draw(img,'RGBA'); d.rectangle([W//2-2,0,W//2+2,H],fill=(255,255,255,255))
    f=font(SANS,50); txt='黄ばみ→真っ白'; tw=d.textlength(txt,font=f); x=(W-tw)/2
    d.rectangle([x-14,110,x+tw+14,110+76],fill=(0,0,0,135)); d.text((x,122),txt,font=f,fill=(255,255,255,255))
    segs.append(watermark(img))
# before 5s
for i in range(int(5*FPS)):
    t=i/FPS; img=get(bf,i)
    if t<1.25: img=big_word(img,'Before',(20,20,20))
    if t<4.2: img=telop(img,['襟の黄ばみ…','洗っても残る…'],y=130,size=36)
    segs.append(watermark(img))
# phone 3s
n=int(3*FPS)
for i in range(n):
    z=1.0+0.05*(i/(n-1)); iw,ih=phone_img.size; cw,ch=iw/z,ih/z
    fr=phone_img.crop(((iw-cw)/2,(ih-ch)/2,(iw+cw)/2,(ih+ch)/2)).resize((W,H),Image.LANCZOS)
    fr=telop(fr,['スマホで撮るだけ'],y=1090,size=38)
    segs.append(watermark(fr))
# white fade 0.6s
last=segs[-1]; white=Image.new('RGB',(W,H),(255,255,255))
for i in range(int(0.6*FPS)):
    segs.append(Image.blend(last,white,[0.3,0.55,0.8,0.95][i]) if i<4 else white)
# result 3.6s
for i in range(int(3.6*FPS)): segs.append(result_frame(i))
# after 5.7s
for i in range(int(5.7*FPS)):
    t=i/FPS; img=get(af,i)
    if t<1.35: img=big_word(img,'After',(200,40,40))
    if t>=2.2: img=telop(img,['浸け置きで、ここまで白く'],y=1090,size=36)
    segs.append(watermark(img))
# endcard 1.5s
big=lk.resize((520,int(520*lk.height/lk.width)),Image.LANCZOS)
for i in range(int(1.5*FPS)):
    t=i/FPS; a=ease(min(max((t-0.1)/0.45,0),1))
    img=Image.new('RGB',(W,H),(255,255,255)); layer=Image.new('RGBA',(W,H),(0,0,0,0))
    layer.paste(big,((W-520)//2,470),big); d=ImageDraw.Draw(layer)
    f=font(SANS,32); txt='osentaku.onrender.com'; tw=d.textlength(txt,font=f)
    d.text(((W-tw)/2,470+big.height+46),txt,font=f,fill=(90,90,90,255))
    layer.putalpha(layer.getchannel('A').point(lambda v:int(v*a)))
    segs.append(Image.alpha_composite(img.convert('RGBA'),layer).convert('RGB'))

print('total',len(segs),len(segs)/FPS,flush=True)
enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-preset','medium',D+'/silent.mp4'],stdin=subprocess.PIPE)
for fr in segs: enc.stdin.write(fr.convert('RGB').tobytes())
enc.stdin.close(); enc.wait(); print('silent done',flush=True)
# cover jpg = first frame
segs[0].save(D+'/cover.jpg',quality=92)
