import os, sys
os.environ['CARD'] = '1'
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import shapes
shapes.FONTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
import scenes2 as S2
import scenes3 as S3
W, H = 1080, 1920
OSW = S3.TITLE_FONT


def thumb(out, img, fit, crop_box, lines, pal, pill, grade, hl_line=None):
    bg = S3.make_bg(*pal)
    WW, WH, WX, WY = 900, 1010, 90, 610
    mask = S3.arch_mask(WW, WH)
    pad = 60
    sh = Image.new('L', (WW + 2 * pad, WH + 2 * pad), 0); sh.paste(mask, (pad, pad + 24))
    sh = sh.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.7))
    shadow = Image.new('RGBA', sh.size, (0, 0, 0, 0)); shadow.putalpha(sh)
    bg.alpha_composite(shadow, (WX - pad, WY - pad))
    # outline ring
    ring = Image.new('L', sh.size, 0); ring.paste(S3.arch_mask(WW + 40, WH + 40), (pad - 20, pad - 20))
    inner = Image.new('L', sh.size, 0); inner.paste(mask, (pad, pad))
    edge = ImageChops.subtract(ImageChops.subtract(ring.filter(ImageFilter.MaxFilter(3)), ring.filter(ImageFilter.MinFilter(9))), inner)
    ol = Image.new('RGBA', sh.size, (255, 226, 190, 0)); ol.putalpha(edge.point(lambda v: int(v * 0.8)))
    bg.alpha_composite(ol, (WX - pad, WY - pad))
    base = S2.prep(img, fit=fit, grade=grade)
    x0, y0, cw = crop_box
    ch = cw * WH / WW
    win = base.resize((WW, WH), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch)).convert('RGBA')
    layer = Image.new('RGBA', (WW, WH), (0, 0, 0, 0)); layer.paste(win, (0, 0), mask)
    bg.alpha_composite(layer, (WX, WY))
    d = ImageDraw.Draw(bg)
    # title (3 lines max, bold condensed, cream with highlight line in gold)
    y = 150
    for i, ln in enumerate(lines):
        size = 148 if len(ln) <= 14 else 128
        f = ImageFont.truetype(OSW, size)
        x = (W - f.getlength(ln)) / 2
        col = (255, 196, 90, 255) if i == hl_line else (255, 240, 214, 255)
        d.text((x + 4, y + 6), ln, font=f, fill=(0, 0, 0, 170))
        d.text((x, y), ln, font=f, fill=col, stroke_width=2, stroke_fill=(30, 14, 20, 255))
        y += int(size * 1.0)
    # pill
    pf = ImageFont.truetype(OSW, 62)
    pw = pf.getlength(pill) + 110
    px = (W - pw) / 2
    d.rounded_rectangle([px, 1560, px + pw, 1560 + 106], 53, fill=(255, 236, 190, 255))
    d.text(((W - pf.getlength(pill)) / 2, 1560 + 16), pill, font=pf, fill=(44, 22, 28, 255))
    bg.convert('RGB').save(out, quality=95)


O = '/home/user/git-hindi/qabr-film/out'
thumb(f'{O}/thumbnail_A_qabr_saath_kya.png', 'img04.jpg', True, (95, 330, 1160), ['QABR MEIN', 'TERE SAATH', 'KYA JAYEGA?'], S3.P['maroon'], 'AAKHIR TAK DEKHEIN', dict(bright=1.0, contrast=1.12, sat=1.0), hl_line=2)
thumb(f'{O}/thumbnail_B_zubaan.png', 'img13.jpg', True, (95, 380, 1160), ['AAJ KAHAN HAI', 'TERI WOH', 'ZUBAAN?'], S3.P['gray'], 'YEH VIDEO ZAROOR DEKHEIN', dict(bright=1.05, contrast=1.1, sat=1.0), hl_line=2)
