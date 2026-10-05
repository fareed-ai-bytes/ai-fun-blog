"""Pure text helpers for posts: slug (BR-10) and excerpt (BR-14)."""

import re
import unicodedata

EXCERPT_LIMIT = 280
SLUG_MAX_LENGTH = 200

_FENCED_CODE = re.compile(r"```.*?```|~~~.*?~~~", re.DOTALL)
_IMAGE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_HTML_TAG = re.compile(r"<[^>]+>")
_BLOCK_MARKER = re.compile(r"^\s{0,3}(?:#{1,6}|>+|[-*+]|\d+[.)])\s+", re.MULTILINE)
_HORIZONTAL_RULE = re.compile(r"^\s{0,3}(?:[-*_]\s*){3,}$", re.MULTILINE)
_EMPHASIS = re.compile(r"[*_~`]+")
_WHITESPACE = re.compile(r"\s+")


def slugify(title: str) -> str:
    """Kebab-case ASCII slug of a title; 'post' if nothing usable remains."""
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")
    return slug[:SLUG_MAX_LENGTH].rstrip("-") or "post"


def next_free_slug(base: str, taken: set[str]) -> str:
    """`base`, else `base-2`, `base-3`… — the first not in `taken` (BR-10)."""
    if base not in taken:
        return base
    n = 2
    while f"{base}-{n}" in taken:
        n += 1
    return f"{base}-{n}"


def make_excerpt(body_md: str, limit: int = EXCERPT_LIMIT) -> str:
    """First `limit` chars of the body with Markdown stripped, cut at a word boundary."""
    text = _FENCED_CODE.sub(" ", body_md)
    text = _IMAGE.sub(r"\1", text)
    text = _LINK.sub(r"\1", text)
    text = _HTML_TAG.sub(" ", text)
    text = _HORIZONTAL_RULE.sub(" ", text)
    text = _BLOCK_MARKER.sub("", text)
    text = _EMPHASIS.sub("", text)
    text = _WHITESPACE.sub(" ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[: limit + 1].rsplit(" ", 1)[0]
    return cut if 0 < len(cut) <= limit else text[:limit]
