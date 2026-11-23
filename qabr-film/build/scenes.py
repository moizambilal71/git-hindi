"""Scene definitions. Every scene = backdrop + parallax paper layers + camera + dynamic overlay."""
import math, random
from PIL import Image, ImageDraw
from shapes import *


def ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def lerp(a, b, u):
    return a + (b - a) * u


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def seg(t, a, b):
    """0..1 progress of t within [a,b]."""
    return clamp((t - a) / (b - a)) if b > a else (1.0 if t >= a else 0.0)


class Scene:
    def __init__(self, bg, layers, cam=None, dyn=None):
        self.bg, self.layers, self.cam, self.dyn = bg, layers, cam, dyn
        self.t0 = self.t1 = 0

    def render(self, t):
        u = seg(t, self.t0, self.t1)
        z, cx, cy = self.cam(u) if self.cam else (1.0, 0, 0)
        f = self.bg.convert('RGBA')
        for L in self.layers:
            img, k = L[0], L[1]
            mx, my = (0, 0)
            if len(L) > 2 and L[2]:
                mx, my = L[2](t - self.t0, u)
            f.paste(img, (int(-M - k * cx + mx), int(-M - k * cy + my)), img)
        if self.dyn:
            self.dyn(f, t - self.t0, u, (z, cx, cy))
        if z != 1.0:
            cw, ch = W / z, H / z
            x0, y0 = (W - cw) / 2, (H - ch) / 2
            f = f.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BILINEAR)
        return f


# ---------------------------------------------------------------- dynamic helpers
def motes(n, seed, col=(255, 235, 200), amax=130, size=(2, 6), speed=(8, 26), area=(0, 0, W, H)):
    rnd = random.Random(seed)
    return [(rnd.uniform(area[0], area[2]), rnd.uniform(area[1], area[3]), rnd.uniform(*speed), rnd.uniform(*size),
             rnd.uniform(0, 6.28), rnd.uniform(0.35, 1.0), col, amax) for _ in range(n)]


def draw_motes(f, ms, t, drift=(0.4, -1.0), fade=1.0):
    ov = Image.new('RGBA', f.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for (x, y, sp, sz, ph, br, col, amax) in ms:
        xx = (x + drift[0] * sp * t + 25 * math.sin(t * 0.6 + ph)) % W
        yy = (y + drift[1] * sp * t) % H
        a = int(amax * br * (0.6 + 0.4 * math.sin(t * 1.3 + ph)) * fade)
        d.ellipse([xx - sz, yy - sz, xx + sz, yy + sz], fill=col + (a,))
    f.alpha_composite(ov)


def put_glow(f, spr, cx, cy, alpha=1.0, scale=1.0):
    if alpha <= 0.01:
        return
    s = spr
    if scale != 1.0:
        s = spr.resize((int(spr.width * scale), int(spr.height * scale)), Image.BILINEAR)
    if alpha < 0.999:
        a = s.split()[3].point(lambda v: int(v * alpha))
        s = s.copy()
        s.putalpha(a)
    f.paste(s, (int(cx - s.width / 2), int(cy - s.height / 2)), s)


def put_fog(f, fog, t, y, speed=14, alpha=1.0):
    dx = -((t * speed) % 400)
    s = fog
    if alpha < 0.999:
        a = fog.split()[3].point(lambda v: int(v * alpha))
        s = fog.copy()
        s.putalpha(a)
    f.paste(s, (int(dx), int(y)), s)


def fade_to(f, col, a):
    if a <= 0.001:
        return
    ov = Image.new('RGBA', f.size, col + (int(255 * clamp(a)),))
    f.alpha_composite(ov)


def heart_pts(cx, cy, s):
    pts = []
    for i in range(0, 361, 6):
        a = math.radians(i)
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((cx + x * s, cy + y * s))
    return pts


def shard_img(size, col):
    rnd = random.Random(int(size * 7))
    n = 4
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.4, 0.4)
        r = size * rnd.uniform(0.45, 1.0)
        pts.append((size + r * math.cos(a), size + r * math.sin(a)))
    im = Image.new('RGBA', (size * 2, size * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).polygon(pts, fill=col + (255,))
    return im


def make_scroll():
    p = Paper('#efe2bd', shadow=0.5, blur=10, off=(0, 8))
    p.rrect(300, 880, 780, 1180, 18, '#efe2bd')
    p.rrect(270, 860, 330, 1200, 28, '#d8c590')
    p.rrect(750, 860, 810, 1200, 28, '#d8c590')
    for i in range(7):
        y = 925 + i * 36
        p.rrect(360, y, 700 - (i % 3) * 50, y + 10, 5, '#b49c62')
    return p.done()


# ================================================================= SCENES
def build_cem():
    bg = backdrop('#060d1c', '#1d2438', [(540, 560, 760, '#6f84b3', 0.40)])
    sky = Paper('#000000', shadow=0)
    rnd = random.Random(2)
    for _ in range(70):
        star(sky, rnd.randint(-50, W + 50), rnd.randint(-50, 900), rnd.randint(3, 8), '#c9d4ee', 4)
    sky.circ(540, 560, 118, '#f2e8c9')
    sky = sky.done()
    sk = Paper('#17213a', shadow=0.35, blur=10); skyline(sk, 1230, scale=1.0); sk = sk.done()
    h1 = Paper('#101829', shadow=0.5); hills(h1, 1380, 60, 3)
    for i in range(9):
        stone(h1, 80 + i * 125 + (i % 2) * 20, 1500 - (i % 3) * 20, 70, 130 + (i % 4) * 25, '#0c1322')
    h1 = h1.done()
    h2 = Paper('#080d17', shadow=0.6); hills(h2, 1600, 50, 5)
    for x, hh in [(150, 300), (420, 240), (700, 330), (950, 260)]:
        stone(h2, x, 1760, 120, hh, '#060a12')
    cypress(h2, 60, 1700, 700); cypress(h2, 1030, 1700, 640)
    h2 = h2.done()
    h3 = Paper('#04070d', shadow=0.5); hills(h3, 1860, 40, 8)
    stone(h3, 250, 1960, 190, 420, '#03050a'); stone(h3, 830, 1960, 210, 480, '#03050a')
    h3 = h3.done()
    fog = fog_layer('#7d8fb8', 70, 1)
    gl = glow_sprite(520, '#9fb3e6', 0.5)
    ms = motes(60, 11)
    ti = text_block('اے غافل انسان!', font('NotoNaskhArabic_700Bold.ttf', 104), (244, 236, 214, 255), 900, stroke=3)
    t2 = text_block('ذرا اپنی قبر کا تصور کر', font('NotoNaskhArabic_700Bold.ttf', 72), (255, 214, 140, 255), 900, stroke=3)

    def dyn(f, t, u, cam):
        put_glow(f, gl, 540, 560, 0.9 + 0.08 * math.sin(t * 0.8))
        put_fog(f, fog, t, 1250, 10, 0.9)
        put_fog(f, fog, t + 9, 1560, 18, 0.7)
        draw_motes(f, ms, t)
        a = ease(seg(t, 1.8, 3.2)) * (1 - ease(seg(t, 7.2, 9.0)))
        if a > 0.01:
            for im, y in ((ti, 330), (t2, 470)):
                s = im.copy(); s.putalpha(im.split()[3].point(lambda v: int(v * a)))
                f.alpha_composite(s, (int((W - s.width) / 2), int(y - 18 * (1 - a))))
    return Scene(bg, [(sky, .08), (sk, .18), (h1, .38), (h2, .65), (h3, 1.0)],
                 lambda u: (lerp(1.0, 1.13, ease(u)), 0, lerp(90, -70, ease(u))), dyn)


def build_dead():
    bg = backdrop('#0b080a', '#28180f', [(540, 1000, 820, '#8a5226', 0.55), (540, 330, 420, '#52689a', 0.35)])
    wall = Paper('#171012', shadow=0.4)
    wall.rect(-M, -M, W + M, 1300, '#1a1214')
    wall.rrect(380, 120, 700, 780, 160, '#3a4a78')
    wall.rect(380, 420, 700, 780, '#3a4a78')
    wall.rect(536, 120, 544, 780, '#1a1214'); wall.rect(380, 400, 700, 408, '#1a1214')
    wall = wall.done()
    floor = Paper('#1f1510', shadow=0.5); floor.poly([(-M, 1250), (W + M, 1250), (W + M, H + M), (-M, H + M)]); floor = floor.done()
    mid = Paper('#ece7d8', shadow=0.7, blur=20, off=(0, 20)); shrouded(mid, 540, 1400, 700, 120); mid = mid.done()
    fam = Paper('#0b0706', shadow=0.5)
    human(fam, 110, 1560, 520, pose='sit', facing=1); human(fam, 250, 1640, 400, pose='sit', facing=1)
    human(fam, 960, 1560, 540, pose='sit', facing=-1); human(fam, 830, 1640, 410, pose='bow', facing=-1)
    fam = fam.done()
    lamp = Paper('#0a0605', shadow=0.4)
    lamp.ell(60, 1760, 220, 1830); lamp.rect(100, 1720, 180, 1770); lamp.ell(110, 1690, 170, 1735)
    lamp = lamp.done()
    bm = beam_sprite(320, 760, 1000, '#9db4e8', 0.28)
    gl = glow_sprite(430, '#ffb866', 0.85)
    ms = motes(70, 21, area=(300, 150, 800, 1250))
    drops = [(21.2, 150, 1420), (23.4, 900, 1430), (25.0, 300, 1470), (26.6, 760, 1480), (27.6, 160, 1420)]

    def dyn(f, t, u, cam):
        f.paste(bm, (int(540 - bm.width / 2), 380), bm)
        fl = 0.85 + 0.12 * math.sin(t * 7.3) * math.sin(t * 2.1)
        put_glow(f, gl, 140, 1700, fl)
        put_glow(f, gl, 540, 1330, 0.25 * fl, 1.4)
        draw_motes(f, ms, t)
        d = ImageDraw.Draw(f)
        for (t0, x, y) in drops:
            tt = t + 11.6 - t0
            if 0 < tt < 1.3:
                yy = y + tt * tt * 160
                d.ellipse([x - 5, yy - 8, x + 5, yy + 8], fill=(190, 215, 255, int(220 * (1 - tt / 1.3))))
    return Scene(bg, [(wall, .1), (floor, .25), (mid, .55), (fam, .8), (lamp, 1.2)],
                 lambda u: (lerp(1.0, 1.38, ease(u)), 0, lerp(0, 190, ease(u))), dyn)


def build_wash():
    bg = backdrop('#05121a', '#12303a', [(540, 900, 700, '#4d8fa0', 0.35)])
    tb = Paper('#0b1a20', shadow=0.5); tb.rrect(60, 1180, 1020, 1400, 40); tb.rect(120, 1380, 180, 1960); tb.rect(900, 1380, 960, 1960); tb = tb.done()
    sh = Paper('#ece7d8', shadow=0.7, blur=22, off=(0, 22)); shrouded(sh, 540, 1090, 860, 190); sh = sh.done()
    bowl = Paper('#0a1519', shadow=0.4); bowl.ell(740, 260, 1000, 330); bowl.poly([(740, 295), (1000, 295), (950, 380), (790, 380)]); bowl = bowl.done()
    ms = motes(40, 4, col=(190, 225, 240), area=(0, 0, W, 1300))
    ties = [32.6, 33.8, 35.0]

    def dyn(f, t, u, cam):
        d = ImageDraw.Draw(f)
        # water drops with ripples (ghusl) 0..2.5s
        for i in range(9):
            t0 = i * 0.33
            tt = (t - t0) % 1.1
            x = 330 + (i * 97) % 380
            if t < 3.2:
                if tt < 0.35:
                    yy = 300 + tt * 3000 * tt * 3
                    d.ellipse([x - 6, yy - 10, x + 6, yy + 10], fill=(200, 230, 245, 230))
                else:
                    r = (tt - 0.35) * 160
                    a = int(190 * (1 - (tt - 0.35) / 0.75))
                    d.ellipse([x - r, 1090 - r * 0.35, x + r, 1090 + r * 0.35], outline=(200, 230, 245, max(0, a)), width=4)
        # ties tightening bands
        for k_, ts in enumerate(ties):
            g = ease(seg(t + 29.9, ts, ts + 0.5))
            if g > 0:
                x = 330 + k_ * 190
                h = 190 * g
                d.rectangle([x - 7, 1090 - h / 2, x + 7, 1090 + h / 2], fill=(168, 159, 134, 255))
        draw_motes(f, ms, t)
    return Scene(bg, [(tb, .3), (sh, .6), (bowl, .5)], lambda u: (lerp(1.0, 1.25, ease(u)), 0, lerp(20, 60, u)), dyn)


def _dusk_bg():
    return backdrop('#14122a', '#4a2f3c', [(540, 1250, 800, '#d68a5c', 0.5), (850, 430, 300, '#f2d9a0', 0.30)])


def build_walk():
    bg = _dusk_bg()
    far = Paper('#241e3a', shadow=0.3); skyline(far, 1280); far.circ(850, 430, 90, '#f6e6b8'); far = far.done()
    far = far
    h1 = Paper('#1a1429', shadow=0.5); hills(h1, 1420, 40, 7)
    for i in range(12):
        stone(h1, 40 + i * 100, 1520 - (i % 3) * 14, 56, 100 + (i % 4) * 20, '#150f22')
    h1 = h1.done()
    proc = Paper('#07050c', shadow=0.5, w=LW + 1800)
    base = 1680
    # procession drawn on a wide sheet; bier carried by four
    bx = 1100
    for k, dx in enumerate((-120, -50, 50, 120)):
        pass
    for dx in (-190, -85, 40, 150):
        human(proc, bx + dx, base, 560, pose='stand')
    proc.rrect(bx - 250, base - 470, bx + 270, base - 410, 24, '#ece7d8')
    for i in range(6):
        human(proc, bx - 340 - i * 105, base + (i % 2) * 10, 520 - (i % 3) * 25, pose='stand' if i % 3 else 'bow')
    proc = proc.done()
    near = Paper('#04030a', shadow=0.4); hills(near, 1820, 30, 2)
    for x in (120, 520, 940):
        stone(near, x, 1960, 150, 320, '#03020a')
    near = near.done()
    fog = fog_layer('#c79a96', 60, 3)
    ms = motes(40, 33, col=(255, 210, 170))

    def dyn(f, t, u, cam):
        put_fog(f, fog, t, 1500, 12, 0.8)
        draw_motes(f, ms, t)
    return Scene(bg, [(far, .1), (h1, .3), (proc, .5, lambda tl, u: (-560 + 520 * u, 4 * math.sin(tl * 5))), (near, 1.0)],
                 lambda u: (lerp(1.0, 1.08, u), lerp(-30, 30, u), 0), dyn)


def build_saf():
    bg = backdrop('#100f24', '#3b2736', [(540, 1100, 760, '#c4825a', 0.40)])
    far = Paper('#201a34', shadow=0.3); skyline(far, 1150, scale=0.8); far = far.done()
    g = Paper('#150f24', shadow=0.5); hills(g, 1250, 25, 4); g = g.done()
    rows = Paper('#07050c', shadow=0.5)
    for r, (y, h, n) in enumerate([(1350, 330, 7), (1500, 430, 6), (1700, 570, 5)]):
        sp = W / (n + 0.4)
        for i in range(n):
            human(rows, 60 + sp * (i + 0.5) + (r % 2) * 30, y, h, pose='bow' if i % 2 else 'stand', facing=1)
    rows = rows.done()
    bier = Paper('#ece7d8', shadow=0.6); bier.rrect(380, 1240, 700, 1290, 20); bier = bier.done()
    ms = motes(40, 41, col=(255, 210, 170))

    def dyn(f, t, u, cam):
        draw_motes(f, ms, t)
    return Scene(bg, [(far, .1), (g, .25), (bier, .5), (rows, .8)],
                 lambda u: (lerp(1.0, 1.28, ease(u)), 0, lerp(0, 120, ease(u))), dyn)


def build_burial():
    bg = backdrop('#0a0706', '#190e09', [(540, 660, 700, '#6a5a8a', 0.35)])
    sky = Paper('#000000', shadow=0)
    sky.rect(-M, -M, W + M, 700, '#2b2540'); sky.circ(240, 300, 90, '#d9cca0')
    sky = sky.done()
    sk = Paper('#1d1830', shadow=0.3); skyline(sk, 640, scale=0.7); sk = sk.done()
    soil = Paper('#3a2517', shadow=0.5, blur=12)
    soil.rect(-M, 640, W + M, H + M, '#3a2517')
    rnd = random.Random(9)
    for i in range(14):
        y = 700 + i * 90
        soil.poly([(-M, y), (W + M, y + rnd.randint(-30, 30)), (W + M, y + 26), (-M, y + 20)], '#4a3020' if i % 2 else '#2c1a10')
    for _ in range(80):
        soil.circ(rnd.randint(0, W), rnd.randint(660, H), rnd.randint(3, 9), '#2a190f')
    soil.rect(330, 600, 750, 1520, '#0b0605')            # grave pit
    soil = soil.done()
    grass = Paper('#17101a', shadow=0.4); grass.rect(-M, 628, W + M, 650); grass.rect(300, 626, 330, 660, '#3a2517'); grass.rect(750, 626, 780, 660, '#3a2517'); grass = grass.done()
    mL = Paper('#08060b', shadow=0.4)
    for x, hh, ps in [(170, 520, 'stand'), (260, 470, 'bow')]:
        human(mL, x, 636, hh, pose=ps, facing=1)
    mL = mL.done()
    mR = Paper('#08060b', shadow=0.4)
    for x, hh, ps in [(860, 530, 'stand'), (950, 470, 'bow')]:
        human(mR, x, 636, hh, pose=ps, facing=-1)
    mR = mR.done()
    body = Paper('#ece7d8', shadow=0.5, blur=12); shrouded(body, 540, 0, 360, 96); body = body.done()
    fall = [(random.Random(i).uniform(-70, 70), random.Random(i + 99).uniform(0, 1)) for i in range(200)]
    gl = glow_sprite(380, '#b9a8e6', 0.5)
    ms = motes(50, 7, col=(210, 180, 140), area=(340, 650, 740, 1500), speed=(4, 10))

    def pile_h(t):
        return 260 * ease(seg(t, 7.0, 13.5)) + 640 * ease(seg(t, 13.5, 22.0))

    def dyn(f, t, u, cam):
        d = ImageDraw.Draw(f)
        # lowering: body descends with two ropes (0..4.3 s)
        yb = lerp(560, 1420, ease(seg(t, 0.3, 4.0)))
        if t < 18:
            f.alpha_composite(body, (int(540 - W / 2 - M + 0), int(yb - H / 2 - M + M)) if False else (0, 0)) if False else None
            f.paste(body, (-M, int(yb - M - H / 2 + 0 * 0)), body) if False else None
        # body placed by offset: body layer drawn at y=0 center -> shift
        by = int(yb - 0)
        f.paste(body, (-M, by - M), body)
        if t < 4.4:
            d.line([(350, 640), (400, by - 10)], fill=(150, 120, 80, 255), width=5)
            d.line([(730, 640), (680, by - 10)], fill=(150, 120, 80, 255), width=5)
        # soil falling 7..24 s (handfuls)
        ph = pile_h(t)
        top = 1520 - ph
        if ph > 2:
            pts = [(330, 1520), (330, top + 70), (430, top + 20), (540, top - 10), (650, top + 20), (750, top + 70), (750, 1520)]
            d.polygon(pts, fill=(74, 48, 30, 255))
            d.polygon([(330, top + 70), (430, top + 20), (540, top - 10), (650, top + 20), (750, top + 70), (700, top + 90), (540, top + 40), (380, top + 90)], fill=(96, 63, 40, 255))
        if 7.0 < t < 24:
            for i, (ox, ph0) in enumerate(fall):
                cyc = 1.15
                tt = ((t - 7.0) / cyc) % 1.0
                k = (tt - ph0 * 0.25)
                if 0 < k < 0.6:
                    x = 540 + ox * (0.6 + k)
                    y = 640 + (k / 0.6) ** 1.8 * (top - 640)
                    r = 5 + (i % 4)
                    d.ellipse([x - r, y - r, x + r, y + r], fill=(112, 76, 48, 255))
        # mourners walk away (11.5..24 s)
        if t > 13:
            a = clamp(1 - seg(t, 18, 24))
            for i, x0 in enumerate((860, 950, 170, 260)):
                pass
        put_glow(f, gl, 540, 660, 0.9 * (1 - ease(seg(t, 18, 25))))
        draw_motes(f, ms, t, drift=(0, 0.2), fade=0.7)
        fade_to(f, (3, 2, 2), ease(seg(t, 22, 25.6)) * 0.85)
    sc = Scene(bg, [(sky, .05), (sk, .12), (soil, .5), (grass, .5), (mL, .5, lambda tl, u: (-max(0, tl - 12) * 85, 0)), (mR, .5, lambda tl, u: (max(0, tl - 12) * 85, 0))],
               lambda u: (lerp(1.0, 1.32, ease(u)), 0, lerp(-80, 480, ease(u))), dyn)
    return sc


def build_exam():
    bg = backdrop('#030203', '#120b09', [(540, 500, 600, '#cfd8ff', 0.30)])
    walls = Paper('#2a190f', shadow=0.6, blur=22)
    walls.rect(-M, -M, 250, H + M); walls.rect(830, -M, W + M, H + M)
    for i in range(10):
        walls.rect(150 + (i % 2) * 40, 200 + i * 190, 250, 230 + i * 190, '#3a2517')
        walls.rect(830, 260 + i * 190, 930 - (i % 2) * 40, 290 + i * 190, '#3a2517')
    walls = walls.done()
    floor = Paper('#0c0705', shadow=0.5); floor.rect(-M, 1700, W + M, H + M); floor = floor.done()
    scroll = make_scroll()
    bm = beam_sprite(300, 640, 1500, '#dfe6ff', 0.34)
    gl = glow_sprite(480, '#ffd98a', 0.9)
    orb = glow_sprite(150, '#ffe8b0', 0.95)
    ms = motes(80, 5, col=(255, 235, 200), area=(260, 0, 820, 1700))
    coins = [(430 + i * 85, 520 + (i % 3) * 110) for i in range(7)]
    ti = text_block('اعمال', font('NotoNaskhArabic_700Bold.ttf', 150), (255, 224, 150, 255), 800, stroke=3)

    def dyn(f, t, u, cam):
        bt = ease(seg(t, 0.2, 3.0))
        f.paste(bm, (int(540 - bm.width / 2), -200), bm) if bt > 0 else None
        # two abstract lights approach (no bodies depicted)
        s = ease(seg(t, 1.5, 6.0))
        for sx, tx in ((120, 380), (960, 700)):
            x = lerp(sx, tx, s)
            put_glow(f, orb, x, 1250, s, 1.7)
            ImageDraw.Draw(f).ellipse([x - 16, 1040, x + 16, 1420], fill=(255, 238, 190, int(255 * s)))
        # question ripples
        if 4.4 < t < 9.5:
            d = ImageDraw.Draw(f)
            for k_ in range(3):
                tt = (t - 4.4 - k_ * 0.9)
                if 0 < tt < 2.6:
                    r = tt * 190
                    d.ellipse([540 - r, 1250 - r * .6, 540 + r, 1250 + r * .6], outline=(255, 238, 190, int(200 * (1 - tt / 2.6))), width=5)
        # coins dissolving 9.5..16
        if 9.5 < t < 17:
            d = ImageDraw.Draw(f)
            for i, (x, y) in enumerate(coins):
                a = clamp(1 - seg(t, 10 + i * 0.7, 12 + i * 0.7))
                yy = y + (1 - a) * 90
                if a > 0.02:
                    d.ellipse([x - 38, yy - 38, x + 38, yy + 38], fill=(224, 176, 70, int(255 * a)), outline=(120, 86, 24, int(255 * a)), width=5)
                    d.ellipse([x - 22, yy - 22, x + 22, yy + 22], outline=(160, 120, 40, int(255 * a)), width=4)
        # scroll of deeds rises 16..19.2
        sg = ease(seg(t, 16.4, 19.2))
        if sg > 0:
            gp = 0.5 + 0.5 * sg
            put_glow(f, gl, 540, 1000, gp * (0.85 + 0.15 * math.sin(t * 3)), 1.0 + 0.5 * sg)
            f.paste(scroll, (-M, int(-M + (1 - sg) * 500)), scroll)
            a = ease(seg(t, 17.5, 18.8))
            if a > 0.01:
                s_ = ti.copy(); s_.putalpha(ti.split()[3].point(lambda v: int(v * a)))
                f.alpha_composite(s_, (int((W - s_.width) / 2), 560))
        draw_motes(f, ms, t, drift=(0, 0.6))
    return Scene(bg, [(walls, .6), (floor, .8)], lambda u: (lerp(1.0, 1.15, u), 0, lerp(0, 40, u)), dyn)


def build_sins():
    bg = backdrop('#140e18', '#3d2420', [(540, 1100, 900, '#e08a50', 0.45)])
    far = Paper('#241a2c', shadow=0.3)
    rnd = random.Random(12)
    x = -50
    while x < W + 100:
        w_, h_ = rnd.randint(130, 230), rnd.randint(360, 760)
        far.rect(x, 1260 - h_, x + w_, 1400, '#241a2c')
        for wy in range(1260 - h_ + 40, 1230, 90):
            for wx in range(int(x) + 22, int(x) + w_ - 30, 55):
                if rnd.random() < 0.5:
                    far.rect(wx, wy, wx + 24, wy + 40, '#d6934e')
        x += w_ + rnd.randint(-10, 30)
    far = far.done()
    gr = Paper('#1a1119', shadow=0.4); gr.rect(-M, 1420, W + M, H + M); gr = gr.done()
    man = Paper('#06040a', shadow=0.5)
    human(man, 280, 1760, 1120, pose='stand')
    man.poly([(330, 880), (700, 820), (712, 852), (350, 960)], '#06040a')          # pointing arm
    man.poly([(700, 820), (790, 808), (794, 826), (710, 852)], '#06040a')           # finger
    man = man.done()
    victims = Paper('#07060b', shadow=0.4)
    human(victims, 830, 1700, 540, pose='bow', facing=-1); human(victims, 960, 1740, 430, pose='bow', facing=-1)
    victims = victims.done()
    shards = [shard_img(s, c) for s, c in ((20, (216, 201, 166)), (28, (216, 201, 166)), (16, (160, 56, 44)), (24, (240, 224, 190)))]
    rnd2 = random.Random(77)
    ev = [(0.15 * i + rnd2.uniform(0, 0.1), rnd2.uniform(-80, 80), rnd2.randint(0, 3), rnd2.uniform(-300, 300)) for i in range(150)]
    heart = heart_pts(560, 1150, 15)

    def dyn(f, t, u, cam):
        t_abs = t + 89.1
        # shards fly from the shouter's mouth toward the victims (starts at 94.5)
        for (t0, oy, k, rot) in ev:
            tt = t_abs - 94.5 - t0
            if 0 < tt < 2.6:
                sp = 1.0 + (t_abs - 94.5) / 22
                x = 330 + tt * 330 * sp
                y = 820 + oy * (tt * 0.8) + tt * tt * 14
                sh = shards[k].rotate(rot * tt, resample=Image.BILINEAR)
                a = clamp(1 - (tt - 1.6) / 1.0)
                if a < 1:
                    sh = sh.copy(); sh.putalpha(sh.split()[3].point(lambda v: int(v * a)))
                f.paste(sh, (int(x - sh.width / 2), int(y - sh.height / 2)), sh)
        d = ImageDraw.Draw(f)
        # friend's heart cracks (108.7 - 110.9)
        hs = seg(t_abs, 108.4, 110.9)
        if 0 < hs < 1 or (hs >= 1 and t_abs < 113):
            a = int(255 * clamp(1 - seg(t_abs, 112.5, 114)))
            gap = ease(seg(t_abs, 109.6, 110.9)) * 40
            left = [(x_ - gap, y_ + gap * 0.3) for (x_, y_) in heart if x_ <= 540 + 8 * math.sin(y_ * 0.05)]
            right = [(x_ + gap, y_ + gap * 0.3) for (x_, y_) in heart if x_ > 540 + 8 * math.sin(y_ * 0.05)]
            ov = Image.new('RGBA', f.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            od.polygon([(x_ - gap, y_ + gap * .3) for (x_, y_) in heart[:len(heart) // 2 + 1]] if False else [(x_ - gap * (1 if x_ < 560 else -1), y_) for x_, y_ in heart], fill=(176, 62, 52, a))
            od.line([(560, 1060), (576, 1120), (548, 1170), (568, 1230), (560, 1330)], fill=(20, 8, 8, a), width=7)
            f.alpha_composite(ov)
    return Scene(bg, [(far, .15), (gr, .35), (victims, .6), (man, .8)], lambda u: (lerp(1.0, 1.12, u), lerp(-40, 40, u), 0), dyn)


def build_silence():
    bg = backdrop('#06070c', '#171820', [(560, 900, 700, '#b88a60', 0.38)])
    face = Paper('#050508', shadow=0.6, blur=26, off=(0, 18))
    profile(face, 520, 760, 520, '#050508')
    face = face.done()
    rim = glow_sprite(520, '#e0a574', 0.65)
    shards = [shard_img(s, c) for s, c in ((20, (216, 201, 166)), (28, (216, 201, 166)), (16, (160, 56, 44)))]
    rnd = random.Random(31)
    fr = [(rnd.uniform(100, 980), rnd.uniform(0, 1500), rnd.randint(0, 2), rnd.uniform(-60, 60)) for _ in range(60)]
    ms = motes(50, 52)
    ti = text_block('کہاں ہے تیری وہ زبان؟', font('NotoNaskhArabic_700Bold.ttf', 104), (244, 236, 214, 255), 940, stroke=4)

    def dyn(f, t, u, cam):
        put_glow(f, rim, 900, 760, 0.9, 1.2)
        for (x, y, k, rot) in fr:
            yy = (y + t * 22) % 1700
            a = clamp(1 - seg(t, 0.5, 5.0)) * 0.9
            if a > 0.02:
                sh = shards[k].rotate(rot * t)
                s2 = sh.copy(); s2.putalpha(sh.split()[3].point(lambda v: int(v * a)))
                f.paste(s2, (int(x), int(yy)), s2)
        # tear
        tt = (t - 3.2) % 3.4
        if t > 3.2 and tt < 2.4:
            yy = 700 + ease(tt / 2.4) * 420
            ImageDraw.Draw(f).ellipse([722 - 7, yy - 11, 722 + 7, yy + 11], fill=(200, 225, 255, int(230 * (1 - tt / 2.4))))
        a = ease(seg(t, 0.1, 1.0)) * (1 - ease(seg(t, 3.6, 5.0)))
        if a > 0.01:
            s_ = ti.copy(); s_.putalpha(ti.split()[3].point(lambda v: int(v * a)))
            f.alpha_composite(s_, (int((W - s_.width) / 2), 1100))
        draw_motes(f, ms, t)
    return Scene(bg, [(face, .6)], lambda u: (lerp(1.0, 1.28, ease(u)), lerp(0, 60, u), lerp(0, 60, u)), dyn)


def _spot_bg():
    return backdrop('#0a0b12', '#22232e', [(540, 1200, 800, '#9fb0d8', 0.40)])


def build_m1():
    bg = _spot_bg()
    crowd = Paper('#0a0a10', shadow=0.4)
    for i, x in enumerate((90, 230, 880, 1000, 350, 760)):
        human(crowd, x, 1500 + (i % 3) * 40, 420 + (i % 3) * 40, pose='stand', facing=1)
    crowd = crowd.done()
    gr = Paper('#0c0c14', shadow=0.3); gr.rect(-M, 1500, W + M, H + M); gr = gr.done()
    one = Paper('#030305', shadow=0.5); human(one, 540, 1640, 760, pose='bow'); one = one.done()
    bm = beam_sprite(240, 560, 1500, '#f2f6ff', 0.62)
    ms = motes(60, 61, col=(220, 230, 255), area=(300, 0, 780, 1600))

    def dyn(f, t, u, cam):
        f.paste(bm, (int(540 - bm.width / 2), 100), bm)
        draw_motes(f, ms, t, drift=(0, 0.5))
    return Scene(bg, [(gr, .4), (crowd, .5), (one, .85)], lambda u: (lerp(1.0, 1.2, u), 0, lerp(0, 90, u)), dyn)


def build_m2():
    bg = backdrop('#0e0a08', '#2a1f18', [(540, 1200, 800, '#d9a066', 0.50)])
    gr = Paper('#0d0a08', shadow=0.4); gr.rect(-M, 1560, W + M, H + M); gr.rect(-M, 1540, W + M, 1568, '#1c1510'); gr = gr.done()
    wall = Paper('#1a130f', shadow=0.4); wall.rect(-M, -M, W + M, 1540); wall = wall.done()
    man = Paper('#030303', shadow=0.5); human(man, 540, 1680, 700, pose='sit'); man.ell(640, 1600, 820, 1650); man.poly([(650, 1625), (810, 1625), (780, 1690), (680, 1690)]); man = man.done()
    bm = beam_sprite(260, 600, 1500, '#ffe9c0', 0.6)
    ms = motes(60, 62, col=(255, 220, 170), area=(300, 0, 780, 1600))

    def dyn(f, t, u, cam):
        f.paste(bm, (int(540 - bm.width / 2), 80), bm)
        draw_motes(f, ms, t, drift=(0, 0.5))
    return Scene(bg, [(wall, .3), (gr, .5), (man, .85)], lambda u: (lerp(1.0, 1.22, u), 0, lerp(0, 110, u)), dyn)


def build_m3():
    bg = backdrop('#04100f', '#0f2b2a', [(540, 900, 650, '#5fa8a0', 0.35)])
    eye = Paper('#e9e3d2', shadow=0.6, blur=22, off=(0, 18))
    pts_top = [(140 + i * 8, 900 - 330 * math.sin(math.pi * i / 100) ** 0.9) for i in range(0, 101, 2)]
    pts_bot = [(140 + i * 8, 900 + 250 * math.sin(math.pi * i / 100) ** 0.9) for i in range(100, -1, -2)]
    eye.poly(pts_top + pts_bot, '#ece6d4')
    eye.circ(540, 905, 205, '#4a2f1d'); eye.circ(540, 905, 120, '#140c07'); eye.circ(600, 840, 36, '#fbf7ea'); eye.circ(500, 960, 16, '#fbf7ea')
    lid = [(140 + i * 8, 900 - 330 * math.sin(math.pi * i / 100) ** 0.9) for i in range(0, 101, 2)]
    eye.line(lid, 16, '#16100c')
    eye = eye.done()
    ms = motes(40, 63, col=(190, 235, 230))

    def dyn(f, t, u, cam):
        d = ImageDraw.Draw(f)
        # tear gathers and rolls down
        g = ease(seg(t, 1.5, 3.2))
        if g > 0:
            y = 1160 + ease(seg(t, 2.8, 6.0)) * 420
            r = 10 + 12 * g
            d.ellipse([560 - r, y - r * 1.3, 560 + r, y + r * 1.3], fill=(195, 228, 255, 235), outline=(255, 255, 255, 255), width=3)
            if t > 2.8:
                d.line([(560, 1160), (560, y)], fill=(195, 228, 255, 140), width=6)
        draw_motes(f, ms, t)
    return Scene(bg, [(eye, .7)], lambda u: (lerp(1.0, 1.35, ease(u)), 0, lerp(0, 120, ease(u))), dyn)


def build_m4():
    bg = backdrop('#0c0805', '#2a1b10', [(540, 1500, 800, '#d08a44', 0.65)])
    walls = Paper('#1a120d', shadow=0.5); walls.rect(-M, -M, W + M, 1620); walls = walls.done()
    gr = Paper('#0a0705', shadow=0.4); gr.rect(-M, 1620, W + M, H + M); gr = gr.done()
    man = Paper('#050303', shadow=0.5); human(man, 540, 1700, 700, pose='kneel', facing=1); man = man.done()
    can = Paper('#d8cfb8', shadow=0.4, blur=8)
    for x in (200, 540, 880):
        pass
    can = None
    gl = glow_sprite(260, '#ffb060', 0.9)
    cx = (210, 870, 540)
    times = (3.4, 6.5, 9.6)
    ms = motes(40, 64, col=(255, 200, 140), area=(0, 600, W, 1800))
    heart = heart_pts(540, 700, 12)

    def dyn(f, t, u, cam):
        d = ImageDraw.Draw(f)
        for x, ts in zip(cx, times):
            d.rounded_rectangle([x - 18, 1590, x + 18, 1680], 6, fill=(216, 207, 184, 255))
            g = ease(seg(t, ts, ts + 0.6))
            if g > 0:
                fl = 0.8 + 0.2 * math.sin(t * 9 + x)
                put_glow(f, gl, x, 1560, g * fl, 1.0)
                d.ellipse([x - 8, 1530, x + 8, 1590], fill=(255, 220, 140, int(255 * g)))
        if t > 12.7:
            a = int(255 * ease(seg(t, 12.7, 13.4)))
            gap = ease(seg(t, 13.0, 14.0)) * 24
            ov = Image.new('RGBA', f.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            od.polygon([(x_ - gap * (1 if x_ < 540 else -1), y_) for x_, y_ in heart], fill=(176, 62, 52, a))
            od.line([(540, 560), (550, 620), (532, 660), (546, 720), (540, 790)], fill=(20, 8, 8, a), width=5)
            f.alpha_composite(ov)
        draw_motes(f, ms, t)
    return Scene(bg, [(walls, .3), (gr, .5), (man, .8)], lambda u: (lerp(1.0, 1.15, u), 0, lerp(0, 60, u)), dyn)


def build_hadith():
    bg = backdrop('#140e06', '#6a4a1e', [(540, 1000, 960, '#ffd98a', 0.65)])
    # radial rays image
    n = 1800
    yy, xx = np.mgrid[0:n, 0:n]
    ang = np.arctan2(yy - n / 2, xx - n / 2)
    dist = np.sqrt((xx - n / 2) ** 2 + (yy - n / 2) ** 2) / (n / 2)
    a = (0.5 + 0.5 * np.sin(ang * 14)) ** 3 * np.clip(1 - dist, 0, 1) ** 1.4 * 0.5
    arr = np.zeros((n, n, 4), np.uint8); arr[..., :3] = (255, 226, 150); arr[..., 3] = (a * 255).astype(np.uint8)
    rays = Image.fromarray(arr, 'RGBA').resize((1200, 1200), Image.BILINEAR)
    # star ornament
    orn = Paper('#c79a4a', shadow=0.0, w=1100, h=1100)
    import shapes as S
    d_ = orn.d
    for k_ in range(2):
        pts = []
        for i in range(16):
            ang_ = math.pi * i / 8 + k_ * math.pi / 8
            r = 500 if i % 2 == 0 else 330
            pts.append((550 + r * math.cos(ang_), 550 + r * math.sin(ang_)))
        d_.polygon(pts, outline=(230, 190, 100, 160), width=6)
    orn = orn.img
    book = Paper('#efe3c0', shadow=0.6, blur=16, off=(0, 16))
    book.poly([(160, 1240), (540, 1190), (540, 1000), (170, 1030)], '#7a4f22')
    book.poly([(920, 1240), (540, 1190), (540, 1000), (910, 1030)], '#7a4f22')
    book.poly([(200, 1210), (540, 1160), (540, 1000), (205, 1020)], '#efe3c0')
    book.poly([(880, 1210), (540, 1160), (540, 1000), (875, 1020)], '#efe3c0')
    for i in range(6):
        y = 1050 + i * 24
        book.line([(235, y + 8 - i * 0.5), (500, y + 22)], 5, '#b49c62'); book.line([(580, y + 22), (845, y + 8 - i * 0.5)], 5, '#b49c62')
    book.rect(536, 1000, 544, 1190, '#9c7a40')
    book = book.done()
    gl = glow_sprite(600, '#ffe2a0', 0.95)
    nas = 'NotoNaskhArabic_700Bold.ttf'
    hd = text_block('«مسلمان کو گالی دینا فسق ہے»', font(nas, 74), (255, 232, 170, 255), 900, spacing=1.8, stroke=3, stroke_col=(60, 36, 10))
    ct = text_block('(صحیح بخاری و صحیح مسلم)', font(nas, 40), (240, 214, 160, 255), 900, spacing=1.7, stroke=2, stroke_col=(60, 36, 10))
    words = [(text_block(s, font('NotoNaskhArabic_700Bold.ttf', 84), (255, 232, 170, 255), 900, stroke=3, stroke_col=(60, 36, 10)), ts, y)
             for s, ts, y in (('ذکرِ الٰہی', 10.6, 340), ('درود شریف', 15.7, 470), ('تلاوتِ قرآن', 17.7, 600))]
    ms = motes(80, 71, col=(255, 230, 170), amax=190)

    def dyn(f, t, u, cam):
        put_glow(f, gl, 540, 1000, 0.9 + 0.07 * math.sin(t))
        r = rays.rotate(t * 3.0, resample=Image.BILINEAR)
        f.paste(r, (int(540 - r.width / 2), int(1000 - r.height / 2)), r)
        o = orn.rotate(-t * 2.0, resample=Image.BILINEAR)
        f.paste(o, (int(540 - o.width / 2), int(1000 - o.height / 2)), o)
        draw_motes(f, ms, t, drift=(0, -1.2))

        def show(im, y, a0, a1, a2, a3):
            a = ease(seg(t, a0, a1)) * (1 - ease(seg(t, a2, a3)))
            if a > 0.01:
                s_ = im.copy(); s_.putalpha(im.split()[3].point(lambda v: int(v * a)))
                f.alpha_composite(s_, (int((W - s_.width) / 2), int(y - 14 * (1 - a))))
        show(hd, 340, 4.2, 5.2, 8.6, 9.4)
        show(ct, 520, 7.6, 8.4, 10.0, 10.8)
        for im, ts, y in words:
            show(im, y, ts, ts + 0.7, 22.6, 23.6)
        f.paste(book, (-M, -M + int(8 * math.sin(t * 1.4))), book)
        fade_to(f, (10, 6, 2), ease(seg(t, 21.5, 23.8)) * 0.6)
    return Scene(bg, [], lambda u: (lerp(1.0, 1.1, u), 0, 0), dyn)


def _dawn_assets(night=False):
    if night:
        bg = backdrop('#0d1230', '#e8a366', [(540, 1250, 800, '#ffd09a', 0.75), (800, 420, 300, '#fff1c2', 0.25)])
    else:
        bg = backdrop('#2a2144', '#eea86a', [(540, 1250, 760, '#ffd7a0', 0.85)])
    sk = Paper('#4a3752' if not night else '#2a2a52', shadow=0.25, blur=10); skyline(sk, 1300); sk = sk.done()
    hl = Paper('#2b2038' if not night else '#1d1a3e', shadow=0.4); hills(hl, 1440, 40, 14)
    for i in range(11):
        stone(hl, 50 + i * 100, 1540 - (i % 3) * 14, 56, 100 + (i % 4) * 22, '#241a31' if not night else '#171638')
    hl = hl.done()
    nr = Paper('#0e0a16', shadow=0.4); hills(nr, 1760, 30, 16)
    for x in (130, 960):
        stone(nr, x, 1960, 150, 300, '#0b0812')
    cypress(nr, 70, 1800, 620, col='#0b0812'); cypress(nr, 1020, 1800, 560, col='#0b0812')
    nr = nr.done()
    return bg, sk, hl, nr


def build_dawn():
    bg, sk, hl, nr = _dawn_assets()
    fig = Paper('#0b0812', shadow=0.4); human(fig, 540, 1840, 820, pose='dua', facing=1); fig = fig.done()
    sun = glow_sprite(420, '#fff0c0', 1.0)
    rays = beam_sprite(60, 900, 1400, '#fff0c0', 0.28)
    petals = motes(70, 81, col=(255, 224, 170), amax=200, size=(3, 7), speed=(18, 46))

    sunl = Image.new('RGBA', (LW, LH), (0, 0, 0, 0))
    g_ = sun.resize((int(sun.width * 1.5), int(sun.height * 1.5)), Image.BILINEAR)
    sunl.paste(g_, (540 + M - g_.width // 2, 1380 + M - g_.height // 2), g_)
    ImageDraw.Draw(sunl).ellipse([540 + M - 90, 1380 + M - 90, 540 + M + 90, 1380 + M + 90], fill=(255, 244, 205, 255))

    def dyn(f, t, u, cam):
        draw_motes(f, petals, t, drift=(0.3, -1.4), fade=ease(seg(t, 6, 12)))
    return Scene(bg, [(sunl, 0.0, lambda tl, u: (0, -340 * ease(seg(tl, 0, 21)))), (sk, .15), (hl, .3), (nr, .6), (fig, .9)], lambda u: (lerp(1.0, 1.16, ease(u)), 0, lerp(40, -80, ease(u))), dyn)


def build_final():
    bg = backdrop('#050914', '#171e34', [(540, 1300, 650, '#7f6a50', 0.38), (540, 460, 520, '#6a7dab', 0.28)])
    sky = Paper('#000000', shadow=0); sky.circ(540, 460, 100, '#efe3c4'); sky = sky.done()
    sk = Paper('#121a2e', shadow=0.3); skyline(sk, 1170, scale=0.9); sk = sk.done()
    g = Paper('#0b111f', shadow=0.5); hills(g, 1450, 40, 22)
    for i in range(9):
        stone(g, 60 + i * 125, 1520, 60, 110 + (i % 3) * 25, '#090e19')
    g = g.done()
    grave = Paper('#070b15', shadow=0.6, blur=22)
    grave.poly([(180, 1760), (300, 1520), (780, 1520), (900, 1760)], '#0a0f1b')
    stone(grave, 540, 1530, 160, 360, '#06090f')
    grave = grave.done()
    near = Paper('#04060b', shadow=0.4); hills(near, 1850, 20, 3); cypress(near, 90, 1860, 760, col='#04060b'); cypress(near, 1000, 1860, 700, col='#04060b'); near = near.done()
    fam = Paper('#05070d', shadow=0.4)
    for i, (x, hh) in enumerate([(700, 560), (790, 520), (880, 480), (960, 440)]):
        human(fam, x, 1790, hh, pose='stand' if i % 2 == 0 else 'bow', facing=-1)
    fam = fam.done()
    scroll = make_scroll()
    gl = glow_sprite(520, '#ffd98a', 0.95)
    bm = beam_sprite(240, 700, 1500, '#ffe9b8', 0.45)
    fog = fog_layer('#7d8fb8', 60, 5)
    ms = motes(60, 91)
    ti = text_block('صرف تیرے اعمال', font('NotoNaskhArabic_700Bold.ttf', 112), (255, 226, 150, 255), 940, stroke=4)

    def dyn(f, t, u, cam):
        put_fog(f, fog, t, 1400, 12, 0.8)
        sg = ease(seg(t, 14.0, 17.5))
        if sg > 0:
            f.paste(bm, (int(540 - bm.width / 2), int(1500 - bm.height * sg + 200)), bm)
            put_glow(f, gl, 540, 1300 - 300 * sg, sg * (0.9 + 0.1 * math.sin(t * 3)), 0.9 + 0.5 * sg)
            f.paste(scroll, (-M, int(-M + 180 - 520 * sg)), scroll)
            a = ease(seg(t, 15.4, 16.6))
            s_ = ti.copy(); s_.putalpha(ti.split()[3].point(lambda v: int(v * a)))
            f.alpha_composite(s_, (int((W - s_.width) / 2), 360))
        draw_motes(f, ms, t)
    sc = Scene(bg, [(sky, .08), (sk, .15), (g, .3), (grave, .55), (fam, .8, lambda tl, u: (max(0, tl - 8.3) * 130 if tl > 8.3 else 0, 0)), (near, 1.0)],
               lambda u: (lerp(1.0, 1.15, ease(u)), 0, lerp(40, -40, ease(u))), dyn)
    return sc


def build_dua():
    bg, sk, hl, nr = _dawn_assets(night=True)
    sky = Paper('#000000', shadow=0)
    rnd = random.Random(4)
    for _ in range(60):
        star(sky, rnd.randint(0, W), rnd.randint(0, 900), rnd.randint(3, 8), '#e7e2d0', 4)
    crescent(sky, 820, 420, 130, '#f6e7b4')
    sky = sky.done()
    fig = Paper('#0b0812', shadow=0.4); human(fig, 540, 1840, 820, pose='dua', facing=1); fig = fig.done()
    sun = glow_sprite(480, '#ffe3a8', 1.0)
    petals = motes(80, 82, col=(255, 224, 170), amax=210, size=(3, 7), speed=(18, 46))
    am = text_block('آمین', font('NotoNaskhArabic_700Bold.ttf', 200), (255, 226, 150, 255), 800, stroke=4, stroke_col=(60, 36, 10))
    ls = text_block('یا رب العالمین', font('NotoNaskhArabic_700Bold.ttf', 84), (244, 236, 214, 255), 800, stroke=3)

    sunl2 = Image.new('RGBA', (LW, LH), (0, 0, 0, 0))
    g2 = sun.resize((int(sun.width * 1.6), int(sun.height * 1.6)), Image.BILINEAR)
    sunl2.paste(g2, (540 + M - g2.width // 2, 1180 + M - g2.height // 2), g2)

    def dyn(f, t, u, cam):
        draw_motes(f, petals, t, drift=(0.3, -1.4))
        a = ease(seg(t, 11.4, 12.6))
        if a > 0:
            for im, y in ((am, 330), (ls, 590)):
                s_ = im.copy(); s_.putalpha(im.split()[3].point(lambda v: int(v * a)))
                f.alpha_composite(s_, (int((W - s_.width) / 2), int(y)))
        fade_to(f, (0, 0, 0), ease(seg(t, 14.6, 16.8)))
    return Scene(bg, [(sky, .06), (sunl2, 0.0), (sk, .15), (hl, .3), (nr, .6), (fig, .9)],
                 lambda u: (lerp(1.12, 1.0, ease(u)), 0, lerp(-60, 30, ease(u))), dyn)


# (start, end, builder)
TIMELINE = [
    (0.0, 11.6, build_cem),
    (11.6, 29.9, build_dead),
    (29.9, 35.7, build_wash),
    (35.7, 40.5, build_walk),
    (40.5, 44.3, build_saf),
    (44.3, 69.9, build_burial),
    (69.9, 89.1, build_exam),
    (89.1, 116.0, build_sins),
    (116.0, 129.0, build_silence),
    (129.0, 135.2, build_m1),
    (135.2, 139.9, build_m2),
    (139.9, 146.1, build_m3),
    (146.1, 160.2, build_m4),
    (160.2, 184.0, build_hadith),
    (184.0, 205.4, build_dawn),
    (205.4, 224.2, build_final),
    (224.2, 241.0, build_dua),
]
XFADE = 0.7
