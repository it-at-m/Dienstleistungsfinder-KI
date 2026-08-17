import fs from "node:fs/promises";
import { generateLoaderJs } from "./lib/fileGenerator.js";
import path from "node:path";

const manifestUrl = new URL("../dist/src/.vite/manifest.json", import.meta.url);
const distDir = new URL("../dist/", import.meta.url);

const MDE_STYLESHEET_URL =
  "https://assets.muenchen.de/mde/1.1.19/css/style.css";
const LOCAL_MDE_STYLESHEET_RELATIVE_PATH = "assets/mde-style.css";

async function loadManifest() {
  try {
    const raw = await fs.readFile(manifestUrl, "utf8");
    return JSON.parse(raw);
  } catch (error) {
    console.error("Unable to load Vite manifest", error);
    process.exit(1);
  }
}

async function generateWebcomponentLoader(manifest) {
  /**
   * Why this?
   *
   * When we build our custom web component, Vite automatically adds a
   * cache-busting mechanic to our minified JS file.
   *
   * Cache-busting ensures users get the newest version of a file, regardless
   * of browser/server/CDN caching.
   *
   * Since we use a web component, we generate a stable loader file that imports
   * the hashed entry file from the manifest.
   */

  const REQUIRED_PREFIX = "src/";
  const REQUIRED_SUFFIX = "-webcomponent.ts";

  for (const key in manifest) {
    if (key.startsWith(REQUIRED_PREFIX) && key.endsWith(REQUIRED_SUFFIX)) {
      const entrypoint = manifest[key].file;
      const fileName = path.basename(key, path.extname(key));
      const dirName = path.dirname(key);
      generateLoaderJs(entrypoint, dirName, fileName);
    }
  }
}

async function fileExists(url) {
  try {
    await fs.access(url);
    return true;
  } catch {
    return false;
  }
}

async function ensureMdeStylesheet() {
  const outputUrl = new URL(LOCAL_MDE_STYLESHEET_RELATIVE_PATH, distDir);
  const outputDirUrl = new URL("./assets/", distDir);

  console.log("=== MDE stylesheet check ===");
  console.log("Target path:", outputUrl.pathname);

  if (await fileExists(outputUrl)) {
    console.log(
      `Using existing MDE stylesheet at dist/${LOCAL_MDE_STYLESHEET_RELATIVE_PATH}`
    );

    const stat = await fs.stat(outputUrl);
    console.log("Existing file size:", stat.size, "bytes");

    const preview = await fs.readFile(outputUrl, "utf8");
    console.log("Preview (first 200 chars):");
    console.log(preview.slice(0, 200));

    return;
  }

  console.log("MDE stylesheet not found locally, attempting download...");
  console.log("Download URL:", MDE_STYLESHEET_URL);

  try {
    await fs.mkdir(outputDirUrl, { recursive: true });

    console.log("Directory ensured:", outputDirUrl.pathname);

    const response = await fetch(MDE_STYLESHEET_URL);

    console.log("HTTP response status:", response.status, response.statusText);

    if (!response.ok) {
      throw new Error(
        `HTTP ${response.status} ${response.statusText} while downloading ${MDE_STYLESHEET_URL}`
      );
    }

    const css = await response.text();

    console.log("Downloaded size:", css.length, "chars");

    await fs.writeFile(outputUrl, css, "utf8");

    console.log(
      `Downloaded MDE stylesheet to dist/${LOCAL_MDE_STYLESHEET_RELATIVE_PATH}`
    );

    console.log("Preview (first 200 chars):");
    console.log(css.slice(0, 200));
  } catch (error) {
    console.error("=== MDE stylesheet ERROR ===");
    console.error(
      `Unable to provide MDE stylesheet at dist/${LOCAL_MDE_STYLESHEET_RELATIVE_PATH}`
    );
    console.error("Error details:", error);

    console.error("Environment:");
    console.error("HTTP_PROXY:", process.env.HTTP_PROXY);
    console.error("HTTPS_PROXY:", process.env.HTTPS_PROXY);

    process.exit(1);
  }
}

async function generateIndexHtml() {
  const indexUrl = new URL("index.html", distDir);
  const html = `<!doctype html>
<html lang="de">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="icon" href="/src/favicon.ico" />
    <link rel="stylesheet" href="/assets/mde-style.css" />
    <title>Dienstleistungsfinder</title>
    <script type="module" src="/loader.js"></script>
  </head>
  <body style="margin: 0; padding: 0">
    <noscript>
      <strong>JavaScript muss aktiviert sein, um diese Anwendung zu verwenden.</strong>
    </noscript>
    <dlf-search-webcomponent></dlf-search-webcomponent>
  </body>
</html>
`;

  await fs.writeFile(indexUrl, html, "utf8");
}

async function main() {
  const manifest = await loadManifest();
  await generateWebcomponentLoader(manifest);
  await ensureMdeStylesheet();
  await generateIndexHtml();
}

await main();
