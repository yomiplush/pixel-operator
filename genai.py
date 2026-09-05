"""Optional AI image generation via Google Gemini (free tier only).
The API key is stored locally in ~/.config/pixel-operator/config.json (0600)
and never committed. Network errors surface as readable messages."""
import base64
import json
import os
from pathlib import Path
from urllib import request, error

CONFIG_DIR = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home()/'.config')))/'pixel-operator'
CONFIG = CONFIG_DIR/'config.json'

# Free-tier friendly defaults. Users on paid plans may edit the model name.
FREE_MODELS = ['gemini-2.5-flash-image', 'gemini-2.0-flash-preview-image-generation']
DEFAULT_MODEL = FREE_MODELS[0]
API = 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'


def _load():
    try:
        return json.loads(CONFIG.read_text())
    except Exception:
        return {}


def load_config():
    cfg = _load()
    return {
        'api_key': cfg.get('api_key', ''),
        'model': cfg.get('model', DEFAULT_MODEL),
    }


def save_config(api_key='', model=DEFAULT_MODEL):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps({'api_key': api_key, 'model': model}, indent=2))
    os.chmod(CONFIG, 0o600)


def generate(prompt, api_key=None, model=None):
    """Ask Gemini to return a PNG (base64) for `prompt`.
    Returns image bytes. Raises RuntimeError with a readable message."""
    cfg = load_config()
    api_key = api_key if api_key is not None else cfg['api_key']
    model = model or cfg['model']
    if not api_key:
        raise RuntimeError(
            'Gemini API key is not set. Get a free key at Google AI Studio '
            '(https://aistudio.google.com/apikey) and enter it in the settings.')
    body = {
        'contents': [{'parts': [{'text': prompt}]}],
        'generationConfig': {
            'responseModalities': ['IMAGE'],
            'responseMimeType': 'image/png',
        },
    }
    req = request.Request(
        API.format(model=model) + '?key=' + request.quote(api_key),
        data=json.dumps(body).encode(),
        headers={'Content-Type': 'application/json'})
    try:
        with request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
    except error.HTTPError as exc:
        detail = ''
        try:
            detail = json.loads(exc.read().decode()).get('error', {}).get('message', '')
        except Exception:
            pass
        raise RuntimeError(f'Gemini API error ({exc.code}): {detail}') from exc
    except error.URLError as exc:
        raise RuntimeError(f'Could not reach Gemini API: {exc.reason}') from exc

    try:
        parts = data['candidates'][0]['content']['parts']
        png = next(p['inlineData']['data'] for p in parts if 'inlineData' in p)
    except (KeyError, IndexError, StopIteration):
        msg = data.get('promptFeedback') or data
        raise RuntimeError(f'Gemini returned no image: {msg}')
    return base64.b64decode(png)
