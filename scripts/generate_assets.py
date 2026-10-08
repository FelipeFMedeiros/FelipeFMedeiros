"""Generate the profile GIF and local SVG badges: python scripts/generate_assets.py.

Requires Pillow. No network access or GitHub credentials are needed.
Use --font /path/to/monospace.ttf to choose a different local font.
"""

from __future__ import annotations

import argparse
from html import escape
from copy import deepcopy
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SIZE = (1000, 240)
SCALE = 2
NAME = "Felipe Medeiros"
SUBTITLE = "Full-Stack Developer · Web & Mobile"
BG = "#0D1117"
SURFACE = "#161B22"
BORDER = "#30363D"
BLUE = "#58A6FF"
TEXT = "#E6EDF3"
MUTED = "#8B949E"
BADGES = {'react': ('React', 'react', None),
 'typescript': ('TypeScript', 'typescript', None),
 'javascript': ('JavaScript', 'javascript', None),
 'tailwind-css': ('Tailwind CSS', 'tailwindcss', None),
 'vite': ('Vite', 'vitejs', None),
 'tanstack-query': ('TanStack Query', 'reactquery', '#FF4154'),
 'radix-ui': ('Radix UI', 'radixui', '#E6EDF3'),
 'shadcn-ui': ('shadcn/ui', 'shadcnui', '#E6EDF3'),
 'react-native': ('React Native', 'react', None),
 'expo': ('Expo', 'expo', '#E6EDF3'),
 'nodejs': ('Node.js', 'nodejs', None),
 'express': ('Express', 'express', '#E6EDF3'),
 'bun': ('Bun', 'bun', None),
 'elysia': ('Elysia.js', 'elysia', None),
 'csharp': ('C#', 'csharp', None),
 'dotnet': ('.NET', 'dotnetcore', None),
 'postgresql': ('PostgreSQL', 'postgresql', None),
 'sql-server': ('SQL Server', 'microsoftsqlserver', None),
 'prisma': ('Prisma', 'prisma', '#E6EDF3'),
 'drizzle': ('Drizzle ORM', 'drizzle', '#C5F74F'),
 'redis': ('Redis', 'redis', None),
 'docker': ('Docker', 'docker', None),
 'github-actions': ('GitHub Actions', 'githubactions', None),
 'linux': ('Linux', 'linux', None),
 'aws': ('AWS EC2', 'amazonwebservices', None),
 'caddy': ('Caddy', 'caddy', '#1F88C0'),
 'git': ('Git', 'git', None),
 'figma': ('Figma', 'figma', None),
 'swagger': ('Swagger', 'swagger', None),
 'zod': ('Zod', 'zod', '#3E67B1'),
 'python': ('Python', 'python', None),
 'fastapi': ('FastAPI', 'fastapi', None),
 'c': ('C', 'c', None),
 'html5': ('HTML5', 'html5', None),
 'css3': ('CSS3', 'css3', None),
 'mongodb': ('MongoDB', 'mongodb', None),
 'mysql': ('MySQL', 'mysql', None)}


def find_font(explicit: str | None) -> str:
    candidates = [explicit] if explicit else [
        "C:/Windows/Fonts/consola.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
        "/System/Library/Fonts/Menlo.ttc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise SystemExit("No monospace font found. Supply --font /path/to/font.ttf.")


def render_frame(font_path: str, count: int, cursor: bool) -> Image.Image:
    im = Image.new("RGB", (SIZE[0] * SCALE, SIZE[1] * SCALE), BG)
    draw = ImageDraw.Draw(im)

    def box(coords: tuple[int, int, int, int]) -> tuple[int, ...]:
        return tuple(value * SCALE for value in coords)

    def write(x: float, y: float, text: str, size: int, color: str) -> None:
        draw.text((x * SCALE, y * SCALE), text,
                  font=ImageFont.truetype(font_path, size * SCALE), fill=color, anchor="lt")

    draw.rounded_rectangle(box((1, 1, 998, 238)), radius=12 * SCALE, outline=BORDER, width=SCALE)
    draw.line(box((2, 43, 997, 43)), fill=BORDER, width=SCALE)
    for x in (25, 43, 61):
        draw.ellipse(box((x, 18, x + 7, 25)), fill=MUTED)
    write(86, 15, "felipe@github: ~", 15, MUTED)
    write(48, 78, ">", 64, MUTED)
    visible = NAME[:count]
    write(104, 78, visible, 64, BLUE)
    if cursor:
        font = ImageFont.truetype(font_path, 64 * SCALE)
        x = 104 + draw.textlength(visible, font=font) / SCALE + 6
        draw.rectangle(box((round(x), 77, round(x) + 3, 137)), fill=BLUE)
    write(104, 174, SUBTITLE, 28, TEXT)
    return im.resize(SIZE, Image.Resampling.LANCZOS)


def generate_gif(font_path: str) -> None:
    # One indexed palette across the entire loop avoids color shifts.
    reference = render_frame(font_path, len(NAME), True)
    palette = reference.quantize(colors=96, method=Image.Quantize.MEDIANCUT)
    states: list[tuple[int, bool, int]] = [(0, True, 400)]
    states += [(count, True, 100) for count in range(1, len(NAME) + 1)]
    states += [(len(NAME), blink % 2 == 1, 500) for blink in range(8)]
    states += [(count, True, 50) for count in range(len(NAME) - 1, -1, -1)]
    states += [(0, False, 500)]
    frames = [render_frame(font_path, count, cursor).quantize(
        palette=palette, dither=Image.Dither.NONE) for count, cursor, _ in states]
    destination = ROOT / "assets/profile-header.gif"
    destination.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(destination, save_all=True, append_images=frames[1:],
                   duration=[duration for _, _, duration in states], loop=0,
                   optimize=True, disposal=1)
    print(f"GIF: {SIZE[0]} x {SIZE[1]}, {sum(s[2] for s in states)} ms, "
          f"{destination.stat().st_size:,} bytes")
    if destination.stat().st_size > 1_000_000:
        raise SystemExit("GIF exceeds the 1 MB size target.")


def icon_svg(name: str, color: str | None = None) -> str:
    namespace = "http://www.w3.org/2000/svg"
    ET.register_namespace("", namespace)
    icon = deepcopy(ET.parse(ROOT / "assets/icons" / f"{name}.svg").getroot())
    icon.set("x", "10")
    icon.set("y", "8")
    icon.set("width", "20")
    icon.set("height", "20")
    icon.set("aria-hidden", "true")
    for node in icon.iter():
        if color:
            for attribute in ("fill", "stroke"):
                if node.get(attribute) and node.get(attribute) != "none" and not node.get(attribute).startswith("url("):
                    node.set(attribute, color)
        elif node.get("fill", "").lower() in ("#000", "#000000", "black"):
            node.set("fill", TEXT)
    if color:
        icon.set("fill", color)
    return ET.tostring(icon, encoding="unicode")


def write_badge(directory: Path, slug: str, label: str, icon: str) -> None:
    width = 50 + round(len(label) * 8.5)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="36" viewBox="0 0 {width} 36" role="img" aria-label="{escape(label, quote=True)}">
  <title>{escape(label)}</title>
  <rect x="0.5" y="0.5" width="{width - 1}" height="35" rx="6" fill="{SURFACE}" stroke="{BORDER}"/>
  {icon}
  <text x="38" y="23" fill="{TEXT}" font-family="DejaVu Sans Mono,Consolas,monospace" font-size="14">{escape(label)}</text>
</svg>
'''
    (directory / f"{slug}.svg").write_text(svg, encoding="utf-8")


def generate_badges() -> None:
    directory = ROOT / "assets/badges"
    directory.mkdir(parents=True, exist_ok=True)
    for slug, (label, name, color) in BADGES.items():
        write_badge(directory, slug, label, icon_svg(name, color))
    contacts = ROOT / "assets/contacts"
    contacts.mkdir(parents=True, exist_ok=True)
    portfolio = '<svg x="10" y="8" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#58A6FF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="7" width="18" height="14" rx="2"/><path d="M8 7V3h8v4M3 12h18M10 12v3h4v-3"/></svg>'
    email = '<svg x="10" y="8" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#58A6FF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 6 10 7 10-7"/></svg>'
    write_badge(contacts, "portfolio", "Portfolio", portfolio)
    write_badge(contacts, "email", "Email", email)
    write_badge(contacts, "linkedin", "LinkedIn", icon_svg("linkedin"))
    instagram = '<svg x="10" y="8" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#E1306C" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="0.9" fill="#E1306C" stroke="none"/></svg>'
    write_badge(contacts, "instagram", "Instagram", instagram)
    print(f"Badges: {len(BADGES)} technology logos, 4 contact buttons")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", help="Path to a local monospace TTF or TTC font")
    parser.add_argument("--badges-only", action="store_true", help="Regenerate badges and contact buttons without changing the GIF")
    args = parser.parse_args()
    if not args.badges_only:
        generate_gif(find_font(args.font))
    generate_badges()


if __name__ == "__main__":
    main()
