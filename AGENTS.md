# AI Visual

Сайт на GitHub Pages состоит из статического указателя в `src/index.html` и самостоятельных приложений в папках категорий. Для новых страниц используй HTML, CSS и JavaScript без фреймворков. Ссылки и пути к локальным ресурсам должны работать под префиксом репозитория `/ai-visual/`.

- Для добавления страниц используй проектный скилл [`$add-visualization-page`](.agents/skills/add-visualization-page/SKILL.md).
- Список между маркерами `catalog:start` и `catalog:end` в `src/index.html` обновляет `python scripts/build_catalog.py`. При изменении состава каталога запусти генератор и проверь diff. Главная оформлена как тёмный указатель, категория React идёт первой.
- Для локального просмотра из корня проекта запусти `python -m http.server 8000 --directory src` и открой `http://localhost:8000/`.
- Workflow в `.github/workflows/pages.yml` публикует `src` после push в `main`. Перед коммитом проверь автора и коммитера через `git var GIT_AUTHOR_IDENT` и `git var GIT_COMMITTER_IDENT`. Для этого репозитория используй имя и email аккаунта `itsanti`.
