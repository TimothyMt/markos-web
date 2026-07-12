#!/usr/bin/env python3
"""brain/_check.py — Linter mối nối (synapse) cho vault brain/.

Bắt lỗi "synapse đứt" TỰ ĐỘNG, không đợi runtime:
  - slug phải khớp tên file
  - industry.fit_frameworks -> file framework có thật
  - framework.composes_with [[x]] -> file framework có thật
  - craft.industry -> file industry có thật
  - craft.expresses [[x]] -> file framework có thật
  - giá trị stage: trong framework -> file stage có thật

KHÔNG phụ thuộc pyyaml (parser frontmatter tối giản cho định dạng brain đã kiểm soát).
Chạy:  py brain/_check.py       (exit 0 = thông; exit 1 = có synapse đứt)
"""
from __future__ import annotations
import os, sys, re, glob

BRAIN = os.path.dirname(os.path.abspath(__file__))


def _parse_frontmatter(path: str) -> dict:
    """Đọc block YAML giữa cặp '---' đầu file. Chỉ hỗ trợ scalar + list phẳng."""
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}
    fm: dict = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, rest = line.partition(":")
        key, rest = key.strip(), rest.strip()
        if rest.startswith("[") and rest.endswith("]"):
            inner = rest[1:-1].strip()
            items = [x.strip().strip('"').strip("'") for x in inner.split(",")] if inner else []
            fm[key] = [x for x in items if x]
        else:
            fm[key] = rest.strip().strip('"').strip("'")
    return fm


def _wikilinks(val) -> list[str]:
    """Trích slug từ ["[[stp]]", ...] hoặc "[[jtbd]]"."""
    out = []
    items = val if isinstance(val, list) else [val]
    for it in items:
        for mm in re.findall(r"\[\[([^\]]+)\]\]", str(it)):
            out.append(mm.strip())
    return out


def _slugs(folder: str) -> set[str]:
    return {os.path.splitext(os.path.basename(p))[0]
            for p in glob.glob(os.path.join(BRAIN, folder, "*.md"))}


def main() -> int:
    frameworks = _slugs("frameworks")
    industries = _slugs("industries")
    stages = _slugs("stages")
    errors: list[str] = []

    def load(folder):
        for p in sorted(glob.glob(os.path.join(BRAIN, folder, "*.md"))):
            yield p, os.path.splitext(os.path.basename(p))[0], _parse_frontmatter(p)

    # 1) slug khớp tên file (industry + stage khai slug tường minh)
    for folder in ("industries", "stages"):
        for p, name, fm in load(folder):
            if fm.get("slug") and fm["slug"] != name:
                errors.append(f"[slug] {folder}/{name}.md: slug='{fm['slug']}' != tên file '{name}'")

    # 2) framework.composes_with -> framework tồn tại; stage: -> stage tồn tại
    for p, name, fm in load("frameworks"):
        for tgt in _wikilinks(fm.get("composes_with", [])):
            if tgt not in frameworks:
                errors.append(f"[composes_with] frameworks/{name}.md -> [[{tgt}]] KHÔNG có file framework")
        for st in (fm.get("stage") or []):
            if st not in stages:
                errors.append(f"[stage] frameworks/{name}.md: stage '{st}' KHÔNG có file stages/{st}.md")

    # 3) industry.fit_frameworks -> framework tồn tại
    for p, name, fm in load("industries"):
        for tgt in _wikilinks(fm.get("fit_frameworks", [])):
            if tgt not in frameworks:
                errors.append(f"[fit_frameworks] industries/{name}.md -> [[{tgt}]] KHÔNG có file framework")

    # 4) craft.industry -> industry tồn tại; craft.expresses -> framework tồn tại
    for p, name, fm in load("craft"):
        ind = fm.get("industry")
        if ind and ind not in ("all", "[all]") and ind not in industries:
            errors.append(f"[industry] craft/{name}.md: industry '{ind}' KHÔNG có file industries/{ind}.md")
        for tgt in _wikilinks(fm.get("expresses", [])):
            if tgt not in frameworks:
                errors.append(f"[expresses] craft/{name}.md -> [[{tgt}]] KHÔNG có file framework")

    n = len(frameworks) + len(industries) + len(stages) + len(_slugs("craft"))
    if errors:
        print(f"BRAIN CHECK: {len(errors)} synapse ĐỨT / {n} note\n")
        for e in errors:
            print("  ✗", e)
        return 1
    print(f"BRAIN CHECK: OK — {n} note, mọi synapse thông "
          f"({len(frameworks)} framework · {len(industries)} industry · "
          f"{len(_slugs('craft'))} craft · {len(stages)} stage)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
