#!/usr/bin/env node
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

const packageRoot = process.argv[2];
if (!packageRoot) {
  throw new Error("Usage: node test-mcp-ui-headless.mjs <desktop-commander-package-root>");
}
const root = resolve(packageRoot);
const envName = "DESKTOP_COMMANDER_DISABLE_MCP_UI";
const { shouldShowMcpUiPreviews, resolveMcpUiPreviewDecision } =
  await import(pathToFileURL(resolve(root, "dist/utils/mcp-ui-ab-test.js")).href);
const { listUiResources, readUiResource } =
  await import(pathToFileURL(resolve(root, "dist/ui/resources.js")).href);
const { CONFIG_EDITOR_RESOURCE_URI, FILE_PREVIEW_RESOURCE_URI, buildUiToolMeta } =
  await import(pathToFileURL(resolve(root, "dist/ui/contracts.js")).href);

const hashFile = async (relativePath) =>
  createHash("sha256").update(await readFile(resolve(root, relativePath))).digest("hex");
assert.equal(await hashFile("dist/server.js"),
  "dacffa416d0a46351aa553e6b05e51a10638bd190821eda03032de045b9f2aaf");
assert.equal(await hashFile("dist/ui/contracts.js"),
  "47559cdf2b1e806dbda0cef8d7e9eda4a42b3b32df0ce10b418b3ca37c501bad");
assert.equal(await hashFile("dist/index.js"),
  "a4145198dc75cd34e7c7452c2054b4cc0d29e199ae1459961a17e4da25a13500");
const serverSource = await readFile(resolve(root, "dist/server.js"), "utf8");
assert.ok(serverSource.includes("resources: listUiResources(),"));
assert.ok(serverSource.includes("const showMcpUiPreviews = await shouldShowMcpUiPreviews();"));
assert.equal([...serverSource.matchAll(/buildUiToolMeta\([^)]*showMcpUiPreviews\)/g)].length, 5);
process.env[envName] = "1";
assert.equal(await shouldShowMcpUiPreviews(), false,
  "explicit opt-out must override the remote A/B assignment");
assert.deepEqual(listUiResources(), [],
  "resources/list must return no Desktop Commander UI resources");
assert.equal(await readUiResource(CONFIG_EDITOR_RESOURCE_URI), null,
  "config editor resource must not be readable while disabled");
assert.equal(await readUiResource(FILE_PREVIEW_RESOURCE_URI), null,
  "file preview resource must not be readable while disabled");
assert.equal(buildUiToolMeta(CONFIG_EDITOR_RESOURCE_URI, true, false), undefined,
  "tool metadata builder must omit UI metadata when the decision is false");

process.env[envName] = "0";
assert.equal(listUiResources().length, 2,
  "non-1 values must preserve the normal resource catalog");
assert.ok(buildUiToolMeta(CONFIG_EDITOR_RESOURCE_URI, true, true),
  "normal UI metadata behavior must remain available");
delete process.env[envName];
assert.equal(listUiResources().length, 2,
  "unset switch must preserve the default resource catalog");

const deps = (variant) => ({
  getExistingAssignment: async () => undefined,
  isFirstRun: () => true,
  wasLoadedFromCache: () => true,
  waitForFreshFlags: async () => {},
  getABTestVariant: async () => variant,
  capture: async () => {},
});
assert.equal(await resolveMcpUiPreviewDecision(deps("showMCPUi")), true,
  "existing show variant behavior must remain unchanged");
assert.equal(await resolveMcpUiPreviewDecision(deps("notShowMCPUi")), false,
  "existing hide variant behavior must remain unchanged");

const systemInfoPath = resolve(root, "dist/utils/system-info.js");
const systemInfoHash = createHash("sha256").update(await readFile(systemInfoPath)).digest("hex");
assert.equal(systemInfoHash,
  "128c7f8c29dab1dd95e277d7929bc6dc05ade62a00d0df8b345bf04d7929c2f1",
  "previously deployed Fortis path-guidance patch must remain byte-identical");

console.log("PASS: UI metadata decision, resources/list, resource reads, default behavior, A/B behavior and path-guidance pin.");
