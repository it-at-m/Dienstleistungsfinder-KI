import { pathToFileURL } from "url";

import { JSDOM } from "jsdom";

async function main() {
  const dom = new JSDOM(
    "<!DOCTYPE html><body><dlf-search-webcomponent></dlf-search-webcomponent></body>",
    { pretendToBeVisual: true }
  );

  const { window } = dom;
  globalThis.window = window;
  globalThis.document = window.document;
  globalThis.HTMLElement = window.HTMLElement;
  globalThis.customElements = window.customElements;
  globalThis.Node = window.Node;
  globalThis.navigator = window.navigator;
  globalThis.AbortController = window.AbortController;
  globalThis.fetch = async (url) => {
    const text = url.toString();
    if (text.includes("categories")) {
      return { ok: true, json: async () => ["Cat A", "Cat B"], status: 200 };
    }
    if (text.includes("keywords")) {
      return { ok: true, json: async () => ["Key A", "Key B"], status: 200 };
    }
    return {
      ok: true,
      json: async () => ({
        examples: [],
        feedback: { positive: {}, negative: {} },
        scrubber_enabled: false,
      }),
      status: 200,
    };
  };

  await import(
    pathToFileURL("../dist/src/entry-dlf-search-webcomponent-DcCeTQ5l.js")
  );
  await new Promise((resolve) => setTimeout(resolve, 0));

  const el = window.document.querySelector("dlf-search-webcomponent");
  console.log("shadow root:", !!el?.shadowRoot);
  const toggle = el?.shadowRoot?.querySelector(".advanced-toggle");
  toggle?.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  await new Promise((resolve) => setTimeout(resolve, 0));

  const groups = Array.from(
    el?.shadowRoot?.querySelectorAll(".filter-group") ?? []
  ).map((node) => node.querySelector("label")?.textContent?.trim());
  console.log("filter groups:", groups);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
