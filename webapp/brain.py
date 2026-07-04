"""
K2 F1 — Loader runtime cho vault brain/ (no pyyaml).
Parser frontmatter tối giản + load_notes() có cache lazy.
"""
import os
import re
import functools
from typing import Any

BRAIN = os.path.join(os.path.dirname(os.path.dirname(__file__)), "brain")

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_LIST_RE = re.compile(r"^\s*-\s*(.+)$", re.MULTILINE)
_INLINE_LIST_RE = re.compile(r"^\s*(\w+):\s*\[(.*)\]\s*$", re.MULTILINE)
_SCALAR_RE = re.compile(r"^\s*(\w+):\s*(.+?)\s*$", re.MULTILINE)

# module-level cache for lazy loading
_notes_cache: dict[str, list[dict]] | None = None


def _parse_scalar(value: str) -> Any:
    """Parse scalar value: bool, int, float, string."""
    v = value.strip()
    # Remove surrounding quotes if present
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        v = v[1:-1]
    # bool
    if v.lower() == "true":
        return True
    if v.lower() == "false":
        return False
    # int
    try:
        return int(v)
    except ValueError:
        pass
    # float
    try:
        return float(v)
    except ValueError:
        pass
    return v


def _parse_inline_list(value: str) -> list:
    """Parse inline list like [a, b] or ["[[x]]", "y"]."""
    items = []
    # Split by comma, handling quoted strings
    current = ""
    in_quote = False
    quote_char = None
    for ch in value:
        if ch in ('"', "'") and not in_quote:
            in_quote = True
            quote_char = ch
        elif ch == quote_char and in_quote:
            in_quote = False
            quote_char = None
        elif ch == "," and not in_quote:
            items.append(current.strip())
            current = ""
            continue
        current += ch
    if current.strip():
        items.append(current.strip())

    # Parse each item
    result = []
    for item in items:
        item = item.strip()
        # Remove surrounding quotes
        if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
            item = item[1:-1]
        result.append(_parse_scalar(item))
    return result


def _parse_frontmatter(text: str) -> dict:
    """Parse frontmatter block into dict with scalar + flat list support."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}
    fm_text = match.group(1)

    result = {}

    # First pass: parse inline lists [a, b] and scalars
    for match in _INLINE_LIST_RE.finditer(fm_text):
        key, value = match.group(1), match.group(2)
        result[key] = _parse_inline_list(value)

    # Second pass: parse scalars (skip keys already parsed as lists)
    for match in _SCALAR_RE.finditer(fm_text):
        key, value = match.group(1), match.group(2)
        if key not in result:
            result[key] = _parse_scalar(value)

    # Third pass: parse dash-lists (flat lists like - item)
    for match in _LIST_RE.finditer(fm_text):
        key = match.string[match.start():match.end()].split(":")[0].strip()
        if key and key not in result:
            # Check if this is a list item under a key
            # Look for the key before this list item
            lines_before = fm_text[:match.start()].split('\n')
            for line in reversed(lines_before):
                line = line.strip()
                if line.endswith(":") and not line.startswith("-"):
                    parent_key = line[:-1].strip()
                    if parent_key not in result:
                        result[parent_key] = []
                    result[parent_key].append(_parse_scalar(match.group(1)))
                    break

    return result


def _parse_note(path: str) -> dict:
    """Parse a single note file into dict with frontmatter + body + slug + path."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    fm = _parse_frontmatter(content)
    fm_match = _FRONTMATTER_RE.match(content)
    body = content[fm_match.end():] if fm_match else content
    slug = os.path.splitext(os.path.basename(path))[0]

    result = {**fm, "body": body, "slug": slug, "path": path}
    return result


def _discover_notes() -> list[dict]:
    """Discover and parse all notes in brain/ subdirectories."""
    notes = []
    subdirs = ["frameworks", "industries", "craft", "stages"]
    for subdir in subdirs:
        dir_path = os.path.join(BRAIN, subdir)
        if not os.path.isdir(dir_path):
            continue
        for fname in os.listdir(dir_path):
            if fname.endswith(".md"):
                path = os.path.join(dir_path, fname)
                notes.append(_parse_note(path))
    return notes


def load_notes(kinds: list[str] | None = None) -> list[dict]:
    """Load all notes from brain/, optionally filtered by kinds (e.g., ['framework']).

    Uses module-level cache (lazy, first-read only).
    """
    global _notes_cache
    if _notes_cache is None:
        _notes_cache = {"all": _discover_notes()}
    notes = _notes_cache["all"]
    if kinds:
        return [n for n in notes if n.get("type") in kinds]
    return list(notes)


# ===== K2 F2 — select() + helpers =====

def _norm_industry(s: str | None) -> str:
    """Normalize industry slug: strip, lower, replace _ with -."""
    return (s or "").strip().lower().replace("_", "-")


def _slug(v: str | None) -> str:
    """Extract slug from [[link]] format or return normalized slug."""
    v = str(v or "").strip()
    if v.startswith("[[") and v.endswith("]]"):
        v = v[2:-2]
    return v.strip().lower()


def select(
    industry: str | None = None,
    stage: str | None = None,
    goal_type: str | None = None,
    statuses: tuple[str, ...] | None = ("live",),
) -> list[dict]:
    """Select frameworks filtered by industry, stage, goal_type, statuses.
    
    Ranking: maturity evergreen(0) < fresh(1) < decaying(2), then updated descending.
    Uses stable double-sort: updated desc first, then maturity asc.
    """
    ind = _norm_industry(industry) if industry else None
    out = []
    for n in load_notes(["framework"]):
        applies = [_slug(a) for a in (n.get("applies_to") or [])]
        if ind is not None and ind not in applies and "all" not in applies:
            continue
        if stage is not None and stage not in (n.get("stage") or []):
            continue
        if goal_type is not None and goal_type not in (n.get("goal_type") or []):
            continue
        if statuses is not None and n.get("status") not in statuses:
            continue
        out.append(n)

    _MAT = {"evergreen": 0, "fresh": 1, "decaying": 2}
    # Stable double-sort: updated desc first, then maturity asc
    out.sort(key=lambda n: n.get("updated", ""), reverse=True)   # updated desc
    out.sort(key=lambda n: _MAT.get(n.get("maturity"), 9))      # maturity asc (stable)
    return out


if __name__ == "__main__":
    # Self-test
    import sys
    print("Import test:", __name__)
    notes = load_notes()
    print(f"load_notes() -> {len(notes)} notes")
    fw = load_notes(["framework"])
    print(f"load_notes(['framework']) -> {len(fw)} notes")
    for n in notes:
        assert "slug" in n and "type" in n and "status" in n, f"missing fields in {n.get('slug')}"
    print("All notes have slug/type/status ✓")

    # Self-verify F2
    f = lambda xs: sorted(n['slug'] for n in xs)
    print('V1', f(select(statuses=None)))
    print('V2', f(select(industry='health-beauty', stage='launch', statuses=None)))
    print('snake', f(select(industry='health_beauty', stage='launch', statuses=None)))
    print('gt-pricing', f(select(goal_type='pricing', statuses=None)))
    print('gt-pos', f(select(goal_type='positioning', statuses=None)))
    print('live-default', f(select()))