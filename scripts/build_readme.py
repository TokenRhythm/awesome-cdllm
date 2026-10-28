#!/usr/bin/env python3
"""Generate README.md and docs/core-systems.md from the YAML files in data/.

    python scripts/build_readme.py           # regenerate both files
    python scripts/build_readme.py --check   # exit 1 if either file is stale (used in CI)

The only dependency is PyYAML (see requirements.txt).
"""
import argparse
import pathlib
import re
import sys
from collections import Counter

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TEMPLATE = ROOT / "scripts" / "README.template.md"
README = ROOT / "README.md"
CORE_DOC = ROOT / "docs" / "core-systems.md"

REQUIRED = ("id", "title", "category", "date", "venue", "paper", "summary")
LOOKUP_FIELDS = ("group", "method", "year", "target", "transition", "decoder", "task", "section")
DATE_RE = re.compile(r"^\d{4}(-(0[1-9]|1[0-2]))?$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")

# Order and labels of the state families in the survey's lookup table (Appendix F).
LOOKUP_GROUPS = [
    "Learned token lookup",
    "Fixed or pretrained token lookup",
    "Vocabulary logits, simplex, and one-hot endpoints",
    "Belief vectors",
    "Analog bits and visual encodings",
    "Contextual encodings, full length (frozen or jointly learned)",
    "Compressed codes with fewer positions",
    "Compressed codes with narrower channels",
    "Remapped cross-modal variational codes",
    "Sentence and segment vectors",
]


def load_yaml(name):
    with open(DATA / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


# --------------------------------------------------------------------------- validation
def validate(groups, papers):
    errors = []
    cat_ids = {c["id"] for g in groups for c in g["categories"]}
    seen_ids, seen_urls = set(), {}
    for i, p in enumerate(papers):
        where = f"papers.yaml entry #{i + 1} ({p.get('id', '?')})"
        for field in REQUIRED:
            if not p.get(field):
                errors.append(f"{where}: missing `{field}`")
        if p.get("id") in seen_ids:
            errors.append(f"{where}: duplicate id")
        seen_ids.add(p.get("id"))
        if p.get("category") not in cat_ids:
            errors.append(f"{where}: unknown category `{p.get('category')}`")
        if p.get("date") and not DATE_RE.match(str(p["date"])):
            errors.append(f"{where}: date must be YYYY or YYYY-MM, got `{p['date']}`")
        for field in ("paper", "project"):
            if p.get(field) and not str(p[field]).startswith("https://"):
                errors.append(f"{where}: `{field}` must be an https URL")
        if p.get("paper"):
            if p["paper"] in seen_urls:
                errors.append(f"{where}: paper URL also used by `{seen_urls[p['paper']]}`")
            seen_urls[p["paper"]] = p.get("id")
        if p.get("code") and not REPO_RE.match(p["code"]):
            errors.append(f"{where}: `code` must be `owner/repo`, got `{p['code']}`")
        if p.get("code_path") and (not p.get("code") or str(p["code_path"]).startswith("/")):
            errors.append(f"{where}: `code_path` needs `code` and must be relative, e.g. `tree/main/subdir`")
        if p.get("code_note") and not p.get("code"):
            errors.append(f"{where}: `code_note` needs `code`")
        summary = p.get("summary", "")
        if summary and not summary.endswith("."):
            errors.append(f"{where}: summary must end with a period")
        if "|" in summary or "\n" in summary.strip():
            errors.append(f"{where}: summary must be one line without `|`")
        if "lookup" in p:
            errors += validate_lookup(where, p["lookup"])
    return errors


def validate_lookup(where, lk):
    if not isinstance(lk, dict):
        return [f"{where}: `lookup` must be a mapping"]
    errors = [f"{where}: lookup is missing `{f}`" for f in LOOKUP_FIELDS if lk.get(f) in (None, "")]
    if lk.get("group") and lk["group"] not in LOOKUP_GROUPS:
        errors.append(f"{where}: unknown lookup group `{lk['group']}` (see LOOKUP_GROUPS in build_readme.py)")
    if lk.get("year") is not None and not (isinstance(lk["year"], int) and 2000 <= lk["year"] <= 2100):
        errors.append(f"{where}: lookup year must be an integer year, got `{lk['year']}`")
    return errors


# --------------------------------------------------------------------------- rendering
def cell(text):
    return str(text).replace("|", "\\|").strip()


def sort_key(p):
    date = str(p["date"])
    year, _, month = date.partition("-")
    return (int(year), int(month or 0), p["title"].lower())


def code_url(p):
    url = f"https://github.com/{p['code']}"
    return f"{url}/{p['code_path']}" if p.get("code_path") else url


def link_title(text):
    """Markdown link title (tooltip); double quotes would end it early."""
    return cell(text).replace('"', "'")


def code_badge(p):
    if p.get("code"):
        # compact badge (GitHub logo + star count): the social style is too wide for the column
        title = f' "{link_title(p["code_note"])}"' if p.get("code_note") else ""
        return (f"[![GitHub stars](https://img.shields.io/github/stars/{p['code']}?style=flat&logo=github&label=&color=2F5D8A)]"
                f"({code_url(p)}{title})")
    if p.get("project"):
        return f"[Project]({p['project']})"
    return "—"


def system_anchor(p):
    return f"system-{p['id']}"


def paper_table(entries):
    rows = [
        "| Model | Paper | Venue | Date | Code |",
        "| :-- | :-- | :--: | :--: | :--: |",
    ]
    for p in sorted(entries, key=sort_key, reverse=True):
        name = f"**{cell(p['name'])}**" if p.get("name") else "—"
        if p.get("lookup"):
            name += (f' [◆](docs/core-systems.md#{system_anchor(p)} '
                     f'"Core system in the survey\'s lookup table (Appendix F)")')
        paper = f"[{cell(p['title'])}]({p['paper']})<br>{cell(p['summary'])}"
        date = str(p["date"]).replace("-", ".")  # a hyphen would let the narrow column wrap
        rows.append(f"| {name} | {paper} | {cell(p['venue'])} | {date} | {code_badge(p)} |")
    return "\n".join(rows)


BACK_TO_CONTENTS = '<p align="right"><sub><a href="#contents">⬆ Back to contents</a></sub></p>'


def render_contents(groups, by_cat):
    lines = ["- [🧭 The Survey at a Glance](#survey-at-a-glance)"]
    for g in groups:
        n = sum(len(by_cat[c["id"]]) for c in g["categories"])
        lines.append(f"- [{g['emoji']} {g['title']}](#{g['id']}) ({n})")
        if len(g["categories"]) > 1:
            for c in g["categories"]:
                lines.append(f"  - [{c['title']}](#{c['id']}) ({len(by_cat[c['id']])})")
    lines.append("- [🗺️ Core Systems at a Glance](#core-systems)")
    lines.append("- [🔗 Related Awesome Lists](#related)")
    lines.append("- [📝 Citation](#citation)")
    return "\n".join(lines)


def render_catalog(groups, by_cat):
    out = []
    for g in groups:
        out.append(f'<a id="{g["id"]}"></a>')
        if len(g["categories"]) == 1:
            c = g["categories"][0]
            out.append(f"## {g['emoji']} {c['title']}")
            out.append("")
            out.append(f"> {c['description'].strip()} <sub>(Survey {c['survey']})</sub>")
            out.append("")
            out.append(paper_table(by_cat[c["id"]]))
            out += ["", BACK_TO_CONTENTS, ""]
        else:
            out.append(f"## {g['emoji']} {g['title']}")
            out.append("")
            out.append(f"*{g['blurb'].strip()}* <sub>(Survey {g['survey']})</sub>")
            for c in g["categories"]:
                out.append("")
                out.append(f'<a id="{c["id"]}"></a>')
                out.append(f"### {c['title']}")
                out.append("")
                out.append(f"> {c['description'].strip()} <sub>(Survey {c['survey']})</sub>")
                out.append("")
                out.append(paper_table(by_cat[c["id"]]))
                out += ["", BACK_TO_CONTENTS]
            out.append("")
    return "\n".join(out).rstrip()


def render_badges(survey, papers):
    # Plain HTML: Markdown is not processed inside the centered <p> block.
    repo = survey["repo"]
    badges = [
        ("https://awesome.re", "https://awesome.re/badge.svg", "Awesome"),
        (survey["pdf"], "https://img.shields.io/badge/Survey-PDF-b31b1b?logo=adobeacrobatreader&logoColor=white",
         "Survey PDF"),
    ]
    if survey.get("arxiv"):
        badges.append((f"https://arxiv.org/abs/{survey['arxiv']}",
                       f"https://img.shields.io/badge/arXiv-{survey['arxiv']}-b31b1b?logo=arxiv&logoColor=white",
                       "arXiv"))
    else:
        badges.append(("#citation", "https://img.shields.io/badge/arXiv-coming_soon-lightgrey?logo=arxiv&logoColor=white",
                       "arXiv: coming soon"))
    badges += [
        ("#contents", f"https://img.shields.io/badge/papers-{len(papers)}-2F5D8A", f"{len(papers)} papers"),
        (f"https://github.com/{repo}/commits/main",
         f"https://img.shields.io/github/last-commit/{repo}?color=2E6B3A", "Last commit"),
        ("CONTRIBUTING.md", "https://img.shields.io/badge/PRs-welcome-E9A23B", "PRs welcome"),
    ]
    return "\n".join(f'  <a href="{href}"><img src="{src}" alt="{alt}"></a>' for href, src, alt in badges)


def render_bibtex(survey):
    lines = [f"@misc{{{survey['bibkey']},",
             f"  title        = {{{survey['title']}}},",
             f"  author       = {{{{{survey['authors']}}}}},",
             "  year         = {2026},"]
    if survey.get("arxiv"):
        lines += [f"  eprint       = {{{survey['arxiv']}}},",
                  "  archivePrefix = {arXiv},",
                  f"  url          = {{https://arxiv.org/abs/{survey['arxiv']}}}"]
    else:
        lines += [f"  url          = {{https://github.com/{survey['repo']}}}"]
    lines.append("}")
    return "\n".join(lines)


def render_survey_links(survey):
    links = [f'<a href="{survey["pdf"]}">📄 PDF</a>']
    if survey.get("arxiv"):
        links.append(f'<a href="https://arxiv.org/abs/{survey["arxiv"]}">arXiv</a>')
    else:
        links.append("arXiv (coming soon)")
    links.append('<a href="#citation">📝 BibTeX</a>')
    links.append('<a href="docs/core-systems.md">🗺️ Core-system lookup</a>')
    return " · ".join(links)


def render_related(related):
    lines = []
    for r in related:
        badge = f"![GitHub stars](https://img.shields.io/github/stars/{r['repo']}?style=social&label=Star)"
        lines.append(f"- [{r['name']}](https://github.com/{r['repo']}) {badge} - {r['description'].strip()}")
    return "\n".join(lines)


def build_readme(groups, papers, survey, related):
    by_cat = {c["id"]: [] for g in groups for c in g["categories"]}
    for p in papers:
        by_cat[p["category"]].append(p)
    news = "\n".join(f"- **[{n['date']}]** {n['text'].strip()}" for n in survey["news"])
    meta = (f"{survey['month']} · {survey['pages']} pages · literature through {survey['coverage']}")
    values = {
        "REPO": survey["repo"],
        "PDF": survey["pdf"],
        "BADGES": render_badges(survey, papers),
        "NEWS": news,
        "SURVEY_META": meta,
        "SURVEY_LINKS": render_survey_links(survey),
        "CONTENTS": render_contents(groups, by_cat),
        "CATALOG": render_catalog(groups, by_cat),
        "CORE_COUNT": str(sum(1 for p in papers if p.get("lookup"))),
        "PAPER_COUNT": str(len(papers)),
        "RELATED": render_related(related),
        "BIBTEX": render_bibtex(survey),
        "COVERAGE": survey["coverage"],
    }
    text = TEMPLATE.read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", text)
    if leftover:
        sys.exit(f"unfilled placeholders in template: {sorted(set(leftover))}")
    return text.rstrip() + "\n"


def build_core_doc(papers):
    core = [p for p in papers if p.get("lookup")]
    out = [
        "<!-- Generated by scripts/build_readme.py from data/papers.yaml. Do not edit by hand. -->",
        "",
        "# Core Systems at a Glance",
        "",
        "This page reproduces the method lookup table of the survey (Appendix F). It lists the "
        f"{len(core)} core continuous-space text generation systems once each, grouped by the family of the "
        "generated state, and gives four standardized attributes for each system:",
        "",
        "- **Target**: what the network is trained to predict: a clean state *x*₀, noise *ε*, velocity *v*, "
        "a token-posterior cross-entropy (CE), probabilities under a weighted squared error, a flow-matching (FM) "
        "velocity, or a two-time flow map.",
        "- **Transition; order**: the generative dynamics (Gaussian or Dirichlet diffusion, flow matching, flow "
        "maps, belief updates, energy-based refinement, or drifting) and the unit refined at each step (the full "
        "sequence, latent blocks, the next vector, the next token, or a growing array).",
        "- **Decoder**: how terminal states become tokens: rounding or a vocabulary head, a shared contextual "
        "readout, a separate parallel or autoregressive (AR) decoder, or a discrete-diffusion decoder.",
        "- **§**: where the survey discusses the system.",
        "",
        "`n/a` means the source does not specify the attribute. Related discrete, hybrid, and pre-diffusion "
        "systems are summarized in Appendix C of the survey, and task-specific configurations are in the "
        "[main list](../README.md#tasks).",
        "",
        "## Contents",
        "",
    ]
    present = [g for g in LOOKUP_GROUPS if any(p["lookup"]["group"] == g for p in core)]
    for g in present:
        n = sum(1 for p in core if p["lookup"]["group"] == g)
        out.append(f"- [{g}](#{slug(g)}) ({n})")
    rendered = 0
    for g in present:
        rows = [p for p in core if p["lookup"]["group"] == g]
        rows.sort(key=lambda p: (int(p["lookup"]["year"]), p["lookup"]["method"].lower()))
        out += ["", f"## {g}", "",
                "| Method | Year | Target | Transition; order | Decoder | Task(s) | § |",
                "| :-- | :--: | :-- | :-- | :-- | :-- | :--: |"]
        for p in rows:
            lk = p["lookup"]
            # the anchor lets ◆ in README.md jump to this exact row
            method = f'<a id="{system_anchor(p)}"></a>[{cell(lk["method"])}]({p["paper"]})'
            if p.get("code"):
                method += f" [<sub>code</sub>]({code_url(p)})"
            if lk.get("state_note"):
                method += f"<br><sub>State: {cell(lk['state_note'])}</sub>"
            section = cell(lk["section"]).replace("App. ", "App.&nbsp;")
            out.append(f"| {method} | {lk['year']} | {cell(lk['target'])} | {cell(lk['transition'])} | "
                       f"{cell(lk['decoder'])} | {cell(lk['task'])} | {section} |")
            rendered += 1
    if rendered != len(core):
        sys.exit(f"core-systems page rendered {rendered} rows for {len(core)} lookup records")
    out += ["", "---", "", "[⬅ Back to the paper list](../README.md)", ""]
    return "\n".join(out)


def slug(text):
    s = text.lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="fail if generated files are out of date")
    args = ap.parse_args()

    groups = load_yaml("categories.yaml")["groups"]
    papers = load_yaml("papers.yaml")
    survey = load_yaml("survey.yaml")
    related = load_yaml("related.yaml")

    errors = validate(groups, papers)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(f"{len(errors)} validation error(s)")

    outputs = {README: build_readme(groups, papers, survey, related), CORE_DOC: build_core_doc(papers)}
    stale = []
    for path, text in outputs.items():
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != text:
            stale.append(path.relative_to(ROOT).as_posix())
            if not args.check:
                path.write_text(text, encoding="utf-8", newline="\n")
    counts = Counter(p["category"] for p in papers)
    if args.check:
        if stale:
            sys.exit(f"out of date: {', '.join(stale)}; run `python scripts/build_readme.py`")
        print(f"OK: {len(papers)} papers in {len(counts)} categories; generated files are up to date")
    else:
        print(f"{len(papers)} papers in {len(counts)} categories; wrote {', '.join(stale) or 'nothing (no changes)'}")


if __name__ == "__main__":
    main()
