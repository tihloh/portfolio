#!/usr/bin/env python3
"""Assemble the general portfolio and optional specialized pages from HTML partials."""
from __future__ import annotations

import argparse
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "index.template.html"
OUTPUT = ROOT / "index.html"
MARKER = "<!-- PORTFOLIO_PARTIALS -->"
SECTIONS = (
    "background", "navigation", "hero", "about", "credentials", "experience",
    "projects", "technical-skills", "evidence", "training", "future",
    "contact", "footer", "image-viewer",
)
SPECIALIZED_TEMPLATE = ROOT / "pages" / "page.template.html"
NAME_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")


class PageValidator(HTMLParser):
    """Original homepage validator, retained for backward compatibility."""

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
    """Preserve the original homepage output and behavior."""
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


class SpecializedPageValidator(PageValidator):
    """Validate anchors and relative URLs from a generated subdirectory."""

    def __init__(self, page: str, all_pages: set[str]):
        super().__init__()
        self.page = page
        self.all_pages = all_pages

    def validate(self, source: str) -> None:
        self.feed(source)
        self.close()
        missing_anchors = sorted(set(self.anchors) - self.ids)
        if missing_anchors:
            raise ValueError(f"{self.page}: broken in-page anchors: {', '.join(missing_anchors)}")
        missing = []
        for raw in self.local_assets:
            path = unquote(urlsplit(raw).path)
            destination = (ROOT / self.page / path).resolve()
            if not destination.is_relative_to(ROOT.resolve()):
                raise ValueError(f"{self.page}: local URL escapes repository: {raw}")
            rel = destination.relative_to(ROOT.resolve())
            if destination.is_file():
                continue
            if destination.is_dir() and (rel == Path(".") or rel.parts[0] in self.all_pages):
                continue
            if rel.parts and rel.parts[0] in self.all_pages and len(rel.parts) == 1:
                continue
            missing.append(raw)
        if missing:
            raise ValueError(f"{self.page}: missing relative files or pages: {', '.join(sorted(set(missing)))}")


def page_names() -> list[str]:
    directory = ROOT / "pages"
    if not directory.is_dir():
        return []
    names = sorted(p.name for p in directory.iterdir() if p.is_dir())
    for name in names:
        if not NAME_PATTERN.fullmatch(name):
            raise ValueError(f"Invalid page directory name: {name}")
        if not (directory / name / "page.json").is_file():
            raise ValueError(f"{name}: page.json is missing")
    return names


def section_file(page: str, identifier: str) -> Path:
    if not isinstance(identifier, str):
        raise ValueError(f"{page}: section identifiers must be strings")
    parts = identifier.split("/")
    if len(parts) == 1 and NAME_PATTERN.fullmatch(parts[0]):
        path = ROOT / "pages" / page / "partials" / f"{parts[0]}.html"
    elif len(parts) == 2 and parts[0] in ("shared", "partials") and NAME_PATTERN.fullmatch(parts[1]):
        path = ROOT / parts[0] / f"{parts[1]}.html"
    else:
        raise ValueError(f"{page}: invalid section identifier: {identifier}")
    if not path.is_file():
        raise ValueError(f"{page}: missing section: {path.relative_to(ROOT)}")
    return path


def assemble_specialized(page: str, names: set[str]) -> str:
    config_path = ROOT / "pages" / page / "page.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    for key in ("title", "description"):
        if not isinstance(config.get(key), str) or not config[key].strip():
            raise ValueError(f"{page}: {key} must be non-empty text")
    sections = config.get("sections")
    if not isinstance(sections, list) or len(sections) < 3 or not all(isinstance(item, str) for item in sections) or len(sections) != len(set(sections)):
        raise ValueError(f"{page}: provide an ordered list of unique sections")
    template = SPECIALIZED_TEMPLATE.read_text(encoding="utf-8")
    placeholders = {"{{PAGE_TITLE}}", "{{PAGE_DESCRIPTION}}", "{{PAGE_CANONICAL}}", MARKER}
    if any(template.count(token) != 1 for token in placeholders):
        raise ValueError("Specialized page template must contain each placeholder exactly once")
    fragments = []
    for identifier in sections:
        section_path = section_file(page, identifier)
        content = section_path.read_text(encoding="utf-8").strip()
        if re.search(r"</?\s*(html|head|body)\b", content, flags=re.IGNORECASE):
            raise ValueError(f"{page}: section cannot contain document-level tags: {identifier}")
        fragments.append(content)
    output = template.replace("{{PAGE_TITLE}}", html.escape(config["title"], quote=True))
    output = output.replace("{{PAGE_DESCRIPTION}}", html.escape(config["description"], quote=True))
    output = output.replace("{{PAGE_CANONICAL}}", "https://cbustamante.portalx.win/" + page + "/")
    output = output.replace(MARKER, "\n\n".join(fragments)) + "\n"
    if len(re.findall(r"<body\b", output, flags=re.IGNORECASE)) != 1:
        raise ValueError(f"{page}: generated HTML must have one body")
    SpecializedPageValidator(page, names).validate(output)
    return output


def run_build(output: Path, expected: str, check: bool) -> bool:
    current = output.read_text(encoding="utf-8") if output.exists() else ""
    if check:
        if current != expected:
            print(f"{output.relative_to(ROOT)} is outdated; run python3 scripts/build_portfolio.py --all", file=sys.stderr)
            return False
        print(f"{output.relative_to(ROOT)} is current and validated")
    elif current != expected:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(expected, encoding="utf-8")
        print(f"Regenerated {output.relative_to(ROOT)}")
    else:
        print(f"{output.relative_to(ROOT)} already up to date")
    return True


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--check", action="store_true", help="Fail if generated pages are out of date")
    target = cli.add_mutually_exclusive_group()
    target.add_argument("--page", help="Build 'general' or a specialized page slug")
    target.add_argument("--all", action="store_true", help="Build the homepage and all specialized pages")
    args = cli.parse_args()
    try:
        names = page_names()
        if args.page and args.page != "general" and args.page not in names:
            raise ValueError(f"Unknown page: {args.page}")
        pages = (["general", *names] if args.all else [args.page or "general"])
        good = True
        for page in pages:
            expected = assemble() if page == "general" else assemble_specialized(page, set(names))
            output = OUTPUT if page == "general" else ROOT / page / "index.html"
            if not run_build(output, expected, args.check):
                good = False
        return 0 if good else 1
    except (ValueError, OSError) as exc:
        print(f"Portfolio build failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
