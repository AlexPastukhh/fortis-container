#!/usr/bin/env node
import assert from "node:assert/strict";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

const packageRoot = process.argv[2];
if (!packageRoot) {
  throw new Error("Usage: node test-system-info-guidance.mjs <desktop-commander-package-root>");
}
const modulePath = resolve(packageRoot, "dist/utils/system-info.js");
const { getOSSpecificGuidance, getPathGuidance } =
  await import(pathToFileURL(modulePath).href + "?fortis-guidance-test");

const mounts = [
  { containerPath: "/workspace/files", readOnly: false, description: "Mounted directory: files" },
  { containerPath: "/workspace/repo", readOnly: false, description: "Mounted directory: repo" },
  { containerPath: "/workspace/repos", readOnly: false, description: "Mounted directory: repos" },
];
const systemInfo = {
  platformName: "Linux (Docker)",
  defaultShell: "bash",
  isWindows: false,
  isMacOS: false,
  docker: {
    isContainer: true,
    containerType: "docker",
    orchestrator: null,
    mountPoints: mounts,

    containerEnvironment: { containerName: "fortis-test" },
  },
};

const mountedGuidance = getOSSpecificGuidance(systemInfo);
for (const path of ["/workspace/files", "/workspace/repo", "/workspace/repos"]) {
  assert.ok(mountedGuidance.includes(path), "Missing actual container mount: " + path);
}
assert.ok(mountedGuidance.includes("Do not infer host-to-container path mappings"));
assert.ok(mountedGuidance.includes("verify the actual Docker mount configuration"));
assert.ok(mountedGuidance.includes("ask the user for the corresponding container path"));
assert.ok(mountedGuidance.includes("Container: fortis-test"));
assert.ok(!mountedGuidance.includes("/home/"));
assert.ok(!mountedGuidance.includes("Docker installer"));
assert.ok(!mountedGuidance.includes("PATH TRANSLATION IN DOCKER"));

const expectedPathGuidance =
  "Always use absolute paths for reliability. Paths are automatically normalized regardless of slash direction. " +
  "\n\n🐳 DOCKER: Prefer paths within mounted directories: /workspace/files, /workspace/repo, /workspace/repos." +
  "\nWhen users ask about file locations, check these mounted paths first.";
assert.equal(getPathGuidance(systemInfo), expectedPathGuidance);

const noMountInfo = {
  ...systemInfo,
  docker: { ...systemInfo.docker, mountPoints: [] },
};
const noMountGuidance = getOSSpecificGuidance(noMountInfo);
assert.ok(noMountGuidance.includes("WARNING: No mounted directories detected."));
assert.ok(noMountGuidance.includes("Do not assume any host path is mounted"));
assert.ok(noMountGuidance.includes("Verify the actual runtime mount configuration"));
assert.ok(noMountGuidance.includes("may not survive container replacement"));
assert.ok(!noMountGuidance.includes("/home/"));
assert.ok(!noMountGuidance.includes("Docker installer"));
assert.ok(!noMountGuidance.includes("remount"));
assert.equal(
  getPathGuidance(noMountInfo),
  "Always use absolute paths for reliability. Paths are automatically normalized regardless of slash direction."
);

console.log("PASS: mounted and no-mount OS guidance; no guessed /home mapping; getPathGuidance unchanged.");
