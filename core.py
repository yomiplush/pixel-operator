"""Image preparation and deterministic drawing plans (Pillow)."""
from dataclasses import dataclass
from pathlib import Path
from PIL import Image, ImageOps
from i18n import tr


@dataclass
class Artwork:
    image: Image.Image
    template: Image.Image
    groups: list
    swatches: list


"""Image preparation and deterministic drawing plans (Pillow)."""
import colorsys
from dataclasses import dataclass
from pathlib import Path
from PIL import Image, ImageOps
from i18n import tr

# Community palettes (hex). 'auto' selects no preset and keeps adaptive colors.
PRESET_PALETTES = {
    'auto': None,
    'DB32': ('000000', '222034', '45283c', '663931', '8f563b', 'df7126', 'd9a066',
             'eec39a', 'fbf236', '99e550', '6abe30', '37946e', '4b692f', '524b24',
             '323c39', '3f3f74', '306082', '5b6ee1', '639bff', '5fcde4', 'cbdbfc',
             'ffffff', '9badb7', '847e87', '696a6a', '595652', '76428a', 'ac3232',
             'd95763', 'd77bba', '8f974a', '8a6f30'),
    'PICO-8': ('000000', '1d2b53', '7e2553', '008751', 'ab5236', '5f574f', 'c2c3c7',
               'fff1e8', 'ff004d', 'ffa300', 'ffec27', '00e436', '29adff', '83769c',
               'ff77a8', 'ffccaa'),
    'Sweetie-16': ('1a1c2c', '5d275d', 'b13e53', 'ef7d57', 'ffcd75', 'a7f070', '38b764',
                   '257179', '29366f', '3b5dc9', '41a6f6', '73eff7', 'f4f4f4', '94b0c2',
                   '566c86', '333c57'),
    'GameBoy': ('0f380f', '306230', '8bac0f', '9bbc0f'),
}


def _parse_palette(palette):
    return [tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) for h in palette]


def _tune(color, brightness=0, contrast=0, saturation=0, hue=0):
    """Apply per-pixel tone changes. Each of brightness/contrast/saturation is
    in -100..100, hue in -180..180 degrees."""
    r, g, b = (c/255 for c in color)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    if hue:
        h = (h + hue/360) % 1.0
    if saturation:
        s = min(1.0, max(0.0, s * (1 + saturation/100)))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    r, g, b = (c*255 for c in (r, g, b))
    if contrast:
        f = 1 + contrast/100
        r, g, b = (128 + (c-128)*f for c in (r, g, b))
    if brightness:
        off = 255 * brightness/100
        r, g, b = (c + off for c in (r, g, b))
    return tuple(min(255, max(0, round(c))) for c in (r, g, b))


def _nearest(color, palette):
    best, bd = palette[0], 1 << 30
    for cand in palette:
        d = sum((color[i]-cand[i])**2 for i in range(3))
        if d < bd:
            bd, best = d, cand
    return best


def prepare(source, width=32, height=32, colors=16, dither=False,
            brightness=0, contrast=0, saturation=0, hue=0, palette='auto'):
    """Build an Artwork. `palette` names a preset in PRESET_PALETTES ('auto'
    for adaptive colors). Tone arguments pre-adjust the image colors."""
    if not (2 <= width <= 256 and 2 <= height <= 256 and 2 <= colors <= 64):
        raise ValueError(tr('Width/height must be 2-256 and colors 2-64.'))
    if palette not in PRESET_PALETTES:
        raise ValueError(tr('Unknown palette preset.'))
    with Image.open(source) as opened:
        original = ImageOps.exif_transpose(opened).convert('RGBA')
    fitted = ImageOps.contain(original, (width, height), Image.Resampling.LANCZOS)
    rgba = Image.new('RGBA', (width, height))
    rgba.paste(fitted, ((width-fitted.width)//2, (height-fitted.height)//2))

    def coords():
        for y in range(height):
            for x in range(width):
                if rgba.getpixel((x, y))[3] >= 128:
                    yield x, y

    opaque = list(coords())
    if not opaque:
        raise ValueError(tr('No opaque pixel to draw.'))

    fixed = _parse_palette(PRESET_PALETTES[palette]) if palette != 'auto' else None
    need_tune = bool(brightness or contrast or saturation or hue)

    def color_at(x, y):
        p = rgba.getpixel((x, y))
        return (p[0], p[1], p[2])

    result = Image.new('RGBA', rgba.size)
    if fixed is not None:
        groups = {}
        for x, y in opaque:
            rgb = _tune(color_at(x, y), brightness, contrast, saturation, hue) if need_tune else color_at(x, y)
            color = _nearest(rgb, fixed)
            result.putpixel((x, y), (*color, 255))
            groups.setdefault(color, []).append((x, y))
        ordered = sorted(groups.items(), key=lambda item: -len(item[1]))
        rows = (len(ordered) + width - 1) // width
        template = Image.new('RGBA', (width, height + 2 + rows))
        swatches = []
        for i, (color, _) in enumerate(ordered):
            point = (i % width, height + 2 + i // width)
            template.putpixel(point, (*color, 255))
            swatches.append(point)
        return Artwork(result, template, ordered, swatches)

    if need_tune:
        tuned = Image.new('RGBA', rgba.size)
        for x, y in opaque:
            tuned.putpixel((x, y), (*_tune(color_at(x, y), brightness, contrast, saturation, hue), 255))
    else:
        tuned = rgba
    visible = [tuned.getpixel((x, y))[:3] for x, y in opaque]
    strip = Image.new('RGB', (len(visible), 1))
    strip.putdata(visible)
    pal = strip.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    quantized = tuned.convert('RGB').quantize(palette=pal,
        dither=Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE).convert('RGB')
    groups = {}
    for x, y in opaque:
        rgb = quantized.getpixel((x, y))
        result.putpixel((x, y), (*rgb, 255))
        groups.setdefault(rgb, []).append((x, y))
    ordered = sorted(groups.items(), key=lambda item: -len(item[1]))
    rows = (len(ordered) + width - 1) // width
    template = Image.new('RGBA', (width, height + 2 + rows))
    swatches = []
    for i, (color, _) in enumerate(ordered):
        point = (i % width, height + 2 + i // width)
        template.putpixel(point, (*color, 255))
        swatches.append(point)
    return Artwork(result, template, ordered, swatches)


@dataclass(frozen=True)
class Calibration:
    first: tuple
    last: tuple
    size: tuple

    def validate(self):
        sx = (self.last[0]-self.first[0])/(self.size[0]-1)
        sy = (self.last[1]-self.first[1])/(self.size[1]-1)
        if min(sx, sy) < 2 or abs(sx-sy) > max(.25, max(sx, sy)*.025):
            raise ValueError(tr('Show the whole image (incl. the empty pixel on the bottom-right) at about 3200% or another integer zoom, then specify the top-left and bottom-right pixel centers again.'))
        return sx, sy

    def point(self, x, y):
        sx, sy = self.validate()
        return round(self.first[0]+x*sx), round(self.first[1]+y*sy)
