"""
check_skills.py — detect updates to mattpocock/skills and Matt's YouTube channel,
report what changed against the last verified snapshot, and recommend exact
next commands. No auto-execute, no auto-tutorial-edits — you keep judgment.

Usage:
    py check_skills.py             # detect + report + recommend
    py check_skills.py --refresh   # also: write new snapshot + rewrite colophon

Snapshot lives in skills_snapshot.json (per-skill blob SHA + recent video IDs).
The verified line in index.html lives between a <p data-verified-line> tag
which the script rewrites on --refresh.

Stdlib only — no pip deps. GitHub API public endpoints (60 req/hr unauth, plenty
for a once-a-week check); YouTube channel via public RSS feed (no auth needed).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 stdout so the ✓/✗/· glyphs render on Windows cp1252 consoles.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# defusedxml protects against XXE + billion-laughs in YouTube's RSS feed.
# stdlib xml.etree.ElementTree is explicitly flagged as unsafe for untrusted XML.
try:
    from defusedxml.ElementTree import fromstring as _xml_fromstring
except ImportError:
    sys.exit(
        "defusedxml is required for safe RSS parsing.\n"
        "Install with: py -m pip install defusedxml\n"
        "(Python's stdlib XML parsers are vulnerable to XXE / billion-laughs attacks.)"
    )

# ---- config ----
REPO            = "mattpocock/skills"
BRANCH          = "main"
CHANNEL_ID      = "UCswG6FSbgZjbWtdf_hMLaow"  # Matt Pocock — derived from his /@mattpocockuk URL
SNAPSHOT_PATH   = Path("skills_snapshot.json")
INDEX_PATH      = Path("index.html")
VIDEOS_TO_TRACK = 30
USER_AGENT      = "skill-update-checker/1.0 (+https://github.com/mattpocock/skills)"


# ---- HTTP helpers (stdlib) ----

def _get(url: str, accept: str = "application/json") -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"  ✗ HTTP {e.code} fetching {url}: {e.reason}")
    except urllib.error.URLError as e:
        sys.exit(f"  ✗ network error fetching {url}: {e.reason}")


def fetch_repo_state(repo: str, branch: str) -> tuple[str, dict[str, str]]:
    """
    Returns (commit_sha, {file_path: blob_sha}) for every *.md file under skills/.
    Uses GitHub's recursive Git Trees API — one request after the branch lookup.
    """
    branch_data = json.loads(_get(f"https://api.github.com/repos/{repo}/branches/{branch}"))
    commit_sha = branch_data["commit"]["sha"]

    tree_data = json.loads(_get(
        f"https://api.github.com/repos/{repo}/git/trees/{commit_sha}?recursive=1"
    ))
    if tree_data.get("truncated"):
        print("  ! GitHub tree response was truncated; some skill files may be missing")

    skill_files: dict[str, str] = {}
    for item in tree_data.get("tree", []):
        path = item.get("path", "")
        if (path.startswith("skills/") and path.endswith(".md")
                and item.get("type") == "blob"):
            skill_files[path] = item["sha"]
    return commit_sha, skill_files


def fetch_youtube_videos(channel_id: str, n: int) -> list[dict]:
    """Public RSS feed; no auth. Returns recent N videos with id/title/published."""
    xml_bytes = _get(
        f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}",
        accept="application/atom+xml",
    )
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "yt":   "http://www.youtube.com/xml/schemas/2015",
    }
    root = _xml_fromstring(xml_bytes)
    videos: list[dict] = []
    for entry in root.findall("atom:entry", ns)[:n]:
        vid_el   = entry.find("yt:videoId", ns)
        title_el = entry.find("atom:title", ns)
        pub_el   = entry.find("atom:published", ns)
        if vid_el is not None and title_el is not None:
            videos.append({
                "id":        vid_el.text,
                "title":     (title_el.text or "").strip(),
                "published": (pub_el.text[:10] if pub_el is not None and pub_el.text else None),
            })
    return videos


# ---- snapshot I/O ----

def load_snapshot() -> dict | None:
    if not SNAPSHOT_PATH.exists():
        return None
    try:
        return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  ! could not parse {SNAPSHOT_PATH}: {e!r} — treating as no snapshot")
        return None


def write_snapshot(snapshot: dict) -> None:
    SNAPSHOT_PATH.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")


# ---- diff logic ----

def diff_skills(old: dict[str, str], new: dict[str, str]) -> tuple[list, list, list]:
    old_keys, new_keys = set(old), set(new)
    added   = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    changed = sorted(p for p in (old_keys & new_keys) if old[p] != new[p])
    return added, removed, changed


def diff_videos(old: list[dict], new: list[dict]) -> list[dict]:
    seen = {v["id"] for v in old}
    return [v for v in new if v["id"] not in seen]


def slug_from_path(path: str) -> str | None:
    """
    'skills/engineering/grill-with-docs/SKILL.md' → 'grill-with-docs'.
    Returns None if the path doesn't fit the expected layout.
    """
    parts = path.split("/")
    return parts[-2] if len(parts) >= 3 else None


def grep_index_for_slugs(slugs: list[str]) -> dict[str, list[int]]:
    """For each slug, return line numbers in index.html that mention /slug."""
    if not INDEX_PATH.exists():
        return {}
    lines = INDEX_PATH.read_text(encoding="utf-8").splitlines()
    hits: dict[str, list[int]] = {}
    for slug in slugs:
        if not slug:
            continue
        needle = "/" + slug
        for i, line in enumerate(lines, 1):
            if needle in line:
                hits.setdefault(slug, []).append(i)
    return hits


# ---- colophon refresh ----

VERIFIED_LINE_RX = re.compile(
    r'(<p[^>]*\bdata-verified-line\b[^>]*>)(.*?)(</p>)',
    re.DOTALL,
)


def corpus_video_count() -> int:
    """
    Count videos in the curated corpus by reading videos.md (the source of truth
    for what's been researched). Snapshot.videos counts the RSS feed (Matt's
    last 15 uploads, regardless of whether we've ingested them) — different
    number, different meaning.
    """
    p = Path("videos.md")
    if not p.exists():
        return 0
    return len(re.findall(r'^### \d+\.', p.read_text(encoding="utf-8"), re.MULTILINE))


def build_verified_html(snapshot: dict) -> str:
    short  = snapshot["repo_commit"][:7]
    n      = corpus_video_count() or len(snapshot["videos"])
    date   = snapshot["verified_at"][:10]
    return (
        f'verified against <em>mattpocock/skills</em> @ '
        f'<a href="https://github.com/{REPO}/tree/{snapshot["repo_commit"]}" '
        f'target="_blank" rel="noopener"><code>{short}</code></a> '
        f'&middot; {n} videos &middot; last checked {date}'
    )


def refresh_colophon(snapshot: dict) -> None:
    if not INDEX_PATH.exists():
        print("  ! index.html not found — skipping colophon update")
        return
    text  = INDEX_PATH.read_text(encoding="utf-8")
    inner = build_verified_html(snapshot)
    m     = VERIFIED_LINE_RX.search(text)
    if not m:
        print("  ! could not find <p data-verified-line> in index.html — add it manually first")
        return
    new_text = text[:m.start(2)] + inner + text[m.end(2):]
    INDEX_PATH.write_text(new_text, encoding="utf-8")
    # The HTML uses corpus count (videos.md), not the RSS snapshot — match that in the log.
    rendered_count = corpus_video_count() or len(snapshot["videos"])
    print(f"  ✓ rewrote colophon verification line: {snapshot['repo_commit'][:7]}, "
          f"{rendered_count} videos (corpus), {snapshot['verified_at'][:10]}")


# ---- recommendation engine ----

def render_recommendations(
    old: dict, repo_commit: str, changed: list[str], added: list[str],
    removed: list[str], new_videos: list[dict],
) -> None:
    print()
    print("  Recommended next steps:")
    n = 1

    if changed or added or removed:
        old_short = old["repo_commit"][:7]
        new_short = repo_commit[:7]
        print(f"  {n}. Inspect the raw skill diff in GitHub:")
        print(f"       https://github.com/{REPO}/compare/{old_short}...{new_short}")
        n += 1

    if new_videos:
        print(f"  {n}. Add these video(s) to VIDEOS in build_notebook.py:")
        for v in new_videos:
            safe_title = v["title"].replace('"', '\\"')
            print(f'       ("https://www.youtube.com/watch?v={v["id"]}", "{safe_title}"),')
        n += 1

    affected_slugs = [slug_from_path(p) for p in (changed + added + removed)]
    affected_slugs = [s for s in affected_slugs if s]
    if affected_slugs or new_videos:
        print(f"  {n}. Add per-change questions to QUESTIONS in build_notebook.py")
        print(f"     (timestamped keys preserve history across re-checks):")
        date_tag = datetime.now(timezone.utc).strftime("%Y-%m")
        for slug in affected_slugs:
            print(f'       ("{slug}-update-{date_tag}",')
            print(f'        "What changed in /{slug} since the previous verification? '
                  f'Quote any new or removed instructions Matt added."),')
        for v in new_videos:
            key = re.sub(r"[^a-z0-9]+", "-", v["title"].lower()).strip("-")[:40]
            print(f'       ("{key}-{date_tag}",')
            print(f'        "Summarize the central new claim Matt makes in this video '
                  f'that the previous corpus did not cover. Quote where possible."),')
        n += 1

    if affected_slugs or new_videos:
        print(f"  {n}. Re-run the idempotent driver — only new questions will fire:")
        print(f"       py build_notebook.py")
        n += 1

    if affected_slugs:
        hits = grep_index_for_slugs(affected_slugs)
        if hits:
            print(f"  {n}. Tutorial sections that reference affected skills (manually review):")
            for slug, lines in hits.items():
                preview = ", ".join(str(x) for x in lines[:8])
                more    = f" (+{len(lines)-8} more)" if len(lines) > 8 else ""
                print(f"       /{slug}: index.html lines {preview}{more}")
            n += 1

    print(f"  {n}. After integration, refresh the snapshot + colophon:")
    print(f"       py check_skills.py --refresh")


# ---- main ----

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check for mattpocock/skills + YouTube channel updates")
    parser.add_argument("--refresh", action="store_true",
                        help="write new snapshot + rewrite colophon verification line")
    args = parser.parse_args(argv)

    now = datetime.now(timezone.utc)
    print(f"[{now.isoformat(timespec='seconds')}] check_skills.py")

    print("  fetching mattpocock/skills tree...")
    repo_commit, current_skills = fetch_repo_state(REPO, BRANCH)
    print(f"    commit {repo_commit[:7]} · {len(current_skills)} skill files under skills/")

    print("  fetching YouTube channel RSS...")
    current_videos = fetch_youtube_videos(CHANNEL_ID, VIDEOS_TO_TRACK)
    print(f"    {len(current_videos)} recent videos")

    old = load_snapshot()

    print()
    print("=" * 72)
    if old is None:
        print("  BASELINE SNAPSHOT — no prior state to diff against")
        print(f"  Capturing current state: {len(current_skills)} skills, {len(current_videos)} videos")
    else:
        last_checked = old.get("verified_at", "unknown")[:10]
        print(f"  Last verified: {last_checked} ({(now - datetime.fromisoformat(old['verified_at'])).days} days ago)")

        added,   removed, changed = diff_skills(old.get("skills", {}), current_skills)
        new_vids                  = diff_videos(old.get("videos", []), current_videos)

        if not (added or removed or changed or new_vids):
            print()
            print("  NO CHANGES — tutorial is current against the snapshot")
        else:
            print()
            if added:
                print(f"  ADDED   ({len(added)}):")
                for p in added: print(f"    + {p}")
            if removed:
                print(f"  REMOVED ({len(removed)}):")
                for p in removed: print(f"    - {p}")
            if changed:
                print(f"  CHANGED ({len(changed)}):")
                for p in changed: print(f"    ~ {p}")
            if new_vids:
                print(f"  NEW VIDEOS ({len(new_vids)}):")
                for v in new_vids:
                    print(f"    + [{v['id']}] {v['title']}  ({v['published']})")

            render_recommendations(old, repo_commit, changed, added, removed, new_vids)

    print("=" * 72)

    # Refresh path: write new snapshot + update colophon
    if args.refresh or old is None:
        snapshot = {
            "verified_at": now.isoformat(timespec="seconds"),
            "repo_commit": repo_commit,
            "skills":      current_skills,
            "videos":      current_videos,
        }
        write_snapshot(snapshot)
        print(f"\n  ✓ snapshot written: {SNAPSHOT_PATH}")
        refresh_colophon(snapshot)
    else:
        print("\n  (no snapshot change — pass --refresh after integrating findings)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
