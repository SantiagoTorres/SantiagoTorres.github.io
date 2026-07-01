#!/usr/bin/env python3
"""Fetch latest publications from Google Scholar and update _data/publications.yml.

Usage:
    python3 scripts/update_pubs.py [--dry-run]
    
Options:
    --dry-run    Show what would be changed but don't modify files
"""

import os
import sys
import re
import time
import difflib
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import yaml
import urllib.parse

# Configuration
SCHOLAR_USER_ID = "ByOx4-sAAAAJ"  # Santiago Torres-Arias
SCHOLAR_URL = f"https://scholar.google.com/citations?user={SCHOLAR_USER_ID}&hl=en&view_op=list_works&sortby=pubdate"
INPUT_YAML = "_data/publications.yml"
OUTPUT_DIFF = "scripts/publications_diff.txt"

# Heuristic: categorize venue keywords
JOURNAL_KEYWORDS = [
    "IEEE Security & Privacy", "NIST", "Journal of Computer Security",
    "IEEE Security & Privacy Magazine", "Springer", " ACM Transactions"
]
MAGAZINE_KEYWORDS = [
    "IEEE Security & Privacy Magazine", "IEEE Security & Privacy",
]
# Everything else becomes conference_papers

def fetch_scholar():
    """Fetch Google Scholar page with proper headers to avoid bot detection."""
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    resp = requests.get(SCHOLAR_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_scholar_entries(html):
    """Parse Google Scholar HTML to extract publication entries.
    
    Returns a list of dicts with keys: title, authors, venue, year
    """
    soup = BeautifulSoup(html, "html.parser")
    entries = []
    
    # Google Scholar groups articles in divs. On the sorted page, each article
    # block is typically a div containing the title link and venue/year info.
    # We look for divs that contain both a title link and publication info.
    article_blocks = soup.select("div.gs_r.gs_r_h gs_or gs_scl")
    if not article_blocks:
        # Fallback: try alternate class names
        article_blocks = soup.select("div.gs_r")
    if not article_blocks:
        # Another fallback - look for divs containing title + year patterns
        all_divs = soup.select("div")
        for d in all_divs:
            text = d.get_text()
            if re.search(r'\d{4}$|,\s*\d{4}\)', text) and d.select_one("a"):
                article_blocks = [d]
                break
    
    for block in article_blocks:
        # Extract title from the main link
        title_el = block.select_one("h3.gs_rt a, div.gs_rt a")
        if not title_el:
            title_el = block.select_one("a")
        title = title_el.text.strip() if title_el else None
        
        if not title:
            continue
        
        # Extract year - look for 4-digit year pattern
        year = None
        # Check the block text for year at the end
        full_text = block.get_text()
        year_match = re.search(r',?\s*(\d{4})\)', full_text) or re.search(r'(\d{4})$', full_text)
        if year_match:
            year = int(year_match.group(1))
        else:
            # Try from surrounding HTML
            for sibling in block.find_next_siblings():
                if re.search(r'\d{4}', sibling.get_text()):
                    yr = re.search(r'(\d{4})', sibling.get_text())
                    if yr and 2010 <= int(yr.group(1)) <= 2030:
                        year = int(yr.group(1))
                        break
        
        # Extract venue
        venue = None
        # Look for venue text in the block
        venue_match = re.search(r'\(([^)]+)\)\s*\d{4}|(\d+)th\s+([\w\s]+?)\s*\d{4}', block.get_text())
        if venue_match:
            venue = venue_match.group(1) or venue_match.group(3)
            venue = venue.strip()
        
        # Extract authors if visible on the page
        authors = None
        author_el = block.select_one("div.gs_a, div.gs_a a")
        if author_el:
            author_text = author_el.get_text()
            # Remove "Cited by X" and "[PDF]" parts
            author_text = re.sub(r'\[PDF\]', '', author_text)
            author_text = re.sub(r'\[HTML\]', '', author_text)
            author_text = re.sub(r'Cited by\s*\d+', '', author_text)
            # Remove year at the end
            author_text = re.sub(r',\s*\d{4}\s*$', '', author_text)
            if author_text:
                authors = author_text.strip()
        
        if title and year:
            entries.append({
                "title": title,
                "authors": authors,
                "venue": venue,
                "year": year,
            })
    
    return entries


def categorize_entry(entry):
    """Categorize entry into journal_papers, magazine_articles, or conference_papers."""
    venue = entry.get("venue", "").lower()
    title = entry.get("title", "").lower()
    
    for kw in MAGAZINE_KEYWORDS:
        if kw.lower() in venue:
            return "magazine_articles"
    
    for kw in JOURNAL_KEYWORDS:
        if kw.lower() in venue:
            return "journal_papers"
    
    # Default to conference papers
    return "conference_papers"


def load_existing_pubs():
    """Load existing publications from YAML."""
    with open(INPUT_YAML, "r") as f:
        return yaml.safe_load(f)


def get_pubs_by_title(pubs):
    """Create a dictionary of title -> entry for all pubs."""
    by_title = {}
    for category_name, entries in pubs.items():
        for entry in entries:
            # Normalize title for comparison
            normalized = re.sub(r'\s+', ' ', entry["title"].strip()).lower()
            by_title[normalized] = entry
    return by_title


def compare_pubs(existing_pubs, new_entries):
    """Compare new entries with existing pubs. Returns (new_list, updated_list)."""
    pubs_by_title = get_pubs_by_title(existing_pubs)
    
    new = []
    updated = []
    
    for entry in new_entries:
        normalized = re.sub(r'\s+', ' ', entry["title"].strip()).lower()
        if normalized in pubs_by_title:
            # Check if fields changed
            old = pubs_by_title[normalized]
            changed = any(entry.get(k) != old.get(k) for k in ["authors", "venue"])
            if changed:
                updated.append({"old": old, "new": entry})
        else:
            new.append(entry)
    
    return new, updated


def format_entry_yaml(entry):
    """Format a single entry for YAML output."""
    yaml_str = ""
    yaml_str += "- title: '{}'\n".format(repr(entry["title"]))
    if entry.get("authors"):
        yaml_str += "  authors: {}\n".format(repr(entry["authors"]))
    if entry.get("venue"):
        yaml_str += "  venue: {}\n".format(repr(entry["venue"]))
    yaml_str += "  year: {}\n".format(entry["year"])
    return yaml_str


def generate_diff_yaml(existing_pubs, new_entries):
    """Generate a YAML representation of new entries and updated entries."""
    output = []
    output.append("=== NEW ENTRIES ===")
    for entry in new_entries:
        output.append(format_entry_yaml(entry))
        output.append("---")
    
    return "\n".join(output)


def main():
    dry_run = "--dry-run" in sys.argv
    
    print("Fetching Google Scholar...")
    html = fetch_scholar()
    print(f"  Fetched {len(html)} bytes")
    
    print("Parsing entries...")
    new_entries = parse_scholar_entries(html)
    print(f"  Found {len(new_entries)} entries")
    
    for i, e in enumerate(new_entries[:5]):
        print(f"    {i+1}. {e['title'][:60]} ({e['year']})")
    
    if new_entries:
        print(f"    ... and {len(new_entries) - 5} more")
    
    print("Loading existing publications...")
    existing_pubs = load_existing_pubs()
    
    print("Comparing...")
    new, updated = compare_pubs(existing_pubs, new_entries)
    
    print(f"\nResults:")
    print(f"  New entries: {len(new)}")
    for e in new:
        cat = categorize_entry(e)
        print(f"    + [{cat}] {e['title'][:60]} ({e['year']})")
    
    print(f"  Updated entries: {len(updated)}")
    for u in updated:
        print(f"    ~ {u['new']['title'][:60]} ({u['new']['year']})")
    
    if not new and not updated:
        print("\nNo new or updated publications found. You're up to date!")
        return
    
    # Generate diff
    diff_text = generate_diff_yaml(existing_pubs, new)
    
    if dry_run:
        print(f"\n--- Would update {INPUT_YAML} with the following new YAML sections ---")
        print(diff_text)
    else:
        with open(OUTPUT_DIFF, "w") as f:
            f.write(diff_text)
        print(f"\nWrote diff to {OUTPUT_DIFF}")
        print("Review the diff (scripts/publications_diff.txt), then manually merge: ")
        print("python3 -c \"import yaml; yaml.safe_load(open('scripts/publications_diff.txt'))\"")
        
        # Show a compact diff of the existing YAML
        print("\n--- Existing YAML structure (for manual merge reference) ---")
        with open(INPUT_YAML, "r") as f:
            print(f.read())


if __name__ == "__main__":
    main()
