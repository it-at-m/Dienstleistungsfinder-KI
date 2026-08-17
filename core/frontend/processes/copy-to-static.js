import fs from "node:fs/promises";

const sourcePath = new URL("../dist/", import.meta.url);
const destinationPath = new URL("../../backend/static/", import.meta.url);

await fs.rm(destinationPath, { recursive: true, force: true });
await fs.cp(sourcePath, destinationPath, { recursive: true });
