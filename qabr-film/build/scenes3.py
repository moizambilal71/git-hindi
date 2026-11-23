"""Card style: gradient + perspective grid + bold condensed title + arched photo window (reference-style graphics)."""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
os.environ['CARD'] = '1'
import scenes2 as S2
from scenes import ease, lerp, clamp, seg, XFADE, fade_to
from shapes import W, H, backdrop, rgb

HERE = os.path.dirname(os.path.abspath(__file__))
WX, WY, WW, WH = 90, 440, 900, 1100          # arch window on the 1080x1920 canvas
TITLE_FONT = os.path.join(HERE, 'fonts', 'Oswald_700Bold.ttf')


def make_bg(top, glow, bottom):
    bg = backdrop(top, bottom, [(540, 1000, 900, glow, 0.55), (540, 1450, 1100, glow, 0.20)])
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    hz = 1470                                    # perspective grid floor
    for i in range(1, 16):
        y = hz + (i ** 1.9) * 3.2
        if y > H: break
        d.line([(0, y), (W, y)], fill=(255, 220, 230, 26), width=2)
    for k in range(-12, 13):
        d.line([(540 + k * 36, hz), (540 + k * 190, H)], fill=(255, 220, 230, 22), width=2)
    bg = Image.alpha_composite(bg.convert('RGBA'), ov)
    return bg


def arch_mask(w, h, inset=0):
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    r = w // 2 - inset
    d.rounded_rectangle([inset, inset, w - inset, h - inset], 46, fill=255)
    d.pieslice([inset, inset, w - inset, inset + 2 * r], 180, 360, fill=255)
    d.rectangle([0, 0, w, inset + r - 1], fill=0)
    d.pieslice([inset, inset, w - inset, inset + 2 * r], 180, 360, fill=255)
    d.rectangle([inset, inset + r, w - inset, h - inset - 46], fill=255)
    return m


_MASK = None
_FRAME = None


def frame_assets():
    global _MASK, _FRAME
    if _MASK is None:
        _MASK = arch_mask(WW, WH)
        pad = 60
        shadow = Image.new('RGBA', (WW + 2 * pad, WH + 2 * pad), (0, 0, 0, 0))
        sh = Image.new('L', shadow.size, 0)
        sh.paste(_MASK, (pad, pad + 24))
        sh = sh.filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * 0.65))
        shadow.putalpha(sh)
        # thin pale outline, offset outwards (like the reference arch frame)
        ol = Image.new('RGBA', (WW + 2 * pad, WH + 2 * pad), (0, 0, 0, 0))
        out = arch_mask(WW + 36, WH + 36)
        ring = Image.new('L', ol.size, 0)
        ring.paste(out, (pad - 18, pad - 18))
        inner = Image.new('L', ol.size, 0)
        inner.paste(_MASK, (pad, pad))
        from PIL import ImageChops
        edge = ImageChops.subtract(ring.filter(ImageFilter.MaxFilter(3)), ring.filter(ImageFilter.MinFilter(7)))
        edge = ImageChops.subtract(edge, inner)
        ol = Image.new('RGBA', ol.size, (240, 215, 235, 0))
        ol.putalpha(edge.point(lambda v: int(v * 0.55)))
        _FRAME = (shadow, ol, pad)
    return _MASK, _FRAME


class Card:
    def __init__(self, photo, title, pal, seed):
        self.p, self.title, self.seed = photo, title, seed
        self.bg = make_bg(*pal)
        self.t0 = self.t1 = 0
        rnd = random.Random(seed)
        self.cross = [(rnd.choice([rnd.uniform(40, 150), rnd.uniform(930, 1040)]), rnd.uniform(380, 1500), rnd.uniform(0, 6.28), rnd.uniform(11, 20)) for _ in range(7)]
        self.dots = [(rnd.uniform(0, W), rnd.uniform(320, 1700), rnd.uniform(0, 6.28), rnd.uniform(1.5, 3.5)) for _ in range(45)]
        self.tf = None

    def title_img(self):
        if self.tf is None:
            for size in (124, 112, 100, 90, 80):
                f = ImageFont.truetype(TITLE_FONT, size)
                if f.getlength(self.title) <= 940:
                    lines = [self.title]
                    break
            else:
                f = ImageFont.truetype(TITLE_FONT, 92)
                ws = self.title.split(); half = (len(ws) + 1) // 2
                lines = [' '.join(ws[:half]), ' '.join(ws[half:])]
            lh = int(f.size * 1.02)
            im = Image.new('RGBA', (1000, lh * len(lines) + 40), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            for i, ln in enumerate(lines):
                x = (1000 - f.getlength(ln)) / 2
                d.text((x + 3, 20 + i * lh + 5), ln, font=f, fill=(0, 0, 0, 150))
                d.text((x, 20 + i * lh), ln, font=f, fill=(255, 226, 172, 255))
            self.tf = im
        return self.tf

    def render(self, t):
        mask, (shadow, ol, pad) = frame_assets()
        u = seg(t, self.t0, self.t1)
        tl = t - self.t0
        f = self.bg.copy()
        # photo window
        z, px, py = self.p.cam(u)
        cw = S2.BW / z
        ch = cw * WH / WW
        cx = S2.BW / 2 + px * (S2.BW - cw) / 2
        cy = S2.BH / 2 + py * (S2.BH - ch) / 2
        x0 = clamp(cx - cw / 2, 0, S2.BW - cw)
        y0 = clamp(cy - ch / 2, 0, S2.BH - ch)
        win = self.p.base.resize((WW, WH), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)).convert('RGBA')
        if self.p.dyn:
            sx = WW / cw
            ws = lambda fx, fy: ((fx * S2.BW - x0) * sx, (fy * S2.BH - y0) * sx)
            self.p.dyn(win, tl, u, ws, sx)
        pop = 0.96 + 0.04 * ease(seg(tl, 0, 0.7))
        a = ease(seg(tl, 0, 0.5))
        f.alpha_composite(shadow, (WX - pad, WY - pad))
        f.alpha_composite(ol, (WX - pad, WY - pad))
        layer = Image.new('RGBA', (WW, WH), (0, 0, 0, 0))
        layer.paste(win, (0, 0), mask)
        f.alpha_composite(layer, (WX, WY))
        # sparkle crosses + dust
        d = ImageDraw.Draw(f)
        for (x, y, ph, r) in self.cross:
            al = int(210 * (0.35 + 0.65 * max(0, math.sin(t * 1.3 + ph))))
            yy = y + 14 * math.sin(t * 0.5 + ph)
            d.line([(x - r, yy), (x + r, yy)], fill=(255, 235, 245, al), width=2)
            d.line([(x, yy - r), (x, yy + r)], fill=(255, 235, 245, al), width=2)
        for (x, y, ph, r) in self.dots:
            al = int(150 * (0.3 + 0.7 * max(0, math.sin(t * 0.9 + ph))))
            yy = (y - t * 6) % H
            d.ellipse([x - r, yy - r, x + r, yy + r], fill=(255, 225, 235, al))
        # title
        ti = self.title_img()
        s = ti.copy(); aa = ease(seg(tl, 0.05, 0.6))
        s.putalpha(ti.split()[3].point(lambda v: int(v * aa)))
        f.alpha_composite(s, (40, int(150 - 24 * (1 - aa))))
        return f


def card(builder, title, pal, seed):
    return lambda: Card(builder(), title, pal, seed)


P = {
    'plum': ('#2a1a33', '#c4785e', '#160f28'), 'navy': ('#101a30', '#5a7fb8', '#0a0f20'), 'brown': ('#2b1b1d', '#b8774c', '#170f10'),
    'maroon': ('#2e1628', '#b8635a', '#170e1e'), 'indigo': ('#1c2142', '#8a9ad0', '#10142a'), 'earth': ('#2a1c14', '#c0813f', '#150e0a'),
    'steel': ('#0e1830', '#5a86b8', '#080d1c'), 'gold': ('#2a1c0a', '#e0a448', '#140c04'), 'red': ('#2e1010', '#e0703a', '#160707'),
    'gray': ('#18181e', '#8a8a9c', '#0c0c10'), 'teal': ('#0c2326', '#4aa09a', '#071214'), 'ember': ('#1e1208', '#d8904a', '#0e0804'),
    'night': ('#0b1130', '#4a6cba', '#060a1c'), 'violet': ('#2a1a44', '#9a68c0', '#150c26'),
}
T = S2
TIMELINE = [
    (0.0, 11.6, card(T.s_cem, 'QABR KA TASAWWUR', P['plum'], 1)),
    (11.6, 18.2, card(T.s_shroud, 'TU MAR CHUKA HAI', P['navy'], 2)),
    (18.2, 29.9, card(T.s_weep, 'GHAR WALE RO RAHE HAIN', P['brown'], 3)),
    (29.9, 35.7, card(T.s_kafan, 'GHUSL AUR SAFED KAFAN', P['maroon'], 4)),
    (35.7, 40.5, card(T.s_carry, 'QABRISTAAN TAK KA SAFAR', P['plum'], 5)),
    (40.5, 44.3, card(T.s_salah, 'NAMAZ-E-JANAZA', P['indigo'], 6)),
    (44.3, 51.4, card(T.s_aerial, 'TAREEK QABR MEIN', P['earth'], 7)),
    (51.4, 62.3, card(T.s_shovel, 'MITTI DAALI JA RAHI HAI', P['earth'], 8)),
    (62.3, 69.9, card(T.s_mound, 'AB TERE SAATH KOI NAHI', P['gray'], 9)),
    (69.9, 86.1, card(T.s_rays, 'QABR KA IMTIHAAN', P['steel'], 10)),
    (86.1, 89.1, card(T.s_book, "SIRF TERE A'MAAL", P['gold'], 11)),
    (89.1, 116.0, card(T.s_fire, 'TU KAISE JEETA THA?', P['red'], 12)),
    (116.0, 129.0, card(T.s_silence, 'KAHAN HAI TERI ZUBAAN?', P['gray'], 13)),
    (129.0, 139.9, card(T.s_lamp, 'KYA YAAD HAI?', P['navy'], 14)),
    (139.9, 146.1, card(T.s_eye, 'AANKHON MEIN AANSOO', P['teal'], 15)),
    (146.1, 160.2, card(T.s_candle, 'KAASH!', P['ember'], 16)),
    (160.2, 184.0, card(T.s_quran, 'GAALI DENA FISQ HAI', P['gold'], 17)),
    (184.0, 205.4, card(T.s_dua, 'ABHI WAQT HAI', P['violet'], 18)),
    (205.4, 219.4, card(T.s_grave2, 'EK DIN YAHAN UTARNA HAI', P['night'], 19)),
    (219.4, 224.2, card(T.s_book2, "SIRF TERE A'MAAL", P['gold'], 20)),
    (224.2, 241.0, card(T.s_moon, 'AAMEEN', P['night'], 21)),
]
