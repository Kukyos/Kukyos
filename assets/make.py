# Regenerates the README's art. Edit the copy below, then: python assets/make.py
# Everything is transparent so it floats on GitHub's own background, dark or light.
# Lettering is baked to paths (GitHub blocks fonts in <img> SVGs).
# ponytail: font paths are Windows defaults; point them elsewhere if you run this off Windows.
import base64, io, math, os
from pathlib import Path
import numpy as np
from scipy import ndimage
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from PIL import Image

NAME = "A M Armaan"
NARRATION = "i build the thing before i decide what it's called."
SECTIONS = ["built", "simulated", "stats"]
# (card file, title, language, blurb)
PROJECTS = [
    ("vvater", "VVater", "TypeScript", "cut the ocean open in 3D. ocean model fields and argo floats in one browser scene."),
    ("satelight", "Satelight", "Python", "ocean temperature down to 1,000 m, rebuilt from satellite surface data alone. SIH 2026."),
    ("angeleyes", "Angel's Eye", "Python", "CCTV that works out what people are doing, then says who, when and why."),
    ("cuprum", "Cuprum", "TypeScript", "hold a gadget up to the camera, it guesses the copper inside, then microbes eat it."),
    ("nullticket", "NullTicket", "TypeScript", "helpdesk that swallows tickets from chat, email, GLPI and Solman, and routes them with LLaMA."),
    ("accessnull", "AccessNull", "TypeScript", "browse the web with your forehead. built for people who can't use their hands."),
    ("3bodyagents", "3bodyagents", "TypeScript", "a swarm of AI agents that go off and do research. groq + llama 4."),
    ("polymath", "Polymath OS", "HTML", "your routine as an RPG leveling system, plus desktop nags when you slack."),
    ("linkedauto", "LinkedAuto", "Python", "watches your repos and drafts the linkedin post the moment something ships."),
    ("visionully", "VisioNULLY", "TypeScript", "fall detection where the video never leaves the browser."),
    ("nulldraw", "NullDraw", "TypeScript", "one shared 1920 x 1080 pixel canvas, everyone drawing at once."),
    ("simathon", "Simathon", "TypeScript", "a hackathon run end to end: entry portal, project gallery, judging system."),
    ("lancist", "Lancist", "Python", "outreach bot for oryn. finds local businesses, audits their sites, writes the cold email."),
    ("blackstone", "Blackstone", "TypeScript", "e-catalogue and digital form filler, built for Blackstone Elevators."),
    ("starsystem", "Star Systems", "Python", "euler vs leapfrog, a generated system under the real sky, and the real one with measured relativity."),
    ("singularity", "SingularityEngine", "Python", "GPU black hole and N-body sim with a symplectic integrator. taichi."),
    ("groundstate", "GroundStateFinder", "Python", "qubit hamiltonians for H2 and NH3. qiskit nature + pyscf."),
    ("fishschooling", "fishschooling-sim", "C", "fish schooling on the GPU. CUDA + OpenGL, emergent by design."),
    ("nozheimers", "Nozheimers", "Python", "three early-onset alzheimer's genes, compared across species."),
]

HERE = Path(__file__).parent
WIN = "C:/Windows/Fonts/"
BLACKLETTER = TTFont(WIN + "OLDENGL.TTF")
SERIF = TTFont(WIN + "GARA.TTF")
ITALIC = TTFont(WIN + "GARAIT.TTF")
MONO = TTFont(os.environ["LOCALAPPDATA"] + "/Microsoft/Windows/Fonts/JetBrainsMono-Regular.ttf")
NO_MOTION = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
# mid greys read on both GitHub themes; the light block darkens text when the viewer is on light mode
TONE = (".t1{fill:#c9c9c9}.t2{fill:#8b8b8b}.ln{stroke:#4a4a4a}"
        ".c0{stop-color:#fdfdfd}.c1{stop-color:#a9a9a9}.c2{stop-color:#3d3d3d}.c3{stop-color:#8e8e8e}.c4{stop-color:#e9e9e9}"
        "@media (prefers-color-scheme:light){.t1{fill:#1f1f1f}.t2{fill:#5c5c5c}.ln{stroke:#b5b5b5}"
        ".c0{stop-color:#8a8a8a}.c1{stop-color:#3a3a3a}.c2{stop-color:#050505}.c3{stop-color:#4a4a4a}.c4{stop-color:#9a9a9a}}")
CHROME = ('<linearGradient id="chrome" x1="0" y1="0" x2="0" y2="1">'
          '<stop class="c0" offset="0"/><stop class="c1" offset=".42"/><stop class="c2" offset=".5"/>'
          '<stop class="c3" offset=".62"/><stop class="c4" offset="1"/></linearGradient>'
          '<linearGradient id="glint" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
          '<stop offset=".5" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')


def fmt(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def width(font, text, size, track=0):
    cmap, hmtx = font.getBestCmap(), font["hmtx"]
    return sum(hmtx[cmap[ord(c)]][0] for c in text) * size / font["head"].unitsPerEm + track * (len(text) - 1)


def text_path(font, text, size, x, y, anchor="start", track=0):
    """SVG path data for `text` with its baseline at y."""
    gs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
    s = size / font["head"].unitsPerEm
    x -= {"start": 0, "middle": width(font, text, size, track) / 2, "end": width(font, text, size, track)}[anchor]
    pen = SVGPathPen(gs, ntos=fmt)
    for c in text:
        g = cmap[ord(c)]
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
        x += hmtx[g][0] * s + track
    return pen.getCommands()


def wrap(font, text, size, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and width(font, trial, size) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


def svg(w, h, style, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f"<style>{style}{NO_MOTION}</style>{body}</svg>\n")


def data_uri(im, fmt_="WEBP", **kw):
    buf = io.BytesIO()
    im.save(buf, fmt_, **kw)
    return f"data:image/{fmt_.lower()};base64,{base64.b64encode(buf.getvalue()).decode()}"


def glint(mask_id, x, y, w, h, period=7, delay=0):
    """A light band that sweeps across whatever `mask_id` covers, then rests."""
    return (f'<g mask="url(#{mask_id})"><g transform="skewX(-22)">'
            f'<rect class="glint" style="animation-delay:{delay}s" x="{x - 160}" y="{y}" width="110" height="{h}" fill="url(#glint)"/>'
            f"</g></g>"), (f".glint{{animation:glint {period}s ease-in-out infinite}}"
                           f"@keyframes glint{{0%{{transform:translateX(0)}}35%,100%{{transform:translateX({w + 320}px)}}}}")


# chrome thorns: black knocked out of tribal.png, split into its separate shapes
_src = np.asarray(Image.open(HERE / "tribal.png").convert("RGB")).astype(float) / 255
_alpha = np.clip((_src.mean(2) - .06) * 3.2, 0, 1)
_rgb = np.clip(_src / np.maximum(_alpha[..., None], 1e-3), 0, 1)
_labels, _ = ndimage.label(_src.mean(2) > .12)


def thorn(label):
    """One chrome shape as a cropped RGBA image (labels come from scipy, stable for this source)."""
    keep = ndimage.binary_dilation(_labels == label, iterations=4)
    ys, xs = np.where(keep)
    sl = slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1)
    rgba = np.dstack([_rgb[sl], (_alpha * keep)[sl]])
    return Image.fromarray((rgba * 255).astype("uint8"), "RGBA")


def placed(im, x, y, h, flip=False, extra=""):
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    w = h * im.width / im.height
    small = im.resize((round(w * 2), round(h * 2)), Image.LANCZOS)  # 2x for retina
    return f'<image href="{data_uri(small, quality=80)}" x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" {extra}/>', w


def header():
    cx, cy, r = 200, 172, 132
    disc = Image.open(HERE / "pfp.png").convert("RGB").resize((340, 340), Image.LANCZOS)

    thorns = "".join(placed(thorn(n), x, y, h, flip)[0] for n, x, y, h, flip in [
        (4, 796, 2, 72, False),   # perched on the name panel's top right
        (34, 372, 236, 96, True),  # hanging off the narration strip's left end
    ])
    name_size = 92 * 380 / width(BLACKLETTER, NAME, 92)  # fit the panel
    name = text_path(BLACKLETTER, NAME, name_size, 652, 152, "middle")
    shine, shine_css = glint("nm", 440, 70, 440, 110, period=8, delay=1.2)
    narration = text_path(ITALIC, NARRATION, 20, 648, 282, "middle")

    style = (TONE + shine_css +
             ".spin{transform-box:fill-box;transform-origin:center;animation:spin 16s linear infinite}"
             "@keyframes spin{to{transform:rotate(360deg)}}"
             ".float{animation:float 6s ease-in-out infinite}@keyframes float{50%{transform:translateY(-5px)}}"
             ".bleed{animation:bleed 2.6s ease-out .2s both}"
             "@keyframes bleed{from{opacity:0;filter:blur(8px)}to{opacity:1;filter:blur(0)}}")
    B = "438,40 884,40 884,214 418,214"
    C = "414,246 884,246 884,304 406,304"
    body = f"""
<defs>{CHROME}
  <clipPath id="disc"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>
  <mask id="nm"><path fill="#fff" d="{name}"/></mask>
</defs>
<g class="float">{thorns}</g>
<g clip-path="url(#disc)"><image class="spin" href="{data_uri(disc, 'JPEG', quality=82)}" x="{cx - r - 2}" y="{cy - r - 2}" width="{2 * r + 4}" height="{2 * r + 4}"/></g>
<g fill="none" class="ln" stroke-width="1.2"><polygon points="{B}"/><polygon points="{C}"/></g>
<g class="bleed"><path fill="url(#chrome)" d="{name}"/>{shine}</g>
<path class="t2" d="{narration}"/>
"""
    return svg(900, 340, style, body)


def divider():
    im, w = placed(thorn(45), 0, 0, 90, extra='id="th"')
    # piece 45 is clipped along the source's bottom edge; fade that edge out
    shine, css = glint("tm", 0, 0, w, 90, period=9)
    body = (f'<defs>{CHROME}<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset=".7" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
            f'<mask id="edge"><rect width="{fmt(w)}" height="90" fill="url(#fade)"/></mask>'
            f'<mask id="tm"><use href="#th"/></mask></defs>'
            f'<g mask="url(#edge)">{im}{shine}</g>')
    return svg(round(w), 90, css, body)


def section(label):
    tw = width(BLACKLETTER, label, 46)
    left, lw = placed(thorn(4), 0, 4, 52, flip=True)
    right, _ = placed(thorn(4), lw + tw + 36, 4, 52)
    body = (f"<defs>{CHROME}</defs>{left}{right}"
            f'<path fill="url(#chrome)" d="{text_path(BLACKLETTER, label, 46, lw + 18, 44)}"/>')
    return svg(round(2 * lw + tw + 36), 60, TONE, body)


def card(i, title, lang, blurb):
    W, H, cut = 420, 168, 12
    frame = f"{cut},1 {W - cut},1 {W - 1},{cut} {W - 1},{H - cut} {W - cut},{H - 1} {cut},{H - 1} 1,{H - cut} 1,{cut}"
    t = text_path(SERIF, title.upper(), 22, 26, 46, track=3)
    lines = wrap(ITALIC, blurb, 19, W - 52)[:3]
    desc = "".join(text_path(ITALIC, line, 19, 26, 80 + n * 23) for n, line in enumerate(lines))
    shine, css = glint(f"c{i}", 26, 20, width(SERIF, title.upper(), 22, 3), 32, period=11, delay=i * .9)
    ornament = (f'<path class="sp" d="M{W - 30} 34l5-9 5 9-5 9z"/>'
                f'<path class="ln" stroke-width="1" d="M26 58H66"/>')
    m = 16  # room for the glow
    body = (f'<defs>{CHROME}<mask id="c{i}"><path fill="#fff" d="{t}"/></mask>'
            f'<filter id="soft" x="-20%" y="-30%" width="140%" height="160%"><feGaussianBlur stdDeviation="7"/></filter></defs>'
            f'<polygon class="glow" style="animation-delay:{-i * 1.3}s" points="{frame}" filter="url(#soft)" transform="translate({m} {m})"/>'
            f'<g transform="translate({m} {m})">'
            f'<polygon class="ln" fill="none" stroke-width="1.2" points="{frame}"/>{ornament}'
            f'<path fill="url(#chrome)" d="{t}"/>{shine}<path class="t1" d="{desc}"/>'
            f'<path class="t2" d="{text_path(MONO, lang.lower(), 11, 26, H - 18)}"/></g>')
    glow = (".glow{fill:none;stroke:#fff;stroke-width:5;opacity:.16;animation:glow 7s ease-in-out infinite}@keyframes glow{50%{opacity:.3}}"
            "@media (prefers-color-scheme:light){.glow{stroke:#000;opacity:.08}}")
    return svg(W + 2 * m, H + 2 * m, TONE + css + glow + ".sp{fill:#8b8b8b}", body)


if __name__ == "__main__":
    (HERE / "header.svg").write_text(header(), encoding="utf-8")
    (HERE / "divider.svg").write_text(divider(), encoding="utf-8")
    for s in SECTIONS:
        (HERE / f"h-{s}.svg").write_text(section(s), encoding="utf-8")
    (HERE / "cards").mkdir(exist_ok=True)
    for i, (slug, *rest) in enumerate(PROJECTS):
        (HERE / "cards" / f"{slug}.svg").write_text(card(i, *rest), encoding="utf-8")
    print("ok")
