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


def prepare(source, width=32, height=32, colors=16, dither=False):
    if not (2 <= width <= 256 and 2 <= height <= 256 and 2 <= colors <= 64):
        raise ValueError(tr('Width/height must be 2-256 and colors 2-64.'))
    with Image.open(source) as opened:
        original = ImageOps.exif_transpose(opened).convert('RGBA')
    fitted = ImageOps.contain(original, (width, height), Image.Resampling.LANCZOS)
    rgba = Image.new('RGBA', (width, height))
    rgba.paste(fitted, ((width-fitted.width)//2, (height-fitted.height)//2))
    # Exclude transparent pixels from quantization to preserve the color budget.
    visible = [p[:3] for p in (rgba.get_flattened_data() if hasattr(rgba, 'get_flattened_data') else rgba.getdata()) if p[3] >= 128]
    if not visible:
        raise ValueError(tr('No opaque pixel to draw.'))
    strip = Image.new('RGB', (len(visible), 1))
    strip.putdata(visible)
    palette = strip.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    quantized = rgba.convert('RGB').quantize(palette=palette,
        dither=Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE).convert('RGB')
    result = Image.new('RGBA', rgba.size)
    groups = {}
    for y in range(height):
        for x in range(width):
            if rgba.getpixel((x, y))[3] >= 128:
                color = quantized.getpixel((x, y))
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
