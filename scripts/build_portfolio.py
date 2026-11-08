#!/usr/bin/env python3
"""Build the static portfolio homepage from its editable HTML partials."""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "index.template.html"
OUTPUT = ROOT / "index.html"
MARKER = "<!-- PORTFOLIO_PARTIALS -->"
SECTIONS = (
    "background", "navigation", "hero", "about", "credentials", "experience",
    "projects", "technical-skills", "evidence", "training", "future",
    "contact", "footer", "image-viewer",
)

class PageValidator(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.anchors = []
        self.local_assets = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        identifier = data.get("id")
        if identifier:
            if identifier in self.ids:
                raise ValueError(f"Duplicate HTML id: {identifier}")
            self.ids.add(identifier)
        for attr in ("href", "src"):
            value = data.get(attr, "") or ""
            if value.startswith("#") and len(value) > 1:
                self.anchors.append(value[1:])
            elif value and not value.startswith((
                "#", "/", "http:", "https:", "data:", "mailto:", "tel:", "javascript:"
            )) and not value.startswith("//"):
                self.local_assets.append(value.split("#")[0].split("?")[0])

def assemble() -> str:
    template = TEMPLATE.read_text(encoding="utf-8")
    if template.count(MARKER) != 1:
        raise ValueError("The HTML template must contain exactly one partials marker")
    content = []
    for name in SECTIONS:
        path = ROOT / "partials" / f"{name}.html"
        section = path.read_text(encoding="utf-8").strip()
        if re.search(r"</?\s*(html|head|body)\b", section, flags=re.IGNORECASE):
            raise ValueError(f"{path}: sections cannot contain html/head/body tags")
        content.append(section)
    result = template.replace(MARKER, "\n\n".join(content)) + "\n"
    if len(re.findall(r"<body\b", result, flags=re.IGNORECASE)) != 1:
        raise ValueError("Generated HTML must have one body")
    parser = PageValidator()
    parser.feed(result)
    parser.close()
    missing_anchors = sorted(set(parser.anchors) - parser.ids)
    if missing_anchors:
        raise ValueError("Broken in-page anchors: " + ", ".join(missing_anchors))
    missing_assets = sorted({
        asset for asset in parser.local_assets if not (ROOT / asset).is_file()
    })
    if missing_assets:
        raise ValueError("Missing local assets: " + ", ".join(missing_assets))
    return result

def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--check", action="store_true", help="Fail if index.html is out of date")
    args = cli.parse_args()
    try:
        expected = assemble()
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if args.check:
            if current != expected:
                print("index.html is outdated; run python3 scripts/build_portfolio.py", file=sys.stderr)
                return 1
            print("index.html is current and validated")
        elif current != expected:
            OUTPUT.write_text(expected, encoding="utf-8")
            print("Regenerated index.html from HTML partials")
        else:
            print("index.html already up to date")
        return 0
    except (ValueError, OSError) as exc:
        print(f"Portfolio build failed: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
