## DLF Frontend

Builds a custom webcomponent that can be used. Build with:

- [V7ue.js](https://vuejs.org/)
- [Refarch-Webcomponent-Starter](https://github.com/it-at-m/refarch-templates/tree/main/refarch-webcomponent)
- [Muc-Patternlab als Komponentenlibrary](https://it-at-m.github.io/muc-patternlab-vue/)

## Installation

Installation of dependencies

```
npm install
```

Compilation and Hot-Reloading for development

```shell
npm run dev
```

The Vite development server runs at `http://localhost:8082/`. It serves the
frontend only; API requests still require the backend.

Compilation and minification for production

```shell
npm run build
```

To build the frontend into the backend's static directory and serve the complete
application on port 8080:

```shell
npm run buildlocal
cd ../backend
uv run python app.py
```

Alternatively, from the repository root, build and run the complete core image:

```shell
docker compose up --build core
```

If `http://localhost:8080/` displays "Build the frontend or run the core
container", the backend is serving its source-tree placeholder. Run one of the
complete-application workflows above.

Linting of source code files (ESLint and Prettier)

```shell
npm run lint
```

Automatic fixing of source code files (Linting and formatting)

```shell
npm run fix
```

Customization of configuration

See [Configuration Reference](https://vitejs.dev/config/).

# Usage

1. Add Import to page:
   `<script src="pathtoloader/loader.js" type="module"></script>`
2. Add Element to page

```html
<dlf-search-webcomponent></dlf-search-webcomponent>
```
