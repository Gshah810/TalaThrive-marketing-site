#!/usr/bin/env python3
"""Scrape Tala Thrive stories/blog off the Framer site into portable Markdown + assets.

Output: tmp/stories-export/
  stories/<slug>.md      Markdown + YAML frontmatter, image paths rewritten to ../assets/
  assets/<file>          Original full-resolution images
  index.json             Machine-readable manifest
  README.md              Handoff notes
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from html import unescape

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")
SITE = "https://www.talathrive.com"
OUT = "/Users/jaspermondares/Projects/tala-thrive/tmp/stories-export"

BLOCKS = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol", "blockquote", "img", "figure"}


def fetch(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", "replace")


def story_urls():
    xml = fetch(f"{SITE}/sitemap.xml")
    locs = re.findall(r"<loc>([^<]+)</loc>", xml)
    return [u for u in locs if "/stories/" in u]


def clean(text):
    text = unescape(text).replace(" ", " ")
    return re.sub(r"[ \t]+", " ", text).strip()


def md_dest(url):
    """Markdown link destination. Angle-bracket it when bare parens would be ambiguous."""
    if re.search(r"[()\s]", url):
        return "<" + url.replace("<", "%3C").replace(">", "%3E") + ">"
    return url


def edge_space(text):
    """Leading and trailing whitespace of a string, so it can be re-emitted outside markers."""
    return text[:len(text) - len(text.lstrip())], text[len(text.rstrip()):]


def wrap_preserving_space(inner, mark):
    """Wrap inner in Markdown markers, keeping any whitespace outside the markers."""
    core = inner.strip()
    if not core:
        return inner  # whitespace-only wrapper: the whitespace IS the content
    lead, trail = edge_space(inner)
    return f"{lead}{mark}{core}{mark}{trail}"


def inline_md(node):
    """Render inline content of a tag to Markdown."""
    out = []
    for child in node.children:
        if isinstance(child, Comment):
            continue  # Framer/React SSR emits <!--$--> Suspense markers around links
        if isinstance(child, NavigableString):
            # Escape literal emphasis characters typed by the author, e.g. one
            # post contains "(**raises hand**)" as literal text inside <strong>.
            txt = unescape(str(child)).replace("\u00a0", " ")
            out.append(re.sub(r"([*_])", r"\\\1", txt))
        elif isinstance(child, Tag):
            name = child.name.lower()
            inner = inline_md(child)
            if name in ("strong", "b", "em", "i"):
                # Framer emits wrappers holding only a space (e.g. <em> </em>).
                # Stripping them would silently glue the neighbouring words together.
                mark = "**" if name in ("strong", "b") else "*"
                out.append(wrap_preserving_space(inner, mark))
            elif name == "code":
                out.append(f"`{inner.strip()}`")
            elif name == "br":
                out.append("\n")
            elif name == "a":
                href = child.get("href", "")
                core = inner.strip()
                if not href:
                    out.append(inner)
                elif not core:
                    out.append(inner if inner else href)
                else:
                    lead, trail = edge_space(inner)
                    out.append(f"{lead}[{core}]({md_dest(href)}){trail}")
            elif name == "img":
                src = child.get("src", "")
                alt = child.get("alt", "") or ""
                out.append(f"![{alt}]({md_dest(src)})")
            else:
                out.append(inner)
    return "".join(out)


def collect_images(node, images):
    for img in node.find_all("img"):
        src = img.get("src")
        if src:
            images.append((src, img.get("alt") or ""))


def render_block(el, images):
    name = el.name.lower()
    if name == "img":
        src = el.get("src")
        if not src:
            return None
        images.append((src, el.get("alt") or ""))
        return f"![{el.get('alt') or ''}]({md_dest(src)})"
    if name == "figure":
        collect_images(el, images)
        img = el.find("img")
        cap = el.find("figcaption")
        if not img:
            return None
        md = f"![{img.get('alt') or ''}]({md_dest(img.get('src',''))})"
        if cap:
            md += f"\n\n*{clean(cap.get_text())}*"
        return md
    if re.fullmatch(r"h[1-6]", name):
        txt = clean(inline_md(el))
        if not txt:
            return None
        level = min(int(name[1]) + 1, 6)  # demote: article title becomes H1
        return "#" * level + " " + txt
    if name == "blockquote":
        collect_images(el, images)
        txt = clean(inline_md(el))
        return "> " + txt.replace("\n", "\n> ") if txt else None
    if name in ("ul", "ol"):
        collect_images(el, images)
        lines = []
        for n, li in enumerate(el.find_all("li", recursive=False), start=1):
            txt = clean(inline_md(li))
            if txt:
                lines.append((f"{n}. " if name == "ol" else "- ") + txt)
        return "\n".join(lines) if lines else None
    if name == "p":
        collect_images(el, images)
        txt = inline_md(el)
        txt = re.sub(r"[ \t]+", " ", unescape(txt)).strip()
        return txt or None
    return None


DATE_RE = re.compile(r"^[A-Z][a-z]{2} \d{1,2}, \d{4}$")


def parse_story(url, html):
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()

    slug = url.rstrip("/").split("/")[-1]
    page_title = clean(soup.title.get_text()) if soup.title else ""
    page_title = re.sub(r"\s*-\s*Tala Thrive.*$", "", page_title)

    og = soup.find("meta", property="og:image")
    og_image = og.get("content") if og else None

    body = soup.body or soup
    all_els = list(body.descendants)

    # Anchor on the date <h6>; the article title is the nearest preceding heading.
    date_el = None
    for el in all_els:
        if isinstance(el, Tag) and el.name == "h6" and DATE_RE.match(clean(el.get_text())):
            date_el = el
            break

    title_el = None
    if date_el:
        idx = all_els.index(date_el)
        for el in reversed(all_els[:idx]):
            if isinstance(el, Tag) and re.fullmatch(r"h[1-5]", el.name or ""):
                title_el = el
                break

    title = clean(title_el.get_text()) if title_el else page_title
    date = clean(date_el.get_text()) if date_el else ""

    # End boundary: the "Previous"/"Next" prev-post nav, else the footer.
    end_el = None
    start_idx = all_els.index(date_el) if date_el else 0
    for el in all_els[start_idx:]:
        if isinstance(el, Tag) and el.name in ("h4", "h5", "p"):
            if clean(el.get_text()) in ("Previous", "Next"):
                end_el = el
                break
    end_idx = all_els.index(end_el) if end_el else len(all_els)

    region = all_els[start_idx + 1:end_idx]
    region_set = {id(x) for x in region}

    images = []
    parts = []
    emitted = []
    for el in region:
        if not isinstance(el, Tag) or el.name not in BLOCKS:
            continue
        # skip anything nested inside a block we already rendered
        if any(any(id(p) == id(done) for p in el.parents) for done in emitted):
            continue
        md = render_block(el, images)
        if md:
            parts.append(md)
            emitted.append(el)

    # de-dupe consecutive repeats (Framer renders responsive variants of the same node)
    deduped = []
    for p in parts:
        if not deduped or deduped[-1] != p:
            deduped.append(p)

    return {
        "slug": slug,
        "url": url,
        "title": title or page_title,
        "date": date,
        "og_image": og_image,
        "body_md": "\n\n".join(deduped).strip(),
        "images": images,
        "_region_ids": region_set,
    }


def asset_name(src):
    path = urllib.parse.urlparse(src).path
    return os.path.basename(path)


def main():
    os.makedirs(f"{OUT}/stories", exist_ok=True)
    os.makedirs(f"{OUT}/assets", exist_ok=True)

    urls = story_urls()
    print(f"{len(urls)} story URLs from sitemap", flush=True)

    manifest = []
    downloaded = {}
    failures = []

    for i, url in enumerate(urls, 1):
        try:
            html = fetch(url)
            s = parse_story(url, html)
        except Exception as e:
            failures.append((url, repr(e)))
            print(f"  !! {url}: {e}", flush=True)
            continue

        # Download every image referenced in the article body.
        local_map = {}
        for src, _alt in s["images"]:
            absolute = urllib.parse.urljoin(url, src)
            base = absolute.split("?")[0]          # original full-res, no Framer resize params
            fname = asset_name(base)
            if base not in downloaded:
                try:
                    blob = fetch(base, binary=True)
                    with open(f"{OUT}/assets/{fname}", "wb") as fh:
                        fh.write(blob)
                    downloaded[base] = fname
                except Exception as e:
                    failures.append((base, repr(e)))
                    continue
            local_map[src] = f"../assets/{downloaded[base]}"

        body = s["body_md"]
        for src_url, local in local_map.items():
            body = body.replace(src_url, local)

        # The per-story hero is the FIRST in-body image. og:image is a single
        # site-wide default (identical on all 36 posts), so it is not a hero.
        hero_local = ""
        if s["images"]:
            first_src = s["images"][0][0]
            hero_local = local_map.get(first_src, "")
            # Promote it out of the body so the template renders it once.
            lead = f"![]({hero_local})"
            if hero_local and body.startswith(lead):
                body = body[len(lead):].lstrip("\n")

        def esc(v):
            return '"' + str(v).replace('"', '\\"') + '"'

        fm = "\n".join([
            "---",
            f"title: {esc(s['title'])}",
            f"slug: {esc(s['slug'])}",
            f"date: {esc(s['date'])}",
            f"source_url: {esc(s['url'])}",
            f"hero_image: {esc(hero_local)}",
            f"og_image_sitewide_default: {esc(s['og_image'] or '')}",
            "---",
        ])
        md = fm + "\n\n# " + s["title"] + "\n\n" + body + "\n"
        with open(f"{OUT}/stories/{s['slug']}.md", "w") as fh:
            fh.write(md)

        words = len(re.findall(r"\w+", body))
        manifest.append({
            "slug": s["slug"],
            "title": s["title"],
            "date": s["date"],
            "source_url": s["url"],
            "markdown_file": f"stories/{s['slug']}.md",
            "hero_image": hero_local,
            "body_images": sorted(set(local_map.values())),
            "word_count": words,
        })
        print(f"[{i:2}/{len(urls)}] {s['slug'][:60]:60} {words:5}w {len(local_map)} img", flush=True)
        time.sleep(0.25)

    with open(f"{OUT}/index.json", "w") as fh:
        json.dump({"source": SITE, "count": len(manifest), "stories": manifest,
                   "failures": failures}, fh, indent=2)

    print(f"\nDone: {len(manifest)} stories, {len(downloaded)} assets, {len(failures)} failures")
    if failures:
        for u, e in failures:
            print("  FAIL", u, e)


if __name__ == "__main__":
    main()
