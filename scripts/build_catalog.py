"""Refresh the static catalog in src/index.html using only the standard library."""

from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote


SRC = Path(__file__).resolve().parents[1] / "src"
CATEGORY_NAMES = {"ai-dev": "AI Dev", "games": "Игры", "react": "React"}
PAGE_DETAILS = {
    "games/aion2-checklist.html": (
        "Aion 2 — Журнал даэва",
        "Чек-лист на день и неделю, заметки и тактики для ближнего боя.",
    ),
    "games/aion2-global-guide.html": (
        "Aion 2 — от 45 уровня до 2800 GS",
        "Маршрут развития персонажа, приоритеты и расход ресурсов в Global.",
    ),
    "react/react_fiber_visualizer.html": (
        "Как работает React Fiber",
        "Пошаговый разбор обновления списка, от setState до изменений в DOM.",
    ),
}


class PageHead(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title_parts = []
        self.description = ""
        self.in_title = False
        self.finished = False

    def handle_starttag(self, tag, attrs):
        if self.finished:
            return
        if tag == "body":
            self.finished = True
        elif tag == "title":
            self.in_title = True
        elif tag == "meta":
            attributes = dict(attrs)
            if (attributes.get("name") or "").lower() == "description":
                self.description = attributes.get("content") or ""

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "head":
            self.finished = True

    def handle_data(self, data):
        if self.in_title and not self.finished:
            self.title_parts.append(data)


def visible(path):
    return not path.name.startswith((".", "_"))


def display_name(slug):
    return slug.replace("-", " ").replace("_", " ").strip().capitalize() or slug


def pages(directory, *, category_root=False):
    entry = directory / "index.html"
    if not category_root and entry.is_file():
        yield entry
        return
    for child in sorted(directory.iterdir(), key=lambda path: (path.name.casefold(), path.name)):
        if not visible(child):
            continue
        if child.is_dir():
            yield from pages(child)
        elif child.suffix.lower() == ".html":
            yield child


def details(page, relative):
    if relative in PAGE_DETAILS:
        return PAGE_DETAILS[relative]
    parser = PageHead()
    with page.open(encoding="utf-8-sig") as source:
        for line in source:
            parser.feed(line)
            if parser.finished:
                break
    parser.close()
    fallback = page.parent.name if page.name == "index.html" else page.stem
    title = " ".join("".join(parser.title_parts).split()) or display_name(fallback)
    return title, " ".join(parser.description.split())


def render_categories():
    lines = []
    for category in sorted(SRC.iterdir(), key=lambda path: (path.name != "react", path.name.casefold(), path.name)):
        if not category.is_dir() or not visible(category):
            continue
        entries = list(pages(category, category_root=True))
        if not entries:
            continue
        label = CATEGORY_NAMES.get(category.name, display_name(category.name))
        slug = escape(category.name)
        lines.extend([
            f'        <section class="category" data-category="{slug}">',
            f'          <h2>{escape(label)}</h2>',
            '          <ul class="entries">',
        ])
        for page in entries:
            relative = page.relative_to(SRC).as_posix()
            title, description = details(page, relative)
            url = quote(relative.removesuffix("index.html") if page.name == "index.html" else relative)
            lines.extend([
                '            <li>',
                f'              <a class="entry" href="./{url}">',
                '                <span class="entry-copy">',
                f'                  <strong>{escape(title)}</strong>',
            ])
            if description:
                lines.append(f'                  <span class="description">{escape(description)}</span>')
            lines.extend([
                '                </span>',
                '                <span class="arrow" aria-hidden="true">↗</span>',
                '              </a>',
                '            </li>',
            ])
        lines.extend(['          </ul>', '        </section>'])
    return "\n".join(lines) or '        <p class="empty">Каталог пока пуст.</p>'


def main():
    index = SRC / "index.html"
    source = index.read_text(encoding="utf-8")
    start, end = "<!-- catalog:start -->", "<!-- catalog:end -->"
    if source.count(start) != 1 or source.count(end) != 1 or source.index(start) > source.index(end):
        raise SystemExit("Expected one ordered pair of catalog markers in src/index.html")
    before = source.split(start, 1)[0]
    after = source.split(end, 1)[1]
    updated = f"{before}{start}\n{render_categories()}\n{end}{after}"
    if source != updated:
        index.write_text(updated, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
