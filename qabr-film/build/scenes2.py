"""Photo-based scenes: user-supplied still images brought to life with camera motion, dust, light and soil FX."""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scenes import ease, lerp, clamp, seg, motes, draw_motes, put_glow, put_fog, fade_to, XFADE, glow_sprite as _gs  # noqa
from shapes import W, H, glow_sprite, beam_sprite, fog_layer, text_block, font, rgb
import shapes

_INTER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'Inter-ExtraBold.otf')


def font(name, size):                       # Roman-Urdu titles use the same bold sans as the captions
    from PIL import ImageFont
    return ImageFont.truetype(_INTER, int(size * 0.86))


def text_block(text, fnt, color, maxw, spacing=1.3, stroke=0, stroke_col=(0, 0, 0)):
    words = text.split()
    lines, cur = [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if fnt.getlength(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w_
    if cur:
        lines.append(cur)
    lh = int(fnt.size * spacing)
    img = Image.new('RGBA', (maxw + 40, lh * len(lines) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        x = (img.width - fnt.getlength(ln)) / 2
        d.text((x + 3, 24 + i * lh), ln, font=fnt, fill=(0, 0, 0, 140))
        d.text((x, 20 + i * lh), ln, font=fnt, fill=color, stroke_width=max(2, stroke), stroke_fill=stroke_col if stroke else (10, 10, 14))
    return img

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
BW, BH = 1350, 2400
NASKH = 'NotoNaskhArabic_700Bold.ttf'
CARD = bool(os.environ.get('CARD'))


def _grade(im, bright=1.0, contrast=1.0, sat=1.0, tint=(1, 1, 1)):
    a = np.asarray(im, np.float32) / 255.0
    a = (a - 0.5) * contrast + 0.5
    a *= bright
    g = a.mean(axis=2, keepdims=True)
    a = g + (a - g) * sat
    a *= np.array(tint, np.float32)[None, None, :]
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), 'RGB')


def prep(name, crop=None, fit=False, focus=(0.5, 0.5), patch=None, grade=None):
    im = Image.open(os.path.join(ASSETS, name)).convert('RGB')
    if patch:                                   # paint out a watermark with a blurred neighbouring patch
        x0, y0, x1, y1, dx = patch
        src = im.crop((x0 + dx, y0, x1 + dx, y1)).filter(ImageFilter.GaussianBlur(3))
        mask = Image.new('L', src.size, 255).filter(ImageFilter.GaussianBlur(4))
        im.paste(src, (x0, y0), mask)
    if crop:
        im = im.crop(crop)
    if fit:
        sc = max(BW / im.width, BH / im.height)
        bg = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
        ox, oy = (bg.width - BW) // 2, (bg.height - BH) // 2
        bg = bg.crop((ox, oy, ox + BW, oy + BH)).filter(ImageFilter.GaussianBlur(48))
        bg = Image.eval(bg, lambda v: int(v * 0.42))
        fw = BW
        fh = int(im.height * fw / im.width)
        fg = im.resize((fw, fh), Image.LANCZOS)
        mask = Image.new('L', (fw, fh), 255)
        md = ImageDraw.Draw(mask)
        for i in range(70):                      # feather top & bottom edges
            v = int(255 * i / 70)
            md.line([(0, i), (fw, i)], fill=v)
            md.line([(0, fh - 1 - i), (fw, fh - 1 - i)], fill=v)
        bg.paste(fg, (0, (BH - fh) // 2), mask)
        base = bg
    else:
        sc = max(BW / im.width, BH / im.height)
        big = im.resize((int(im.width * sc) + 1, int(im.height * sc) + 1), Image.LANCZOS)
        ox = int((big.width - BW) * focus[0])
        oy = int((big.height - BH) * focus[1])
        base = big.crop((ox, oy, ox + BW, oy + BH))
    base = base.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    if grade:
        base = _grade(base, **grade)
    return base


class Photo:
    """cam(u) -> (zoom, px, py) with px,py in [-1,1] (pan inside the slack)."""

    def __init__(self, base, cam, dyn=None, shake=0.0):
        self.base, self.cam, self.dyn, self.shake = base, cam, dyn, shake
        self.t0 = self.t1 = 0

    def window(self, t):
        u = seg(t, self.t0, self.t1)
        z, px, py = self.cam(u)
        ww, wh = BW / z, BH / z
        cx = BW / 2 + px * (BW - ww) / 2
        cy = BH / 2 + py * (BH - wh) / 2
        if self.shake:
            cx += self.shake * (math.sin(t * 23.1) + 0.6 * math.sin(t * 41.7)) * 2.0
            cy += self.shake * (math.sin(t * 19.3 + 1) + 0.6 * math.sin(t * 37.3)) * 2.0
        x0 = clamp(cx - ww / 2, 0, BW - ww)
        y0 = clamp(cy - wh / 2, 0, BH - wh)
        return x0, y0, ww, wh

    def render(self, t):
        x0, y0, ww, wh = self.window(t)
        f = self.base.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + ww, y0 + wh)).convert('RGBA')
        if self.dyn:
            sx, sy = W / ww, H / wh

            def ws(fx, fy):                      # base fraction -> screen px
                return (fx * BW - x0) * sx, (fy * BH - y0) * sy
            self.dyn(f, t - self.t0, seg(t, self.t0, self.t1), ws, sx)
        return f


def _title(im_text, y, a0, a1, a2, a3):
    def draw(f, t):
        if CARD:
            return
        a = ease(seg(t, a0, a1)) * (1 - ease(seg(t, a2, a3)))
        if a > 0.01:
            s = im_text.copy()
            s.putalpha(im_text.split()[3].point(lambda v: int(v * a)))
            f.alpha_composite(s, (int((W - s.width) / 2), int(y - 14 * (1 - a))))
    return draw


def _warm_motes(seed, n=70, col=(255, 235, 200), amax=150, drift=(0.4, -1.0), size=(2, 6), speed=(8, 26)):
    ms = motes(n, seed, col=col, amax=amax, size=size, speed=speed)
    return lambda f, t, fade=1.0: draw_motes(f, ms, t, drift=drift, fade=fade)


# ------------------------------------------------------------------ builders (one per timeline slot)
def s_cem():
    base = prep('img01.jpg', patch=(80, 104, 134, 138, 70), grade=dict(bright=0.92, contrast=1.1, sat=1.0))
    m = _warm_motes(11)
    t1 = text_block('Ae ghafil insaan!', font(NASKH, 104), (244, 236, 214, 255), 900, stroke=3)
    t2 = text_block('Zara apni qabr ka tasawwur kar', font(NASKH, 76), (255, 214, 140, 255), 900, stroke=3)
    d1, d2 = _title(t1, 300, 1.8, 3.2, 7.2, 9.0), _title(t2, 450, 2.4, 3.8, 7.2, 9.0)

    def dyn(f, t, u, ws, sx):
        m(f, t); d1(f, t); d2(f, t)
    return Photo(base, lambda u: (lerp(1.0, 1.22, ease(u)), lerp(0.1, -0.1, u), lerp(0.7, -0.2, ease(u))), dyn)


def s_shroud():
    base = prep('img02.jpg', crop=(105, 40, 450, 640), grade=dict(bright=0.9, contrast=1.15, sat=0.8, tint=(0.95, 1.0, 1.08)))
    m = _warm_motes(21, 90, col=(220, 230, 255), amax=170)

    def dyn(f, t, u, ws, sx):
        m(f, t)
    return Photo(base, lambda u: (lerp(1.0, 1.3, ease(u)), 0, lerp(0.8, -0.5, ease(u))), dyn)


def s_weep():
    base = prep('img03.jpg', grade=dict(bright=0.92, contrast=1.1, sat=0.9))
    m = _warm_motes(31, 70, col=(255, 225, 190), amax=120)

    def dyn(f, t, u, ws, sx):
        m(f, t)
    return Photo(base, lambda u: (lerp(1.0, 1.35, ease(u)), lerp(-0.2, -0.7, ease(u)), lerp(-0.2, -0.8, ease(u))), dyn)


def s_kafan():
    base = prep('img04.jpg', fit=True, grade=dict(bright=0.95, contrast=1.1, sat=0.9))
    m = _warm_motes(41, 60, col=(255, 220, 190), amax=130)
    ms = motes(40, 42, col=(200, 225, 245), amax=200, size=(2, 5), speed=(70, 120))

    def dyn(f, t, u, ws, sx):
        m(f, t)
        if t < 2.7:                              # water droplets (ghusl)
            d = ImageDraw.Draw(f)
            for i in range(10):
                tt = (t - i * 0.27) % 0.9
                x = 440 + (i * 83) % 200
                if tt < 0.4 and t > 0:
                    y = 200 + tt * tt * 3800
                    d.ellipse([x - 5, y - 9, x + 5, y + 9], fill=(205, 232, 250, 220))
    return Photo(base, lambda u: (lerp(1.0, 1.4, ease(u)), 0, lerp(0.1, 0.0, u)), dyn)


def s_carry():
    base = prep('img05.jpg', fit=True, grade=dict(bright=0.92, contrast=1.12, sat=0.95))
    sand = motes(80, 52, col=(236, 205, 160), amax=170, size=(2, 5), speed=(60, 160))

    def dyn(f, t, u, ws, sx):
        draw_motes(f, sand, t, drift=(2.0, -0.05))
    return Photo(base, lambda u: (1.25, lerp(0.85, -0.85, ease(u)), 0.0), dyn)


def s_salah():
    base = prep('img06.jpg', grade=dict(bright=0.85, contrast=1.1, sat=0.85, tint=(0.97, 0.98, 1.05)))
    m = _warm_motes(61, 50, col=(255, 250, 235), amax=110)

    def dyn(f, t, u, ws, sx):
        m(f, t)
    return Photo(base, lambda u: (lerp(1.0, 1.2, ease(u)), lerp(0.4, -0.3, u), lerp(-0.4, 0.2, u)), dyn)


def s_aerial():
    base = prep('img07.jpg', grade=dict(bright=0.88, contrast=1.1, sat=0.95))
    m = _warm_motes(71, 60, col=(230, 200, 160), amax=130, drift=(0.6, -0.2))

    def dyn(f, t, u, ws, sx):
        m(f, t)
    return Photo(base, lambda u: (lerp(1.0, 1.4, ease(u)), 0.0, lerp(-0.2, 0.0, ease(u))), dyn)


def s_shovel():
    base = prep('img09.jpg', grade=dict(bright=0.8, contrast=1.15, sat=0.9))
    rnd = random.Random(9)
    drops = [(rnd.uniform(0, W), rnd.uniform(0, 1), rnd.uniform(500, 1100), rnd.uniform(3, 9), rnd.uniform(0, 6.28)) for _ in range(160)]
    m = _warm_motes(81, 50, col=(210, 170, 130), amax=140, drift=(0.1, 1.0))

    def dyn(f, t, u, ws, sx):
        d = ImageDraw.Draw(f)
        for (x, ph, sp, r, w) in drops:           # soil falling in handfuls
            cyc = (t * 0.87 + ph) % 1.0
            if cyc < 0.7:
                y = -40 + (cyc / 0.7) ** 1.6 * (H + 80) * (0.8 + 0.2 * ph)
                xx = x + 18 * math.sin(t * 2 + w)
                d.ellipse([xx - r, y - r, xx + r, y + r], fill=(96, 64, 42, 235))
                d.ellipse([xx - r * 0.5, y - r * 0.5, xx + r * 0.2, y + r * 0.2], fill=(140, 98, 66, 220))
        m(f, t)
        fade_to(f, (3, 2, 2), ease(seg(t, 9.0, 10.9)) * 0.55)
    return Photo(base, lambda u: (lerp(1.05, 1.25, u), 0, lerp(-0.3, 0.3, u)), dyn)


def s_mound():
    base = prep('img08.jpg', grade=dict(bright=0.95, contrast=1.1, sat=0.95))
    m = _warm_motes(91, 80, col=(255, 240, 210), amax=190, drift=(0.5, 0.4))
    bm = beam_sprite(160, 520, 1300, '#ffeccc', 0.22)

    def dyn(f, t, u, ws, sx):
        x, y = ws(0.78, 0.04)
        a = 0.7 + 0.3 * math.sin(t * 0.9)
        b = bm.copy(); b.putalpha(bm.split()[3].point(lambda v: int(v * a)))
        bb = b.rotate(18, expand=True, resample=Image.BILINEAR)
        f.paste(bb, (int(x - bb.width / 2 + 30), int(y - 60)), bb)
        m(f, t)
    return Photo(base, lambda u: (lerp(1.0, 1.25, ease(u)), lerp(-0.2, 0.3, u), lerp(0.3, -0.4, u)), dyn)


def s_rays():
    base = prep('img10.jpg', grade=dict(bright=0.95, contrast=1.1, sat=0.9))
    m = _warm_motes(101, 90, col=(235, 245, 255), amax=170, drift=(0.1, 0.5))
    gl = glow_sprite(300, '#dfeaff', 0.6)

    def dyn(f, t, u, ws, sx):
        x, y = ws(0.5, 0.46)
        put_glow(f, gl, x, y, 0.55 + 0.25 * math.sin(t * 1.1), 1.6 + 0.3 * u)
        m(f, t)
        for k in range(3):                         # question ripples around the figure (tasks of the grave)
            tt = t - 4.5 - k * 0.9
            if 0 < tt < 2.6 and t < 12:
                px, py = ws(0.49, 0.865)
                r = tt * 150 * sx
                ImageDraw.Draw(f).ellipse([px - r, py - r * 0.35, px + r, py + r * 0.35], outline=(255, 240, 200, int(200 * (1 - tt / 2.6))), width=4)
    return Photo(base, lambda u: (lerp(1.0, 1.45, ease(u)), 0.0, lerp(-0.5, 0.75, ease(u))), dyn)


def s_book():
    base = prep('img11.jpg', grade=dict(bright=1.0, contrast=1.1, sat=1.0))
    m = _warm_motes(111, 110, col=(255, 210, 120), amax=230, drift=(0.2, -1.6), size=(2, 5), speed=(20, 60))
    gl = glow_sprite(520, '#ffd98a', 0.9)
    ti = text_block("A'maal", font(NASKH, 160), (255, 224, 150, 255), 800, stroke=4, stroke_col=(60, 36, 10))

    def dyn(f, t, u, ws, sx):
        x, y = ws(0.5, 0.72)
        put_glow(f, gl, x, y, ease(u) * (0.8 + 0.1 * math.sin(t * 4)), 1.2 + 0.6 * ease(u))
        m(f, t)
        a = 0.0 if CARD else ease(seg(t, 0.8, 1.9))
        s = ti.copy(); s.putalpha(ti.split()[3].point(lambda v: int(v * a)))
        f.alpha_composite(s, (int((W - s.width) / 2), 420))
    return Photo(base, lambda u: (lerp(1.0, 1.35, ease(u)), 0.0, lerp(0.2, 0.7, ease(u))), dyn)


def s_fire():
    base = prep('img12.jpg', grade=dict(bright=0.95, contrast=1.1, sat=1.0))
    emb = motes(110, 121, col=(255, 170, 60), amax=230, size=(2, 5), speed=(40, 120))

    def dyn(f, t, u, ws, sx):
        draw_motes(f, emb, t, drift=(0.3, -1.6))
        flick = 0.07 * math.sin(t * 6.7) * math.sin(t * 2.3)
        fade_to(f, (255, 120, 20), max(0.0, flick))
    return Photo(base, lambda u: (lerp(1.0, 1.28, ease(u)), 0.2, lerp(0.4, -0.3, u)), dyn, shake=3.5)


def s_silence():
    base = prep('img13.jpg', fit=True, grade=dict(bright=1.05, contrast=1.05, sat=1.0))
    ti = text_block('Kahan hai teri woh zubaan?', font(NASKH, 110), (244, 236, 214, 255), 940, stroke=4)
    shards = motes(40, 131, col=(210, 200, 170), amax=190, size=(3, 8), speed=(10, 25))
    d = _title(ti, 300, 0.1, 1.0, 3.6, 5.0)

    def dyn(f, t, u, ws, sx):
        draw_motes(f, shards, t, drift=(0.1, 1.0), fade=1 - ease(seg(t, 0.5, 5.0)))
        d(f, t)
    return Photo(base, lambda u: (lerp(1.0, 1.3, ease(u)), 0.0, 0.0), dyn)


def s_lamp():
    base = prep('img14.jpg', grade=dict(bright=1.0, contrast=1.1, sat=1.0))
    fog = fog_layer('#9aa3b8', 70, 3)
    m = _warm_motes(141, 70, col=(235, 240, 255), amax=150, drift=(0.1, 0.5))
    gl = glow_sprite(260, '#ffffff', 0.5)

    def dyn(f, t, u, ws, sx):
        x, y = ws(0.45, 0.31)
        put_glow(f, gl, x, y, 0.6 + 0.12 * math.sin(t * 7.1) * math.sin(t * 1.3), 1.4)
        put_fog(f, fog, t, 1100, 10, 0.55)
        m(f, t)
    return Photo(base, lambda u: (lerp(1.0, 1.32, ease(u)), lerp(0.1, -0.1, u), lerp(0.2, 0.5, ease(u))), dyn)


def s_eye():
    base = prep('img15.jpg', grade=dict(bright=0.95, contrast=1.1, sat=0.95, tint=(1.0, 0.98, 1.0)))

    def dyn(f, t, u, ws, sx):
        pass
    return Photo(base, lambda u: (lerp(1.0, 1.55, ease(u)), lerp(-0.1, -0.3, u), lerp(-0.2, -0.4, ease(u))), dyn)


def s_candle():
    base = prep('img16.jpg', grade=dict(bright=1.0, contrast=1.1, sat=1.0))
    gl = glow_sprite(420, '#ffb060', 0.9)
    m = _warm_motes(161, 60, col=(255, 200, 140), amax=170, drift=(0.1, -0.9))

    def dyn(f, t, u, ws, sx):
        x, y = ws(0.53, 0.55)
        fl = 0.75 + 0.15 * math.sin(t * 9) + 0.1 * math.sin(t * 13.3 + 1)
        put_glow(f, gl, x, y, fl, 1.2)
        m(f, t)
    return Photo(base, lambda u: (lerp(1.0, 1.3, ease(u)), lerp(0.0, 0.1, u), lerp(0.1, -0.2, u)), dyn)


def s_quran():
    base = prep('img17.jpg', grade=dict(bright=1.0, contrast=1.08, sat=1.0))
    m = _warm_motes(171, 100, col=(255, 230, 170), amax=210, drift=(0.2, -1.0))
    gl = glow_sprite(520, '#ffe2a0', 0.7)
    hd = text_block('"Musalman ko gaali dena fisq hai"', font(NASKH, 74), (255, 232, 170, 255), 900, spacing=1.8, stroke=4, stroke_col=(50, 30, 8))
    ct = text_block('(Sahih Bukhari o Sahih Muslim)', font(NASKH, 40), (240, 214, 160, 255), 900, spacing=1.7, stroke=3, stroke_col=(50, 30, 8))
    words = [(text_block(s, font(NASKH, 84), (255, 232, 170, 255), 900, stroke=4, stroke_col=(50, 30, 8)), ts, y)
             for s, ts, y in (('Zikr-e-Ilahi', 10.6, 330), ('Durood Shareef', 15.7, 460), ('Tilawat-e-Quran', 17.7, 590))]
    dh, dc = _title(hd, 330, 4.2, 5.2, 8.6, 9.4), _title(ct, 510, 7.6, 8.4, 10.0, 10.8)
    dw = [_title(im, y, ts, ts + 0.7, 22.6, 23.6) for im, ts, y in words]

    def dyn(f, t, u, ws, sx):
        x, y = ws(0.5, 0.2)
        put_glow(f, gl, x, y, 0.6 + 0.2 * math.sin(t * 1.2), 2.0)
        m(f, t)
        dh(f, t)
        for d in dw:
            d(f, t)
        fade_to(f, (10, 6, 2), ease(seg(t, 21.5, 23.8)) * 0.5)
    return Photo(base, lambda u: (lerp(1.0, 1.28, ease(u)), lerp(0.0, 0.1, u), lerp(0.4, -0.2, ease(u))), dyn)


def s_dua():
    base = prep('img18.jpg', grade=dict(bright=1.0, contrast=1.08, sat=1.0))
    gl = glow_sprite(360, '#ffc070', 0.9)
    m = _warm_motes(181, 80, col=(255, 225, 170), amax=190, drift=(0.2, -1.1))

    def dyn(f, t, u, ws, sx):
        x, y = ws(0.9, 0.54)
        put_glow(f, gl, x, y, 0.75 + 0.12 * math.sin(t * 8) * math.sin(t * 2.7), 1.3)
        m(f, t)
        fade_to(f, (255, 214, 150), ease(seg(t, 14, 21.4)) * 0.12)
    return Photo(base, lambda u: (lerp(1.0, 1.3, ease(u)), lerp(-0.2, 0.2, u), lerp(0.0, -0.1, u)), dyn)


def s_grave2():
    base = prep('img08.jpg', grade=dict(bright=0.8, contrast=1.15, sat=0.85, tint=(0.95, 0.97, 1.08)))
    m = _warm_motes(191, 70, col=(235, 235, 250), amax=160, drift=(0.5, 0.4))

    def dyn(f, t, u, ws, sx):
        m(f, t)
    return Photo(base, lambda u: (lerp(1.3, 1.0, ease(u)), lerp(0.3, -0.2, u), lerp(-0.4, 0.3, u)), dyn)


def s_book2():
    base = prep('img11.jpg', grade=dict(bright=1.0, contrast=1.12, sat=1.0))
    m = _warm_motes(201, 130, col=(255, 210, 120), amax=240, drift=(0.2, -1.8), size=(2, 5), speed=(20, 70))
    gl = glow_sprite(560, '#ffd98a', 0.95)
    ti = text_block("Sirf tere a'maal", font(NASKH, 112), (255, 226, 150, 255), 940, stroke=4, stroke_col=(60, 36, 10))

    def dyn(f, t, u, ws, sx):
        x, y = ws(0.5, 0.72)
        put_glow(f, gl, x, y, 0.9 + 0.1 * math.sin(t * 3), 1.6)
        m(f, t)
        a = 0.0 if CARD else ease(seg(t, 0.5, 1.6))
        s = ti.copy(); s.putalpha(ti.split()[3].point(lambda v: int(v * a)))
        f.alpha_composite(s, (int((W - s.width) / 2), 380))
    return Photo(base, lambda u: (lerp(1.1, 1.4, ease(u)), 0.0, lerp(0.4, 0.7, u)), dyn)


def s_moon():
    base = prep('img19.jpg', grade=dict(bright=1.0, contrast=1.08, sat=1.0))
    rnd = random.Random(19)
    tw = [(rnd.random(), rnd.random() * 0.55, rnd.uniform(0, 6.28), rnd.uniform(2, 6)) for _ in range(40)]
    gl = glow_sprite(300, '#cfe0ff', 0.55)
    m = _warm_motes(211, 50, col=(255, 235, 190), amax=140, drift=(0.2, -0.8))
    am = text_block('Aameen', font(NASKH, 200), (255, 226, 150, 255), 800, stroke=5, stroke_col=(40, 30, 10))
    ls = text_block('Ya Rabbal Aalameen', font(NASKH, 84), (244, 236, 214, 255), 800, stroke=4)

    def dyn(f, t, u, ws, sx):
        x, y = ws(0.28, 0.26)
        put_glow(f, gl, x, y, 0.7 + 0.2 * math.sin(t * 1.5), 1.3)
        d = ImageDraw.Draw(f)
        for (fx, fy, ph, r) in tw:
            px, py = ws(fx, fy)
            a = int(200 * (0.5 + 0.5 * math.sin(t * 2.0 + ph)))
            d.ellipse([px - r / 2, py - r / 2, px + r / 2, py + r / 2], fill=(235, 240, 255, a))
        m(f, t)
        a = 0.0 if CARD else ease(seg(t, 11.4, 12.6))
        for im, yy in ((am, 330), (ls, 590)):
            s = im.copy(); s.putalpha(im.split()[3].point(lambda v: int(v * a)))
            f.alpha_composite(s, (int((W - s.width) / 2), yy))
        fade_to(f, (0, 0, 0), ease(seg(t, 14.6, 16.8)))
    return Photo(base, lambda u: (lerp(1.0, 1.22, ease(u)), 0.0, lerp(0.3, -0.3, ease(u))), dyn)


TIMELINE = [
    (0.0, 11.6, s_cem),
    (11.6, 18.2, s_shroud),
    (18.2, 29.9, s_weep),
    (29.9, 35.7, s_kafan),
    (35.7, 40.5, s_carry),
    (40.5, 44.3, s_salah),
    (44.3, 51.4, s_aerial),
    (51.4, 62.3, s_shovel),
    (62.3, 69.9, s_mound),
    (69.9, 86.1, s_rays),
    (86.1, 89.1, s_book),
    (89.1, 116.0, s_fire),
    (116.0, 129.0, s_silence),
    (129.0, 139.9, s_lamp),
    (139.9, 146.1, s_eye),
    (146.1, 160.2, s_candle),
    (160.2, 184.0, s_quran),
    (184.0, 205.4, s_dua),
    (205.4, 219.4, s_grave2),
    (219.4, 224.2, s_book2),
    (224.2, 241.0, s_moon),
]
