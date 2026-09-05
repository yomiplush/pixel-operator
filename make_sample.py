"""Generate an original, small deterministic test sprite; no downloaded assets."""
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parent
pattern = [
'................',
'.....AAAAAA.....',
'...AAAAAAAAAA...',
'..AABBAAAABBAA..',
'..AABBAAAABBAA..',
'..AAAAAAAAAAAA..',
'..AACAAAAAACAA..',
'...AACCCCCCAA...',
'....AAAAAAA.....',
'.....DDDDDD.....',
'...DDDDDDDDDD...',
'..DDDDDDDDDDDD..',
'..DD.DDDDDD.DD..',
'.....DD..DD.....',
'....CCC..CCC....',
'................']
colors = {'.':(0,0,0,0), 'A':(119,218,173,255), 'B':(32,44,64,255),
          'C':(255,200,102,255), 'D':(102,143,218,255)}
image = Image.new('RGBA', (16,16))
image.putdata([colors[p] for row in pattern for p in row])
image.save(ROOT/'sample.png')
