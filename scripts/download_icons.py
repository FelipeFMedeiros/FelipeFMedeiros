"""Restore the vendored SVGs from the pinned URLs in assets/icons/sources.json.

Optional maintenance command; requires an internet connection, no extra packages.
"""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def download(item: tuple[str, str]) -> str:
    name, url = item
    request = Request(url, headers={"User-Agent": "FelipeFMedeiros-profile-assets"})
    with urlopen(request, timeout=30) as response:
        data = response.read()
    if ET.fromstring(data).tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError(f"Invalid SVG returned for {name}")
    (ROOT / "assets/icons" / f"{name}.svg").write_bytes(data)
    return name


def main() -> None:
    manifest = json.loads((ROOT / "assets/icons/sources.json").read_text(encoding="utf-8"))
    with ThreadPoolExecutor(max_workers=6) as executor:
        for name in executor.map(download, manifest["icons"].items()):
            print(name)


if __name__ == "__main__":
    main()
