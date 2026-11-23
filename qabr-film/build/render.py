import sys, os, subprocess, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import shapes
from shapes import *

HERE = os.path.dirname(os.path.abspath(__file__))
shapes.FONTDIR = os.environ.get('FONTDIR', os.path.join(HERE, 'fonts'))
import importlib
SC = importlib.import_module(os.environ.get('SCENES', 'scenes'))

FPS = 30
DUR = 241.0

SUBS = json.load(open(os.path.join(HERE, 'subs.json')))   # [[start,end,text,hl], ...]

ROMAN = json.load(open(os.path.join(HERE, 'roman.json')))   # [start,end,[words],[word starts],hl]
_rcache = {}
_rfont = None


def plate_img(ci, k):
    key = ('p', ci, k)
    if key in _rcache:
        return _rcache[key]
    f = ImageFont.truetype(os.path.join(shapes.FONTDIR, 'Inter-ExtraBold.otf'), 66)
    words = ROMAN[ci][2]
    sp = f.getlength(' ') + 6
    ws = [f.getlength(w) for w in words]
    tot = sum(ws) + sp * (len(words) - 1)
    pw, ph = int(tot) + 100, 134
    im = Image.new('RGBA', (pw, ph + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, pw, ph], 28, fill=(20, 15, 38, 215))
    x = 50
    cur = k - 1
    for i, w in enumerate(words):
        if i == cur:
            d.rounded_rectangle([x - 14, 24, x + ws[i] + 14, ph - 24], 18, fill=(255, 236, 190, 255))
            d.text((x, 32), w, font=f, fill=(40, 24, 24, 255))
        else:
            d.text((x, 32), w, font=f, fill=(255, 255, 255, 255 if i < cur else 150))
        x += ws[i] + sp
    _rcache[key] = im
    return im


def roman_img(ci, k):
    global _rfont
    key = (ci, k)
    if key in _rcache:
        return _rcache[key]
    if _rfont is None:
        _rfont = ImageFont.truetype(os.path.join(shapes.FONTDIR, 'Inter-ExtraBold.otf'), 84)
    words = ROMAN[ci][2]
    hl = ROMAN[ci][4]
    sp = _rfont.getlength(' ')
    ws = [_rfont.getlength(w) for w in words]
    tot = sum(ws) + sp * (len(words) - 1)
    im = Image.new('RGBA', (int(tot) + 60, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 30
    for i, w in enumerate(words):
        if i < k:
            col = (255, 214, 126, 255) if hl else (255, 255, 255, 255)
        else:
            col = (255, 255, 255, 120)
        d.text((x + 3, 40 + 4), w, font=_rfont, fill=(0, 0, 0, 150))
        d.text((x, 40), w, font=_rfont, fill=col, stroke_width=3, stroke_fill=(10, 10, 14, 230))
        x += ws[i] + sp
    _rcache[key] = im
    return im


_cache = {}


def get_scene(i):
    if i not in _cache:
        a, b, fn = SC.TIMELINE[i]
        s = fn()
        s.t0, s.t1 = a, b
        _cache[i] = s
        # keep memory bounded
        for k in list(_cache):
            if abs(k - i) > 1:
                del _cache[k]
    return _cache[i]


_ov = {}


def overlays():
    if not _ov:
        _ov['vig'] = vignette(0.85)
        yy = np.linspace(0, 1, 640)[:, None]
        arr = np.zeros((640, W, 4), np.uint8)
        arr[..., :3] = (3, 3, 6)
        arr[..., 3] = (np.clip(yy, 0, 1) ** 1.5 * 190).astype(np.uint8)
        _ov['band'] = Image.fromarray(arr, 'RGBA')
        _ov['grain'] = grain_tile()
        _ov['sub'] = {}
    return _ov


def sub_img(i):
    ov = overlays()
    if i not in ov['sub']:
        s, e, text, hl = SUBS[i]
        if hl:
            im = text_block(text, font('NotoNaskhArabic_700Bold.ttf', 50), (255, 214, 126, 255), 960, spacing=1.6, stroke=4, stroke_col=(20, 10, 0))
        else:
            im = text_block(text, font('NotoNaskhArabic_600SemiBold.ttf', 46), (236, 232, 220, 255), 960, spacing=1.6, stroke=4, stroke_col=(8, 8, 12))
        ov['sub'][i] = im
    return ov['sub'][i]


def frame_at(t):
    ov = overlays()
    # which scenes are active (crossfade at boundaries)
    idx = [i for i, (a, b, _) in enumerate(SC.TIMELINE) if a - SC.XFADE / 2 <= t < b + SC.XFADE / 2] or [len(SC.TIMELINE) - 1]
    if len(idx) == 1:
        f = get_scene(idx[0]).render(t)
    else:
        i0, i1 = idx[0], idx[1]
        bnd = SC.TIMELINE[i1][0]
        k = SC.ease((t - (bnd - SC.XFADE / 2)) / SC.XFADE)
        f0 = get_scene(i0).render(t)
        f1 = get_scene(i1).render(t)
        f = Image.blend(f0, f1, k)
    f = f.convert('RGBA')
    f.alpha_composite(ov['vig'])
    if not os.environ.get('CARD'):
        f.alpha_composite(ov['band'], (0, H - 640))
    # film grain
    gx, gy = int(t * 997) % 64, int(t * 613) % 64
    f.alpha_composite(ov['grain'].crop((gx, gy, gx + W, gy + H)))
    # start/end fades
    if t < 1.2:
        SC.fade_to(f, (0, 0, 0), 1 - SC.ease(t / 1.2))
    if t > DUR - 1.8:
        SC.fade_to(f, (0, 0, 0), SC.ease((t - (DUR - 1.8)) / 1.6))
    # subtitles
    for i, (s, e, text, hl) in enumerate([] if os.environ.get('NO_URDU') else SUBS):
        if s - 0.05 <= t <= e + 0.25:
            a = SC.ease((t - (s - 0.05)) / 0.25) * (1 - SC.ease((t - e) / 0.25))
            im = sub_img(i)
            if a > 0.01:
                im2 = im.copy()
                im2.putalpha(im.split()[3].point(lambda v: int(v * a)))
                y = 1600 - im.height // 2 + int(10 * (1 - a))
                f.alpha_composite(im2, (int((W - im.width) / 2), y))
            break
    # Roman-Urdu karaoke captions (bold, words light up as they are spoken)
    for ci, (cs, ce, words, wts, hl) in enumerate(ROMAN):
        if cs - 0.05 <= t <= ce + 0.18:
            a = SC.ease((t - (cs - 0.05)) / 0.14) * (1 - SC.ease((t - ce) / 0.18))
            k = sum(1 for x in wts if t >= x - 0.02)
            im = plate_img(ci, k) if os.environ.get('CARD') else roman_img(ci, k)
            if a > 0.01:
                im2 = im.copy()
                im2.putalpha(im.split()[3].point(lambda v: int(v * a)))
                f2 = Image.new('RGBA', f.size, (0, 0, 0, 0))
                f2.alpha_composite(im2, (int((W - im2.width) / 2), (1690 if os.environ.get('CARD') else (1400 if os.environ.get('NO_URDU') else 1330)) - im2.height // 2 + int(8 * (1 - a))))
                f = Image.alpha_composite(f.convert('RGBA'), f2)
            break
    return f.convert('RGB')


def render_range(a, b, out):
    cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p', '-g', '30', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(a, b):
        p.stdin.write(frame_at(n / FPS).tobytes())
    p.stdin.close()
    p.wait()


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        for t in sys.argv[3:]:
            frame_at(float(t)).resize((540, 960)).save(f'{sys.argv[2]}_{float(t):06.1f}.png')
    elif sys.argv[1] == 'range':
        render_range(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
