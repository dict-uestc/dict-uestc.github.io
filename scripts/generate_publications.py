import bibtexparser
from bibtexparser.bparser import BibTexParser
from collections import defaultdict
from pathlib import Path
import re

# =========================
# CONFIG
# =========================
BIB_FILE = "_bibliography/papers.bib"
PUB_OUTPUT = "_pages/publications.md"
INDEX_FILE = "index.md"

# 👇 改成你团队成员名字（用于高亮）
TEAM_MEMBERS = {
    "Zeng, Shaoning": "🔥 Zeng Shaoning"
}


# =========================
# LOAD BIBTEX (ROBUST)
# =========================
def load_bib(path):
    with open(path, encoding="utf-8") as f:
        parser = BibTexParser(common_strings=True)
        parser.ignore_nonstandard_types = False
        bib_database = bibtexparser.load(f, parser=parser)
    return bib_database.entries


# =========================
# AUTHOR PROCESSING
# =========================
def format_authors(author_str):
    authors = [a.strip() for a in author_str.split(" and ")]

    formatted = []
    for a in authors:
        if a in TEAM_MEMBERS:
            formatted.append(f"**{TEAM_MEMBERS[a]}**")
        else:
            formatted.append(a)

    return ", ".join(formatted)


def is_team_member(author_str):
    return any(member in author_str for member in TEAM_MEMBERS.keys())


# =========================
# VENUE NORMALIZATION
# =========================
def normalize_venue(entry):
    venue = entry.get("booktitle") or entry.get("journal") or ""

    if not venue:
        return "Unknown Venue"

    venue_lower = venue.lower()

    # Conference mapping
    if "aaai" in venue_lower:
        return "AAAI"
    if "cvpr" in venue_lower:
        return "CVPR"
    if "iccv" in venue_lower:
        return "ICCV"
    if "neurips" in venue_lower:
        return "NeurIPS"
    if "icml" in venue_lower:
        return "ICML"
    # if "ieee" in venue_lower:
    #    return "IEEE Journal"

    return venue


# =========================
# FORMAT ENTRY (PUBLICATION CARD)
# =========================
def format_entry(entry):
    title = entry.get("title", "No Title")
    author = format_authors(entry.get("author", ""))
    year = entry.get("year", "")
    venue = normalize_venue(entry)

    url = entry.get("url", "")
    pdf = entry.get("pdf", "")
    code = entry.get("code", "")

    # ===== links（用 · 分隔，更像 Scholar）=====
    links = []
    if pdf:
        links.append(f"[PDF]({pdf})")
    if code:
        links.append(f"[Code]({code})")
    if url:
        links.append(f"[Link]({url})")

    links_str = " · ".join(links)

    # ===== Scholar-style Markdown =====
    md = f"""**{title}**  
{author}  
*{venue} {year}*  
{links_str}
"""

    return {
        "title": title,
        "author": author,
        "year": year,
        "venue": venue,
        "md": md,
        "raw_author": entry.get("author", "")
    }


# =========================
# PUBLICATIONS PAGE GENERATION
# =========================
def generate_publications(entries):
    grouped = defaultdict(list)

    for e in entries:
        grouped[e["year"]].append(e)

    years = sorted(grouped.keys(), reverse=True)

    content = """---
layout: single
title: Publications
permalink: /publications/
---

# 近期发表部分论文

- 完整论文列表，请参见 [谷歌学术 →](https://scholar.google.com/citations?user=4ySzHlYAAAAJ&hl=en)

"""

    for year in years:
        content += f"\n## {year}\n\n"
        for e in grouped[year]:
            content += e["md"] + "\n"

    Path(PUB_OUTPUT).write_text(content, encoding="utf-8")


# =========================
# NEWS GENERATOR (CLI OUTPUT)
# =========================
def generate_news(entries):
    latest = sorted(entries, key=lambda x: x["year"], reverse=True)[0]

    title = latest["title"]
    year = latest["year"]
    venue = latest["venue"]

    news = f'- {year}: 📄 Paper accepted at {venue} — "{title}"'

    print("\n=== Suggested News Entry ===\n")
    print(news)
    print("\nCopy this into index.md under News section.\n")


# =========================
# OPTIONAL: HOME PAGE SNIPPET
# =========================
def generate_home_snippet(entries, top_n=5):
    sorted_entries = sorted(entries, key=lambda x: x["year"], reverse=True)

    snippet = "\n".join([e["md"] for e in sorted_entries[:top_n]])

    print("\n=== Suggested Homepage Publications Snippet ===\n")
    print(snippet)
    print("\n")


# =========================
# MAIN
# =========================
def main():
    raw_entries = load_bib(BIB_FILE)
    entries = [format_entry(e) for e in raw_entries]

    # Publications page
    generate_publications(entries)

    # CLI outputs
    generate_news(entries)
    generate_home_snippet(entries)


if __name__ == "__main__":
    main()

