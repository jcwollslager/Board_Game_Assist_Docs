#!/usr/bin/env python3
"""Convert the private BG Assist GitHub wiki into the public Pages site."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


MANIFEST_NAME = ".wiki-publish-manifest.json"
IMAGE_URL_PATTERN = re.compile(
    r"(?P<prefix><img\b[^>]*?\bsrc=[\"'])(?P<html_url>https?://[^\"']+)(?P<suffix>[\"'][^>]*>)"
    r"|(?P<md_prefix>!\[[^\]]*\]\()(?P<md_url>https?://[^)\s]+)(?P<md_suffix>\))",
    re.IGNORECASE,
)
MARKDOWN_LINK_PATTERN = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
WIKI_LINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")


@dataclass(frozen=True)
class Page:
    source: Path
    title: str
    output_name: str
    permalink: str


SPECIAL_PAGES = {
    "home": ("BG Assist", "index.md", "/"),
    "installing-bga": ("Installing BG Assist", "installing.md", "/installing/"),
    "start-up-guide": ("Start-up Guide", "getting-started.md", "/getting-started/"),
}


def normalized_name(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = value.replace("‐", "-").replace("‑", "-").replace("–", "-").replace("—", "-")
    value = value.strip().removesuffix(".md")
    return value


def slugify(value: str) -> str:
    value = normalized_name(value)
    value = unicodedata.normalize("NFKD", value)
    value = "".join(character for character in value if not unicodedata.combining(character))
    value = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return value or "page"


def human_title(value: str) -> str:
    return normalized_name(value).replace("-", " ").strip().title()


def discover_pages(wiki_dir: Path) -> list[Page]:
    pages: list[Page] = []
    for source in sorted(wiki_dir.glob("*.md"), key=lambda path: path.name.casefold()):
        if source.stem.startswith("_"):
            continue

        key = slugify(source.stem)
        title, output_name, permalink = SPECIAL_PAGES.get(
            key,
            (human_title(source.stem), f"{key}.md", f"/{key}/"),
        )
        pages.append(Page(source, title, output_name, permalink))

    if not any(page.output_name == "index.md" for page in pages):
        raise RuntimeError("The private wiki does not contain Home.md.")
    return pages


def page_aliases(page: Page) -> set[str]:
    source_name = normalized_name(page.source.stem)
    return {
        source_name.casefold(),
        source_name.replace(" ", "-").casefold(),
        page.title.casefold(),
        page.title.replace(" ", "-").casefold(),
        Path(page.output_name).stem.casefold(),
    }


def resolve_page_target(target: str, aliases: dict[str, Page]) -> tuple[Page, str] | None:
    target = target.strip().strip("<>")
    parsed = urllib.parse.urlparse(target)

    if parsed.scheme and parsed.netloc:
        if parsed.netloc.casefold() != "github.com":
            return None
        marker = "/jcwollslager/Board_Game_Assist/wiki/"
        if marker.casefold() not in parsed.path.casefold():
            return None
        target = parsed.path[parsed.path.casefold().index(marker.casefold()) + len(marker) :]
        fragment = parsed.fragment
    else:
        target, separator, fragment = target.partition("#")
        if not separator:
            fragment = ""

    target = urllib.parse.unquote(target).lstrip("./")
    key = normalized_name(target).replace(" ", "-").casefold()
    page = aliases.get(key) or aliases.get(key.replace("-", " "))
    if page is None:
        return None
    return page, fragment


def jekyll_link(page: Page, fragment: str = "") -> str:
    suffix = f"#{fragment}" if fragment else ""
    return "{{ '" + page.permalink + "' | relative_url }}" + suffix


def rewrite_page_links(text: str, aliases: dict[str, Page]) -> str:
    def replace_wiki_link(match: re.Match[str]) -> str:
        parts = [part.strip() for part in match.group(1).split("|", 1)]
        label = parts[0]
        target = parts[1] if len(parts) == 2 else parts[0]
        resolved = resolve_page_target(target, aliases)
        if resolved is None:
            return match.group(0)
        page, fragment = resolved
        return f"[{label}]({jekyll_link(page, fragment)})"

    def replace_markdown_link(match: re.Match[str]) -> str:
        label, destination = match.groups()
        destination = destination.strip()
        resolved = resolve_page_target(destination, aliases)
        if resolved is None:
            return match.group(0)
        page, fragment = resolved
        return f"[{label}]({jekyll_link(page, fragment)})"

    text = WIKI_LINK_PATTERN.sub(replace_wiki_link, text)
    return MARKDOWN_LINK_PATTERN.sub(replace_markdown_link, text)


def image_extension(url: str, content_type: str | None) -> str:
    extension = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if extension in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
        return extension

    if content_type:
        extension = mimetypes.guess_extension(content_type.split(";", 1)[0].strip()) or ""
        if extension == ".jpe":
            extension = ".jpg"
        if extension:
            return extension
    return ".png"


def download_image(url: str, token: str) -> tuple[bytes, str | None]:
    headers = {"User-Agent": "BGA-Wiki-Publisher/1.0"}

    def request(extra_headers: dict[str, str] | None = None):
        request_headers = dict(headers)
        if extra_headers:
            request_headers.update(extra_headers)
        request = urllib.request.Request(url, headers=request_headers)
        return urllib.request.urlopen(request, timeout=60)

    try:
        response = request()
    except urllib.error.HTTPError as error:
        host = (urllib.parse.urlparse(url).hostname or "").casefold()
        github_host = host == "github.com" or host.endswith(".github.com") or host.endswith(".githubusercontent.com")
        if error.code not in {401, 403, 404} or not token or not github_host:
            raise
        response = request({"Authorization": f"Bearer {token}"})

    with response:
        return response.read(), response.headers.get("Content-Type")


def localize_images(
    text: str,
    docs_dir: Path,
    token: str,
    used_images: set[str],
    known_images: dict[str, str],
) -> str:
    image_dir = docs_dir / "assets" / "images"
    image_dir.mkdir(parents=True, exist_ok=True)

    def replace_image(match: re.Match[str]) -> str:
        url = match.group("html_url") or match.group("md_url")
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
        relative_path = known_images.get(url, "")

        if relative_path:
            destination = docs_dir / relative_path
            if not destination.is_file():
                raise RuntimeError(
                    f"The mapped public image does not exist: {relative_path}"
                )
        else:
            existing_images = sorted(image_dir.glob(f"wiki-{digest}.*"))
            if existing_images:
                destination = existing_images[0]
                relative_path = destination.relative_to(docs_dir).as_posix()
            else:
                try:
                    image_bytes, content_type = download_image(url, token)
                except (OSError, urllib.error.URLError) as error:
                    print(
                        "::warning title=Wiki image was not published::"
                        f"GitHub would not allow this private attachment to be downloaded: {url} "
                        f"({error})"
                    )
                    return match.group(0)

                filename = f"wiki-{digest}{image_extension(url, content_type)}"
                relative_path = f"assets/images/{filename}"
                destination = docs_dir / relative_path
                if not destination.exists() or destination.read_bytes() != image_bytes:
                    destination.write_bytes(image_bytes)
        used_images.add(relative_path)

        public_url = "{{ '/" + relative_path.replace(os.sep, "/") + "' | relative_url }}"
        if match.group("html_url"):
            return f"{match.group('prefix')}{public_url}{match.group('suffix')}"
        return f"{match.group('md_prefix')}{public_url}{match.group('md_suffix')}"

    return IMAGE_URL_PATTERN.sub(replace_image, text)


def remove_existing_front_matter(text: str) -> str:
    if not text.startswith("---"):
        return text.lstrip("\ufeff")
    match = re.match(r"\A---\s*\n.*?\n---\s*\n", text, flags=re.DOTALL)
    return text[match.end() :] if match else text


def front_matter(page: Page) -> str:
    safe_title = page.title.replace('"', '\\"')
    return (
        "---\n"
        "layout: page\n"
        f'title: "{safe_title}"\n'
        f"permalink: {page.permalink}\n"
        "---\n\n"
    )


def update_header_pages(config_path: Path, pages: list[Page]) -> None:
    config = config_path.read_text(encoding="utf-8")
    ordered_names = ["index.md"]
    for preferred in ("installing.md", "getting-started.md"):
        if any(page.output_name == preferred for page in pages):
            ordered_names.append(preferred)
    ordered_names.extend(
        sorted(
            page.output_name
            for page in pages
            if page.output_name not in set(ordered_names)
        )
    )
    replacement = "header_pages:\n" + "".join(f"  - {name}\n" for name in ordered_names)
    updated, count = re.subn(
        r"header_pages:\s*\n(?:\s+-\s+.*\n)*",
        replacement,
        config,
        count=1,
    )
    if count == 0:
        updated = config.rstrip() + "\n\n" + replacement
    config_path.write_text(updated.rstrip() + "\n", encoding="utf-8")


def load_manifest(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {"pages": [], "images": []}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"pages": [], "images": []}
    return {
        "pages": list(loaded.get("pages", [])),
        "images": list(loaded.get("images", [])),
    }


def safe_generated_path(docs_dir: Path, relative_path: str) -> Path | None:
    candidate = (docs_dir / relative_path).resolve()
    docs_root = docs_dir.resolve()
    if candidate == docs_root or docs_root not in candidate.parents:
        return None
    return candidate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wiki-dir", type=Path, required=True)
    parser.add_argument("--docs-dir", type=Path, required=True)
    arguments = parser.parse_args()

    wiki_dir = arguments.wiki_dir.resolve()
    docs_dir = arguments.docs_dir.resolve()
    pages = discover_pages(wiki_dir)
    aliases = {
        alias: page
        for page in pages
        for alias in page_aliases(page)
    }
    token = os.environ.get("BGA_WIKI_READ_TOKEN", "")
    image_map_path = docs_dir / "scripts" / "wiki_image_map.json"
    known_images = json.loads(image_map_path.read_text(encoding="utf-8"))
    manifest_path = docs_dir / MANIFEST_NAME
    old_manifest = load_manifest(manifest_path)
    used_images: set[str] = set()

    for page in pages:
        source_text = page.source.read_text(encoding="utf-8")
        body = remove_existing_front_matter(source_text)
        body = rewrite_page_links(body, aliases)
        body = localize_images(body, docs_dir, token, used_images, known_images)
        output = front_matter(page) + body.strip() + "\n"
        (docs_dir / page.output_name).write_text(output, encoding="utf-8")

    current_page_names = {page.output_name for page in pages}
    for relative_path in old_manifest["pages"]:
        if relative_path in current_page_names:
            continue
        generated_path = safe_generated_path(docs_dir, relative_path)
        if generated_path and generated_path.is_file():
            generated_path.unlink()

    for relative_path in old_manifest["images"]:
        if relative_path in used_images:
            continue
        generated_path = safe_generated_path(docs_dir, relative_path)
        if generated_path and generated_path.is_file() and generated_path.name.startswith("wiki-"):
            generated_path.unlink()

    update_header_pages(docs_dir / "_config.yml", pages)
    manifest = {
        "pages": sorted(current_page_names),
        "images": sorted(used_images),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Prepared {len(pages)} wiki page(s) and {len(used_images)} hosted image(s).")


if __name__ == "__main__":
    main()
