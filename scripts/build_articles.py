import json
import re
from pathlib import Path
from urllib.parse import quote

# Lokasi utama repositori
ROOT = Path(__file__).resolve().parent.parent

# Folder artikel
ARTICLE_DIR = ROOT / "Artikel"

# File indeks artikel
OUTPUT_FILE = ARTICLE_DIR / "articles.json"


def read_frontmatter(content):
    """
    Membaca metadata sederhana dari Markdown.
    Contoh:
    ---
    title: Judul Artikel
    author: Nama Penulis
    date: 2026-11-04
    description: Deskripsi artikel
    ---
    """

    metadata = {}

    if not content.startswith("---"):
        return metadata

    parts = content.split("---", 2)

    if len(parts) < 3:
        return metadata

    for line in parts[1].strip().splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        metadata[key.strip().lower()] = value.strip().strip('"').strip("'")

    return metadata


def extract_description(content):
    """
    Mengambil paragraf pertama sebagai deskripsi.
    """

    content = re.sub(
        r"\A---.*?---",
        "",
        content,
        flags=re.DOTALL
    )

    for line in content.splitlines():

        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        return line[:250]

    return "Baca artikel selengkapnya di IPEN Academy."


def build_articles():

    articles = []

    if not ARTICLE_DIR.exists():
        print("Folder Artikel tidak ditemukan.")
        return

    for file in ARTICLE_DIR.rglob("*.md"):

        # Jangan membaca Markdown di folder baca
        if "baca" in file.relative_to(ARTICLE_DIR).parts:
            continue

        content = file.read_text(encoding="utf-8")

        metadata = read_frontmatter(content)

        relative_path = file.relative_to(ARTICLE_DIR).as_posix()

        title = metadata.get(
            "title",
            file.stem.replace("-", " ").title()
        )

        author = metadata.get(
            "author",
            "IPEN Academy"
        )

        date = metadata.get(
            "date",
            ""
        )

        description = metadata.get(
            "description",
            extract_description(content)
        )

        article = {
            "title": title,
            "author": author,
            "date": date,
            "description": description,
            "file": relative_path,
            "url": "/Artikel/baca/?file=" + quote(relative_path, safe="/")
        }

        articles.append(article)

    # Urutkan berdasarkan tanggal terbaru
    articles.sort(
        key=lambda item: item["date"],
        reverse=True
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            articles,
            ensure_ascii=False,
            indent=4
        ),
        encoding="utf-8"
    )

    print(f"Berhasil membuat indeks {len(articles)} artikel.")


if __name__ == "__main__":
    build_articles()
