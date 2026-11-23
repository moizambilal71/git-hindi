"""Paper-cut lightbox primitives: layered paper shapes with baked soft shadows."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
M = 100                      # layer margin so parallax never exposes edges
LW, LH = W + 2 * M, H + 2 * M
FONTDIR = None


def P(x, y):
    return (x + M, y + M)


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class Paper:
    """One sheet of cut paper. Draw in canvas coords, call done() to bake shadow."""

    def __init__(self, color, shadow=0.6, blur=18, off=(0, 12), w=LW, h=LH):
        self.img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.c = rgb(color) if isinstance(color, str) else color
        self.shadow, self.blur, self.off = shadow, blur, off

    def _c(self, col):
        if col is None:
            return self.c
        return rgb(col) if isinstance(col, str) else col

    def poly(self, pts, col=None):
        self.d.polygon([P(*p) for p in pts], fill=self._c(col))

    def ell(self, x0, y0, x1, y1, col=None):
        a, b = P(x0, y0), P(x1, y1)
        self.d.ellipse([a, b], fill=self._c(col))

    def circ(self, x, y, r, col=None):
        self.ell(x - r, y - r, x + r, y + r, col)

    def rect(self, x0, y0, x1, y1, col=None):
        self.d.rectangle([P(x0, y0), P(x1, y1)], fill=self._c(col))

    def rrect(self, x0, y0, x1, y1, r, col=None):
        self.d.rounded_rectangle([P(x0, y0), P(x1, y1)], r, fill=self._c(col))

    def line(self, pts, width, col=None):
        self.d.line([P(*p) for p in pts], fill=self._c(col), width=width, joint='curve')

    def done(self):
        a = self.img.split()[3]
        sh = Image.new('RGBA', self.img.size, (0, 0, 0, 0))
        sh.putalpha(a.point(lambda v: int(v * self.shadow)))
        sh = Image.merge('RGBA', (Image.new('L', sh.size, 0),) * 3 + (sh.split()[3],))
        sh = sh.transform(sh.size, Image.AFFINE, (1, 0, -self.off[0], 0, 1, -self.off[1]))
        sh = sh.filter(ImageFilter.GaussianBlur(self.blur))
        return Image.alpha_composite(sh, self.img)


# ---------------------------------------------------------------- backgrounds
def backdrop(top, bot, glows=(), size=(W, H)):
    w, h = size
    t = np.linspace(0, 1, h)[:, None, None]
    a, b = np.array(rgb(top), float), np.array(rgb(bot), float)
    img = a * (1 - t) + b * t
    img = img * np.ones((1, w, 1))
    yy, xx = np.mgrid[0:h, 0:w]
    for (cx, cy, r, col, s) in glows:
        d = np.sqrt(((xx - cx) / r) ** 2 + ((yy - cy) / r) ** 2)
        k = np.clip(1 - d, 0, 1) ** 2 * s
        img = img + k[..., None] * np.array(rgb(col), float)[None, None, :]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'RGB')


def glow_sprite(r, color, strength=1.0):
    """RGBA radial glow, alpha falls off smoothly."""
    n = int(r * 2)
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.sqrt((xx - r) ** 2 + (yy - r) ** 2) / r
    a = np.clip(1 - d, 0, 1) ** 2.2 * strength
    arr = np.zeros((n, n, 4), np.uint8)
    arr[..., :3] = rgb(color)
    arr[..., 3] = np.clip(a * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA')


def beam_sprite(w_top, w_bot, h, color, strength=0.5):
    arr = np.zeros((h, int(max(w_top, w_bot)) + 4, 4), np.uint8)
    arr[..., :3] = rgb(color)
    ww = arr.shape[1]
    yy, xx = np.mgrid[0:h, 0:ww]
    t = yy / h
    half = (w_top + (w_bot - w_top) * t) / 2
    d = np.abs(xx - ww / 2) / np.maximum(half, 1)
    a = np.clip(1 - d, 0, 1) ** 1.3 * (1 - t * 0.55) * strength
    arr[..., 3] = np.clip(a * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA')


def fog_layer(color, alpha, seed=1, w=W + 500, h=420):
    rnd = random.Random(seed)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for _ in range(14):
        cx, cy = rnd.randint(0, w), rnd.randint(h // 3, 2 * h // 3)
        rx, ry = rnd.randint(160, 340), rnd.randint(40, 100)
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=rgb(color) + (alpha,))
    return im.filter(ImageFilter.GaussianBlur(55))


def vignette(strength=0.8):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W * 0.72)) ** 2 + ((yy - H / 2) / (H * 0.66)) ** 2)
    a = np.clip((d - 0.45) / 0.75, 0, 1) ** 1.6 * strength
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 3] = np.clip(a * 255, 0, 255).astype(np.uint8)
    arr[..., :3] = (4, 5, 9)
    return Image.fromarray(arr, 'RGBA')


def grain_tile(seed=3):
    rng = np.random.default_rng(seed)
    n = rng.normal(128, 40, (H + 64, W + 64)).clip(0, 255).astype(np.uint8)
    arr = np.stack([n, n, n, np.full_like(n, 16)], -1)
    return Image.fromarray(arr, 'RGBA')


# ---------------------------------------------------------------- motifs
def moon(p, cx, cy, r, col='#f1e6c4', bite=0.0):
    p.circ(cx, cy, r, col)
    if bite:
        p.circ(cx + r * bite, cy - r * 0.08, r * 0.92, '#000000')  # removed later by crescent()


def crescent(p, cx, cy, r, col='#f3e3b0'):
    """True crescent via mask."""
    m = Image.new('L', (LW, LH), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([P(cx - r, cy - r), P(cx + r, cy + r)], fill=255)
    d.ellipse([P(cx - r + r * 0.42, cy - r - r * 0.06), P(cx + r + r * 0.42, cy + r - r * 0.06)], fill=0)
    layer = Image.new('RGBA', (LW, LH), rgb(col) + (0,))
    layer.putalpha(m)
    p.img.alpha_composite(layer)


def star(p, cx, cy, r, col='#f3e3b0', n=4):
    pts = []
    for i in range(n * 2):
        ang = math.pi * i / n - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.28
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    p.poly(pts, col)


def stone(p, x, base, w, h, col=None):
    """Arched gravestone."""
    p.rect(x - w / 2, base - h + w / 2, x + w / 2, base + 40, col)
    p.ell(x - w / 2, base - h, x + w / 2, base - h + w, col)


def stone_flat(p, x, base, w, h, col=None, tilt=0):
    p.poly([(x - w / 2, base), (x - w / 2 + tilt, base - h), (x + w / 2 + tilt, base - h), (x + w / 2, base)], col)


def cypress(p, x, base, h, w=None, col=None):
    w = w or h * 0.17
    pts = [(x, base - h)]
    for i in range(1, 9):
        t = i / 8
        pts.append((x + w * math.sin(math.pi * min(1, t * 1.15)) * 0.5 * (1 - 0.1 * t), base - h + h * 0.88 * t))
    pts += [(x + w * 0.1, base), (x - w * 0.1, base)]
    for i in range(8, 0, -1):
        t = i / 8
        pts.append((x - w * math.sin(math.pi * min(1, t * 1.15)) * 0.5 * (1 - 0.1 * t), base - h + h * 0.88 * t))
    p.poly(pts, col)


def hills(p, base_y, amp, seed, col=None, step=60, freq=1.0):
    rnd = random.Random(seed)
    ph = [rnd.random() * 6.28 for _ in range(3)]
    pts = [(-M, H + M)]
    x = -M
    while x <= W + M:
        y = base_y + amp * (math.sin(x * 0.004 * freq + ph[0]) * 0.55 + math.sin(x * 0.011 * freq + ph[1]) * 0.3 + math.sin(x * 0.027 * freq + ph[2]) * 0.15)
        pts.append((x, y))
        x += step
    pts.append((W + M, H + M))
    p.poly(pts, col)


def skyline(p, base, col=None, seed=5, scale=1.0):
    """Mosque domes + minarets."""
    def dome(cx, w, h):
        p.ell(cx - w / 2, base - h * 1.1, cx + w / 2, base + h * 0.9, col)
        p.rect(cx - w / 2, base - 8, cx + w / 2, base + 200, col)
        p.rect(cx - 3, base - h * 1.1 - 40 * scale, cx + 3, base - h * 1.0, col)
        p.circ(cx, base - h * 1.1 - 44 * scale, 8 * scale, col)

    def minaret(cx, h, w=26):
        p.rect(cx - w / 2, base - h, cx + w / 2, base + 200, col)
        p.rect(cx - w * 0.9, base - h + 60, cx + w * 0.9, base - h + 80, col)
        p.poly([(cx - w * 0.7, base - h), (cx + w * 0.7, base - h), (cx, base - h - 90 * scale)], col)
    dome(540, 330 * scale, 150 * scale)
    dome(380, 150 * scale, 80 * scale)
    dome(700, 150 * scale, 80 * scale)
    minaret(190, 330 * scale)
    minaret(890, 330 * scale)
    p.rect(-M, base, W + M, base + 300, col)


def human(p, x, base, h, col=None, pose='stand', facing=1):
    """Paper-cut person (robe silhouette). pose: stand, sit, kneel, bow, dua."""
    c = col
    r = h * 0.075
    if pose == 'stand' or pose == 'dua':
        p.circ(x, base - h + r, r, c)
        p.poly([(x - h * 0.07, base - h + r * 1.6), (x + h * 0.07, base - h + r * 1.6),
                (x + h * 0.13, base - h * 0.68), (x + h * 0.17, base), (x - h * 0.17, base), (x - h * 0.13, base - h * 0.68)], c)
        if pose == 'dua':
            hx = x + facing * h * 0.07
            p.poly([(x - h * 0.1, base - h * 0.74), (hx - h * 0.1, base - h * 0.52), (hx + h * 0.1, base - h * 0.52), (x + h * 0.1, base - h * 0.74)], c)
            p.rrect(hx - h * 0.1, base - h * 0.58, hx + h * 0.1, base - h * 0.47, int(h * 0.05), c)
    elif pose == 'bow':
        hx = x + facing * h * 0.1
        p.circ(hx, base - h * 0.8 + r, r, c)
        p.poly([(x - h * 0.08, base - h * 0.78), (hx + h * 0.02, base - h * 0.78),
                (x + h * 0.14, base - h * 0.4), (x + h * 0.17, base), (x - h * 0.17, base), (x - h * 0.12, base - h * 0.5)], c)
    elif pose == 'sit':
        hx = x + facing * h * 0.05
        p.circ(hx, base - h * 0.62, r, c)
        p.poly([(x - h * 0.1, base - h * 0.55), (hx + h * 0.07, base - h * 0.55), (x + h * 0.22, base - h * 0.2),
                (x + h * 0.34, base), (x - h * 0.34, base), (x - h * 0.22, base - h * 0.25)], c)
    elif pose == 'kneel':
        hx = x + facing * h * 0.12
        p.circ(hx, base - h * 0.55, r, c)
        p.poly([(x - h * 0.08, base - h * 0.5), (hx + h * 0.05, base - h * 0.5), (x + h * 0.15, base - h * 0.2),
                (x + h * 0.28, base), (x - h * 0.25, base), (x - h * 0.12, base - h * 0.3)], c)


def shrouded(p, x, y, length, thick, col='#ece7d8', fold='#cfc7b0', tie='#a89f86', vertical=False):
    """White burial cloth wrapping a lying figure, centered at (x,y). Horizontal by default (head at left)."""
    if vertical:
        # draw horizontal on temp paper then rotate
        tmp = Paper(col, shadow=0, w=LW, h=LH)
        shrouded(tmp, W / 2, H / 2, length, thick, col, fold, tie)
        im = tmp.img.rotate(90, expand=False, center=(LW / 2, LH / 2))
        p.img.alpha_composite(im, (int(x - W / 2), int(y - H / 2)))
        return
    x0, x1 = x - length / 2, x + length / 2
    p.rrect(x0, y - thick / 2, x1, y + thick / 2, int(thick * 0.5), col)
    p.circ(x0 + thick * 0.45, y, thick * 0.62, col)               # head bump
    p.poly([(x1 - length * 0.12, y - thick * 0.5), (x1, y - thick * 0.22), (x1, y + thick * 0.22), (x1 - length * 0.12, y + thick * 0.5)], col)
    for fx in (0.22, 0.38, 0.55, 0.72):                           # fold lines
        xx = x0 + length * fx
        p.line([(xx, y - thick * 0.45), (xx + thick * 0.12, y), (xx, y + thick * 0.45)], max(2, int(thick * 0.05)), fold)
    for tx in (0.14, 0.5, 0.9):                                   # ties
        xx = x0 + length * tx
        p.rect(xx - 4, y - thick * 0.5, xx + 4, y + thick * 0.5, tie)


def profile(p, cx, cy, s, col, lips_closed=True):
    """Side-facing head silhouette (facing right). s = head height."""
    pts = [(-0.30, 0.62), (-0.34, 0.20), (-0.30, -0.15), (-0.18, -0.42), (0.02, -0.52), (0.20, -0.45),
           (0.30, -0.28), (0.31, -0.10), (0.38, 0.06), (0.30, 0.10), (0.31, 0.17), (0.28, 0.22), (0.31, 0.26),
           (0.26, 0.32), (0.27, 0.44), (0.20, 0.56), (0.08, 0.64), (0.0, 0.92), (-0.40, 1.1), (-0.60, 1.5), (-0.6, 2.0), (0.9, 2.0), (0.8, 1.4), (0.52, 1.05), (0.25, 0.9)]
    pts = [(cx + a * s, cy + b * s) for a, b in pts]
    # order matters for a simple polygon; hand-built outline
    p.poly(pts, col)


def font(name, size):
    return ImageFont.truetype(f"{FONTDIR}/{name}", size)


def text_block(text, fnt, color, maxw, spacing=1.7, align='center', stroke=0, stroke_col=(0, 0, 0)):
    """RTL-shaped, word-wrapped text -> RGBA image."""
    words = text.split()
    lines, cur = [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if fnt.getlength(t, direction='rtl', language='ur') <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    lh = int(fnt.size * spacing)
    img = Image.new('RGBA', (maxw + 40, lh * len(lines) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        wl = fnt.getlength(ln, direction='rtl', language='ur')
        x = (img.width - wl) / 2
        d.text((x, 20 + i * lh), ln, font=fnt, fill=color, direction='rtl', language='ur',
               stroke_width=stroke, stroke_fill=stroke_col)
    return img
