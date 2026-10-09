import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent

ARTICLES_DIR = ROOT / "Artikel" / "artikel"
ARTICLES_INDEX = ROOT / "Artikel" / "articles.json"

FILES_DIR = ROOT / "Berkas"
FILES_INDEX = ROOT / "Berkas" / "files.json"

FILE_CATEGORIES = {
    "Buku": "Buku",
    "Jurnal": "Jurnal",
    "Materi": "Materi",
}

ALLOWED_FILE_EXTENSIONS = {
    ".pdf",
    ".epub",
    ".txt",
    ".doc",
    ".docx",
    ".odt",
    ".rtf",
}


def make_title(filename):
    stem = Path(filename).stem

    stem = re.sub(r"[-_]+", " ", stem)
    stem = re.sub(r"\s+", " ", stem)

    return stem.strip().title()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ) + "\n",
        encoding="utf-8"
    )


def read_frontmatter(text):
    metadata = {}

    if not text.startswith("---"):
        return metadata

    parts = text.split("---", 2)

    if len(parts) < 3:
        return metadata

    for line in parts[1].splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        metadata[key.strip().lower()] = value.strip().strip(
            "\"'"
        )

    return metadata


def build_articles():
    articles = []

    if ARTICLES_DIR.exists():
        for path in sorted(ARTICLES_DIR.rglob("*")):
            if not path.is_file():
                continue

            if path.suffix.lower() != ".md":
                continue

            relative_path = path.relative_to(ROOT).as_posix()

            text = path.read_text(encoding="utf-8")
            metadata = read_frontmatter(text)

            title = metadata.get("title") or make_title(path.name)

            category = metadata.get("category", "Artikel")
            description = metadata.get("description", "")

            # Markdown mentah tidak ditayangkan sebagai halaman
            # tersendiri. Halaman pembaca akan mengambilnya.
            encoded_path = quote(relative_path, safe="/")

            articles.append({
                "title": title,
                "category": category,
                "description": description,
                "url": "/baca/?file=" + quote(
                    relative_path,
                    safe=""
                ),
                "source": "/" + encoded_path,
            })

    write_json(ARTICLES_INDEX, articles)

    print(f"Artikel ditemukan: {len(articles)}")


def build_files():
    files = []

    for folder_name, category in FILE_CATEGORIES.items():
        category_dir = FILES_DIR / folder_name

        if not category_dir.exists():
            continue

        for path in sorted(category_dir.rglob("*")):
            if not path.is_file():
                continue

            if path.suffix.lower() not in ALLOWED_FILE_EXTENSIONS:
                continue

            relative_path = path.relative_to(ROOT).as_posix()
            encoded_path = quote(relative_path, safe="/")

            files.append({
                "title": make_title(path.name),
                "filename": path.name,
                "category": category,
                "extension": path.suffix[1:].upper(),
                "url": "/" + encoded_path,
            })

    files.sort(
        key=lambda item: (
            item["category"].lower(),
            item["title"].lower()
        )
    )

    write_json(FILES_INDEX, files)

    print(f"Berkas ditemukan: {len(files)}")


def main():
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

    for folder_name in FILE_CATEGORIES:
        (FILES_DIR / folder_name).mkdir(
            parents=True,
            exist_ok=True
        )

    build_articles()
    build_files()


if __name__ == "__main__":
    main()
