import json
import re
from pathlib import Path
from urllib.parse import quote

# =========================================
# IPEN ACADEMY — ARTICLE INDEX GENERATOR
# =========================================

ROOT = Path(__file__).resolve().parent.parent

ARTICLE_DIR = ROOT / "Artikel"
OUTPUT = ARTICLE_DIR / "articles.json"

articles = []


def parse_frontmatter(content):
    """
    Membaca metadata Markdown.
    Format metadata menggunakan YAML sederhana.
    """

    metadata = {}

    if not content.startswith("---"):
        return metadata, content

    match = re.match(
        r"\A---\s*\n(.*?)\n---\s*(?:\n|$)",
        content,
        re.DOTALL
    )

    if not match:
        return metadata, content

    frontmatter = match.group(1)

    for line in frontmatter.splitlines():

        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        key = key.strip().lower()
        value = value.strip()

        if len(value) >= 2:
            if value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]

        metadata[key] = value

    body = content[match.end():].strip()

    return metadata, body


def create_description(content):
    """
    Mengambil paragraf pertama sebagai deskripsi
    jika metadata description tidak tersedia.
    """

    text = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[#>*_`]", "", text)

    paragraphs = [
        paragraph.strip().replace("\n", " ")
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    if not paragraphs:
        return ""

    description = paragraphs[0]

    if len(description) > 200:
        description = description[:197] + "..."

    return description


# =========================================
# READ ARTICLES
# =========================================

if not ARTICLE_DIR.exists():
    raise FileNotFoundError(
        f"Folder artikel tidak ditemukan: {ARTICLE_DIR}"
    )


for file in sorted(ARTICLE_DIR.rglob("*.md")):

    # Jangan membaca file Markdown tersembunyi.
    if any(part.startswith(".") for part in file.relative_to(ARTICLE_DIR).parts):
        continue

    content = file.read_text(encoding="utf-8")

    metadata, body = parse_frontmatter(content)

    title = metadata.get(
        "title",
        file.stem.replace("-", " ").replace("_", " ").title()
    )

    description = metadata.get(
        "description",
        create_description(body)
    )

    category = metadata.get("category", "Artikel")

    author = metadata.get("author", "IPEN Academy")

    date = metadata.get("date", "")

    relative_path = file.relative_to(ARTICLE_DIR).as_posix()

    encoded_path = quote(relative_path, safe="/")

    article_url = (
        "/Artikel/baca.html?file=" + encoded_path
    )

    articles.append({
        "title": title,
        "description": description,
        "category": category,
        "author": author,
        "date": date,
        "url": article_url
    })


# =========================================
# SORT ARTICLES
# =========================================

articles.sort(
    key=lambda article: article.get("date", ""),
    reverse=True
)


# =========================================
# GENERATE JSON
# =========================================

OUTPUT.write_text(
    json.dumps(
        articles,
        ensure_ascii=False,
        indent=4
    ),
    encoding="utf-8"
)


print("=================================")
print("IPEN ACADEMY ARTICLE GENERATOR")
print("=================================")
print(f"Jumlah artikel: {len(articles)}")
print(f"Output: {OUTPUT}")
print("Status: Berhasil")
print("=================================")
