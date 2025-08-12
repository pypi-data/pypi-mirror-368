#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import html
import itertools
import json
import os
import re
import sys
from pathlib import Path

import requests
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich import box

API_ROOT = "https://www.sefaria.org"
TOC_URL = f"{API_ROOT}/api/index"
INDEX_V2_URL = f"{API_ROOT}/api/v2/raw/index"
TEXTS_V3_URL = f"{API_ROOT}/api/v3/texts"
TEXTS_V1_URL = f"{API_ROOT}/api/texts"

CACHE_DIR = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "sefaria_cli"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
TOC_CACHE = CACHE_DIR / "toc.json"

console = Console()

# -------------------------
# Utilities / cleaning
# -------------------------

FOOTNOTE_MARKER_RE = re.compile(
    r"<sup[^>]*class=['\"][^'\"]*footnote-marker[^'\"]*['\"][^>]*>.*?</sup>",
    re.I | re.S,
)
FOOTNOTE_TEXT_RE = re.compile(
    r"<i[^>]*class=['\"][^'\"]*footnote[^'\"]*['\"][^>]*>.*?</i>",
    re.I | re.S,
)
TAG_RE = re.compile(r"<[^>]+>")

def strip_html(s: str, keep_notes: bool = False) -> str:
    """Remove HTML; optionally keep Sefaria footnote markers/text."""
    if not isinstance(s, str):
        s = str(s)
    if not keep_notes:
        s = FOOTNOTE_MARKER_RE.sub("", s)
        s = FOOTNOTE_TEXT_RE.sub("", s)
    s = TAG_RE.sub("", s)
    s = html.unescape(s)
    return s.replace("\xa0", " ").strip()

def flatten_lines(x):
    """Yield strings from arbitrarily nested lists/strings."""
    if x is None:
        return
    if isinstance(x, (list, tuple)):
        for el in x:
            yield from flatten_lines(el)
    else:
        yield str(x)

def http_get(url, params=None, timeout=20):
    headers = {"User-Agent": "sefaria-cli/1.3 (+local; educational use)"}
    r = requests.get(url, params=params or {}, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json()

def load_toc(force_refresh=False):
    """Load and cache the Table of Contents (normalize to {'contents': [...]})."""
    if TOC_CACHE.exists() and not force_refresh:
        try:
            data = json.loads(TOC_CACHE.read_text("utf-8"))
            if isinstance(data, list):
                data = {"contents": data}
            return data
        except Exception:
            pass
    data = http_get(TOC_URL)
    if isinstance(data, list):
        data = {"contents": data}
    TOC_CACHE.write_text(json.dumps(data), encoding="utf-8")
    return data

def list_top_categories(toc):
    if isinstance(toc, list):
        toc = {"contents": toc}
    return [c for c in toc.get("contents", []) if "category" in c]

def find_category_node(toc, category_path):
    node = toc if isinstance(toc, dict) else {"contents": toc}
    for cat in category_path:
        found = None
        for child in node.get("contents", []):
            if child.get("category") == cat:
                found = child
                break
        if not found:
            return None
        node = found
    return node

def list_texts_in_category(node):
    return [child for child in node.get("contents", []) if "title" in child]

def choose_from_list(title, items, label_func=lambda x: x, allow_back=True):
    while True:
        console.print(f"\n[bold]{title}[/bold]")
        for i, item in enumerate(items, start=1):
            console.print(f"  [cyan]{i}[/cyan]. {label_func(item)}")
        if allow_back:
            console.print("  [cyan]0[/cyan]. Back")
        idx = IntPrompt.ask("Select", default=0 if allow_back else 1)
        if allow_back and idx == 0:
            return None
        if 1 <= idx <= len(items):
            return items[idx - 1]
        console.print("[red]Invalid selection[/red]")

def get_index_record(title):
    return http_get(f"{INDEX_V2_URL}/{requests.utils.quote(title)}")

def _guess_title(tref: str) -> str:
    return (tref.split(",")[0] if "," in tref else tref.split()[0])

def _normalize_text_payload(payload, keep_notes):
    """Return (he_lines, en_lines, ref, title) cleaned and flattened."""
    he = payload.get("he") or payload.get("hebrew") or []
    en = payload.get("en") or payload.get("english") or payload.get("text") or []
    ref = payload.get("ref") or payload.get("citation")
    title = payload.get("index_title") or payload.get("book")
    he = [strip_html(s, keep_notes=keep_notes) for s in flatten_lines(he)]
    en = [strip_html(s, keep_notes=keep_notes) for s in flatten_lines(en)]
    return he, en, ref, title

def get_text_bilingual(tref, lang_pref="bi", keep_notes=False):
    """Prefer v3; fall back to v1. Return dict with he/en lists and metadata."""
    # Try v3
    try:
        data = http_get(f"{TEXTS_V3_URL}/{requests.utils.quote(tref)}")
        if isinstance(data, dict):
            if "text" in data and isinstance(data["text"], dict):
                he, en, ref, title = _normalize_text_payload(
                    {"he": data["text"].get("he"),
                     "en": data["text"].get("en"),
                     "ref": data.get("ref"),
                     "index_title": data.get("index_title")},
                    keep_notes,
                )
            else:
                he, en, ref, title = _normalize_text_payload(data, keep_notes)
            if he or en:
                return {"he": he, "en": en, "ref": ref or tref, "title": title or _guess_title(tref)}
    except Exception:
        pass

    # Fallback to v1
    params = {"lang": "bi"} if lang_pref == "bi" else {"lang": lang_pref}
    data = http_get(f"{TEXTS_V1_URL}/{requests.utils.quote(tref)}", params=params)
    he, en, ref, title = _normalize_text_payload(data, keep_notes)
    return {"he": he, "en": en, "ref": ref or tref, "title": title or _guess_title(tref)}

# -------------------------
# Rendering
# -------------------------

def print_text_block(data, mode="bi", layout="sbs"):
    title = data.get("title", "")
    ref = data.get("ref", "")
    he = data.get("he", [])
    en = data.get("en", [])
    console.rule(f"[bold]{title} — {ref}[/bold]")

    if mode in ("he", "en"):
        lines = he if mode == "he" else en
        for i, line in enumerate(lines, 1):
            console.print(f"[dim]{i:>3}[/dim] {line}")
        return

    if layout == "stack":
        console.print("[bold]Hebrew[/bold]")
        for i, line in enumerate(he, 1):
            console.print(f"[dim]{i:>3}[/dim] {line}")
        console.print()
        console.print("[bold]English[/bold]")
        for i, line in enumerate(en, 1):
            console.print(f"[dim]{i:>3}[/dim] {line}")
        return

    table = Table(box=box.MINIMAL_DOUBLE_HEAD, expand=True, show_lines=False, pad_edge=False)
    table.add_column("Hebrew", justify="right", ratio=1, overflow="fold", no_wrap=False)
    table.add_column("English", justify="left", ratio=1, overflow="fold", no_wrap=False)
    for l, r in itertools.zip_longest(he, en, fillvalue=""):
        table.add_row(l, r)
    console.print(table)

# -------------------------
# Schema helpers
# -------------------------

def _collect_leaf_paths(node, cur_path, out):
    """
    Collect English paths to leaves, e.g., ['Genesis','Bereshit'].
    """
    if not isinstance(node, dict):
        return

    def en_title(n):
        for t in n.get("titles", []):
            if t.get("lang") == "en" and t.get("text"):
                return t["text"]
        return n.get("enTitle") or n.get("title")

    # Composite node
    if node.get("nodes"):
        for ch in node["nodes"]:
            title = en_title(ch)
            next_path = cur_path + ([title] if title else [])
            _collect_leaf_paths(ch, next_path, out)
        return

    # Leaf
    title = en_title(node)
    if title:
        out.append(cur_path + [title])

def _infer_numeric_sections(schema):
    """
    If index uses numeric sections (e.g., Chapter/Verse) return ['1','2',...].
    Uses first node's 'lengths' if present.
    """
    node = None
    if isinstance(schema, dict):
        if schema.get("nodes"):
            node = schema["nodes"][0]
        else:
            node = schema
    if not isinstance(node, dict):
        return None
    lengths = node.get("lengths")
    if isinstance(lengths, list) and lengths and isinstance(lengths[0], int) and lengths[0] > 0:
        return [str(i) for i in range(1, lengths[0] + 1)]
    return None

# -------------------------
# Interactive flows
# -------------------------

def interactive_browse(lang_mode, layout, keep_notes):
    toc = load_toc()
    top = list_top_categories(toc)
    cat = choose_from_list("Top Categories", top, label_func=lambda n: n.get("category", ""))
    if not cat:
        return

    path = [cat["category"]]
    while True:
        node = find_category_node(toc, path)
        if not node:
            console.print("[red]Category not found[/red]")
            return
        subcats = [c for c in node.get("contents", []) if "category" in c]
        texts = list_texts_in_category(node)

        table = Table(box=box.SIMPLE, show_header=True)
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Name", style="white")
        for sc in subcats:
            table.add_row("Category", sc["category"])
        for t in texts:
            table.add_row("Text", t["title"])
        console.print(table)

        names = [("Category", sc["category"]) for sc in subcats] + [("Text", t["title"]) for t in texts]
        if not names:
            console.print("[yellow]No further items.[/yellow]")
            return
        selection = Prompt.ask("Type a name to open (or '..' to go back)", default="..")
        if selection.strip() == "..":
            if len(path) == 1:
                return
            path.pop()
            continue
        matches = [n for n in names if n[1].lower() == selection.strip().lower()]
        if not matches:
            console.print("[red]Not found. Use the exact name as shown.[/red]")
            continue
        kind, name = matches[0]
        if kind == "Category":
            path.append(name)
            continue

        # Open a text: propose valid sections (numeric chapters or named leaf paths)
        try:
            idx = get_index_record(name)
        except Exception as e:
            console.print(f"[red]Failed to load index for {name}:[/red] {e}")
            idx = None

        leaf_paths = []
        chapters = None
        if idx and "schema" in idx:
            _collect_leaf_paths(idx["schema"], [], leaf_paths)  # e.g., ['Genesis','Bereshit']
            chapters = _infer_numeric_sections(idx["schema"])   # e.g., ['1','2',...]

        if chapters:
            chap = choose_from_list(f"Select a chapter of [bold]{name}[/bold]",
                                    chapters, label_func=lambda s: s, allow_back=True)
            if not chap:
                return
            verses = Prompt.ask("Optional verse(s), e.g., '1-5' (blank for whole chapter)", default="")
            tref = f"{name} {chap}{(':' + verses.strip()) if verses.strip() else ''}"

        elif leaf_paths:
            def label(p): return " \u2192 ".join(p)  # "Genesis → Bereshit"
            choice = choose_from_list(f"Select a section of [bold]{name}[/bold]",
                                      leaf_paths, label_func=label, allow_back=True)
            if not choice:
                return
            extra = Prompt.ask("Optional further reference (e.g., '1:1-5'; leave blank for whole section)", default="")
            tref = f"{name}, {', '.join(choice)}{(' ' + extra.strip()) if extra.strip() else ''}"

        else:
            tref = Prompt.ask(f"Enter a reference (e.g., '{name} 2:1-5' or '{name}, Genesis, Bereshit')",
                              default=name)

        try:
            data = get_text_bilingual(tref, "bi" if lang_mode == "bi" else lang_mode, keep_notes=keep_notes)
            print_text_block(data, mode=lang_mode, layout=layout)
        except requests.HTTPError as e:
            console.print(f"[red]Couldn’t fetch '{tref}':[/red] {e}")
            if chapters:
                console.print("[yellow]Tip:[/yellow] Examples: "
                              f"'{name} 1', '{name} 2:1-5'")
            elif leaf_paths:
                console.print("[yellow]Tip:[/yellow] Examples:")
                for p in leaf_paths[:8]:
                    console.print(f"  • {name}, {', '.join(p)}")
        return

def open_direct(tref, lang_mode, layout, keep_notes):
    data = get_text_bilingual(tref, "bi" if lang_mode == "bi" else lang_mode, keep_notes=keep_notes)
    print_text_block(data, mode=lang_mode, layout=layout)

# -------------------------
# Main
# -------------------------

def main():
    parser = argparse.ArgumentParser(
        description="CLI browser for Sefaria texts (bilingual by default).",
        epilog="Examples:\n"
               "  python3 sefaria_cli.py                       # interactive browse\n"
               "  python3 sefaria_cli.py --open 'Genesis 1'   # open a specific ref\n"
               "  python3 sefaria_cli.py --lang en            # English only\n"
               "  python3 sefaria_cli.py --layout stack       # Hebrew then English\n",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--refresh", action="store_true", help="Refresh cached table of contents")
    parser.add_argument("--lang", choices=["bi", "en", "he"], default="bi",
                        help="Text display: 'bi' (default), 'en', or 'he'")
    parser.add_argument("--open", dest="tref", help="Open a specific reference directly (e.g., 'Berakhot 2a')")
    parser.add_argument("--layout", choices=["sbs", "stack"], default="sbs",
                        help="Bilingual layout: side-by-side (sbs) or stacked (stack)")
    parser.add_argument("--notes", choices=["on", "off"], default="off",
                        help="Show footnote markers/text (default off)")
    args = parser.parse_args()

    keep_notes = (args.notes == "on")

    try:
        load_toc(force_refresh=args.refresh)
    except Exception as e:
        console.print(f"[red]Failed to load Table of Contents:[/red] {e}")
        sys.exit(1)

    if args.tref:
        open_direct(args.tref, args.lang, args.layout, keep_notes)
    else:
        interactive_browse(args.lang, args.layout, keep_notes)

if __name__ == "__main__":
    main()
