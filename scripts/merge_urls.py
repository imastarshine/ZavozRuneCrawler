import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import src.parser
import src.database


def dedupe(db, urls):
    groups = {}
    for url in urls:
        canonical = src.parser.normalize_url(url)
        groups.setdefault(canonical, set()).add(url)
    for canonical, variants in sorted(groups.items()):
        if len(variants) <= 1:
            continue
        print(f"merging {len(variants)} variants into {canonical}: {sorted(variants)}")
        for variant in sorted(variants):
            if variant != canonical:
                db.merge_url(variant, canonical)


def main():
    dedupe(src.database.linkdb, src.database.linkdb.get_links().keys())
    dedupe(src.database.contentdb, src.database.contentdb.get_urls())


if __name__ == "__main__":
    main()
