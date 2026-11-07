#!/usr/bin/env node
import { createHash } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const EXPECTED_VERSION = "0.2.52";
const EXPECTED_FILES = {
  "dist/utils/mcp-ui-ab-test.js": "978c72e71812e555f6e90cf107d936be5777f60f2e2658109af92513a2a06a42",
  "dist/ui/resources.js": "7d4bd8fc68b75333176d4dc8363b92323fc63d19334cc6727d8348d56b1879ee",
};
const EXPECTED_CONTEXT_FILES = {
  "dist/server.js": "dacffa416d0a46351aa553e6b05e51a10638bd190821eda03032de045b9f2aaf",
  "dist/ui/contracts.js": "47559cdf2b1e806dbda0cef8d7e9eda4a42b3b32df0ce10b418b3ca37c501bad",
  "dist/index.js": "a4145198dc75cd34e7c7452c2054b4cc0d29e199ae1459961a17e4da25a13500",
};
const packageRoot = process.argv[2];
if (!packageRoot) {
  throw new Error("Usage: node apply-mcp-ui-headless.mjs <desktop-commander-package-root>");
}
const root = resolve(packageRoot);
const packageJson = JSON.parse(await readFile(resolve(root, "package.json"), "utf8"));
if (packageJson.version !== EXPECTED_VERSION) {
  throw new Error(`Expected Desktop Commander ${EXPECTED_VERSION}; found ${packageJson.version ?? "unknown"}.`);
}
const sha256 = (text) => createHash("sha256").update(text).digest("hex");
for (const [relativePath, expectedHash] of Object.entries(EXPECTED_CONTEXT_FILES)) {
  const actualHash = sha256(await readFile(resolve(root, relativePath)));
  if (actualHash !== expectedHash) {
    throw new Error(`Context source SHA-256 mismatch for ${relativePath}: ${actualHash}`);
  }
}
const serverSource = await readFile(resolve(root, "dist/server.js"), "utf8");
const metadataCallCount = [...serverSource.matchAll(/buildUiToolMeta\([^)]*showMcpUiPreviews\)/g)].length;
if (!serverSource.includes("resources: listUiResources(),") ||
    !serverSource.includes("const showMcpUiPreviews = await shouldShowMcpUiPreviews();") ||
    metadataCallCount !== 5) {
  throw new Error("Desktop Commander UI exposure points differ from the reviewed server source.");
}
function replaceExactlyOnce(source, marker, replacement, label) {
  const first = source.indexOf(marker);
  if (first < 0 || source.indexOf(marker, first + marker.length) >= 0) {
    throw new Error(`Expected exactly one source marker for ${label}; refusing to patch.`);
  }
  return source.slice(0, first) + replacement + source.slice(first + marker.length);
}

async function patchFile(relativePath, transform) {
  const target = resolve(root, relativePath);
  const original = await readFile(target, "utf8");
  const originalHash = sha256(original);
  if (originalHash !== EXPECTED_FILES[relativePath]) {
    throw new Error(`Source SHA-256 mismatch for ${relativePath}: ${originalHash}`);
  }
  const updated = transform(original);
  if (updated === original) {
    throw new Error(`Patch made no change to ${relativePath}; refusing to continue.`);
  }
  await writeFile(target, updated, "utf8");
  const patchedHash = sha256(await readFile(target, "utf8"));
  if (patchedHash !== sha256(updated)) {
    throw new Error(`Post-write verification failed for ${relativePath}.`);
  }
  console.log(`${relativePath}: ${originalHash} -> ${patchedHash}`);
}
await patchFile("dist/utils/mcp-ui-ab-test.js", (source) =>
  replaceExactlyOnce(
    source,
    `export async function shouldShowMcpUiPreviews() {
    return resolveMcpUiPreviewDecision({`,
    `export async function shouldShowMcpUiPreviews() {
    if (process.env.DESKTOP_COMMANDER_DISABLE_MCP_UI === '1') {
        return false;
    }
    return resolveMcpUiPreviewDecision({`,
    "MCP UI preview decision"
  )
);

await patchFile("dist/ui/resources.js", (source) =>
  replaceExactlyOnce(
    source,
    `export function listUiResources() {
    return [FILE_PREVIEW_RESOURCE, CONFIG_EDITOR_RESOURCE];
}
export async function readUiResource(uri) {
    const resource = READABLE_UI_RESOURCES[uri];`,
    `export function listUiResources() {
    if (process.env.DESKTOP_COMMANDER_DISABLE_MCP_UI === '1') {
        return [];
    }
    return [FILE_PREVIEW_RESOURCE, CONFIG_EDITOR_RESOURCE];
}
export async function readUiResource(uri) {
    if (process.env.DESKTOP_COMMANDER_DISABLE_MCP_UI === '1') {
        return null;
    }
    const resource = READABLE_UI_RESOURCES[uri];`,
    "MCP UI resource visibility"
  )
);

console.log("PASS: Desktop Commander MCP UI opt-out patched; feature-flag state is untouched.");
