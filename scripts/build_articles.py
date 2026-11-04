import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTICLE_DIR = ROOT / "Artikel"
OUTPUT = ARTICLE_DIR / “articles.json”

articles = []

for file in sorted(ARTICLE_DIR.glob(”*.md”)):

content = file.read_text(encoding="utf-8")
metadata = {}
# Membaca metadata di bagian awal Markdown
if content.startswith("---"):
    parts = content.split("---", 2)
    if len(parts) == 3:
        for line in parts[1].strip().splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip().lower()] = value.strip().strip('"').strip("'")
        content = parts[2].strip()
title = metadata.get("title", file.stem.replace("-", " ").title())
description = metadata.get("description", "")
category = metadata.get("category", "Artikel")
author = metadata.get("author", "IPEN Academy")
date = metadata.get("date", "")
articles.append({
    "title": title,
    "description": description,
    "category": category,
    "author": author,
    "date": date,
    "url": f"/Artikel/baca.html?file={file.name}"
})

OUTPUT.write_text(
json.dumps(articles, ensure_ascii=False, indent=4),
encoding=“utf-8”
)

print(f”Berhasil membuat indeks: {len(articles)} artikel.”)
