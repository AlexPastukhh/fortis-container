#!/usr/bin/env node
import { createHash } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const EXPECTED_VERSION = "0.2.52";
const EXPECTED_SOURCE_SHA256 = "101955412d1f9b11933cdd285742512b0cda13b054e0be40ddc2ec41507d8956";
const EXPECTED_PATCHED_SHA256 = "128c7f8c29dab1dd95e277d7929bc6dc05ade62a00d0df8b345bf04d7929c2f1";
const packageRoot = process.argv[2];
if (!packageRoot) {
  throw new Error("Usage: node apply-system-info-guidance.mjs <desktop-commander-package-root>");
}
const root = resolve(packageRoot);
const packageJson = JSON.parse(await readFile(resolve(root, "package.json"), "utf8"));
if (packageJson.version !== EXPECTED_VERSION) {
  throw new Error(`Expected Desktop Commander ${EXPECTED_VERSION}; found ${packageJson.version ?? "unknown"}.`);
}
const target = resolve(root, "dist/utils/system-info.js");
const original = await readFile(target, "utf8");
const originalHash = createHash("sha256").update(original).digest("hex");

function replaceRangeOnce(source, startMarker, endMarker, replacement, label) {
  const start = source.indexOf(startMarker);
  if (start < 0 || source.indexOf(startMarker, start + startMarker.length) >= 0) {
    throw new Error(`Expected exactly one start marker for ${label}.`);
  }
  const end = source.indexOf(endMarker, start);
  if (end < 0 || source.indexOf(endMarker, end + endMarker.length) >= 0) {
    throw new Error(`Expected exactly one end marker for ${label}.`);
  }
  return source.slice(0, start) + replacement + source.slice(end + endMarker.length);
}

if (originalHash === EXPECTED_PATCHED_SHA256) {
  console.log("Already patched; no changes made. SHA-256: " + originalHash);
  process.exit(0);
}
if (originalHash !== EXPECTED_SOURCE_SHA256) {
  throw new Error("Source hash mismatch; refusing to patch an unreviewed package file: " + originalHash);
}

const pathGuidanceMarker = "export function getPathGuidance(systemInfo) {";
const pathGuidanceOffset = original.indexOf(pathGuidanceMarker);
if (pathGuidanceOffset < 0 || original.indexOf(pathGuidanceMarker, pathGuidanceOffset + 1) >= 0) {
  throw new Error("Expected one getPathGuidance() definition; refusing to continue.");
}
const originalPathGuidance = original.slice(pathGuidanceOffset);

const mountedStart = "            guidance += " + String.fromCharCode(96) + "\n\nIMPORTANT: When users ask about files, FIRST check mounted directories above.";
const mountedEnd = "NOTE: Desktop Commander Docker installer mounts host folders to /home/[folder-name].`;";
const mountedReplacement = [
  "            guidance += `",
  "",
  "IMPORTANT: When users ask about files, FIRST check mounted directories above.",
  "Always use the listed container paths as-is for file operations.",
  "",
  "PATH HANDLING IN DOCKER:",
  "- Do not infer host-to-container path mappings or rewrite host paths into a guessed container directory.",
  "- If a user provides a host-side path, verify the actual Docker mount configuration before translating it.",
  "- If no mapping is verified, ask the user for the corresponding container path.`;"
].join("\n");

let updated = replaceRangeOnce(
  original, mountedStart, mountedEnd, mountedReplacement, "mounted-directories guidance"
);

const noMountStart = "            guidance += " + String.fromCharCode(96) +
  "\n\n⚠️  WARNING: No mounted directories detected.";
const noMountEnd = "Desktop Commander Docker installer typically mounts folders to /home/[folder-name]." +
  String.fromCharCode(96) + ";";
const noMountReplacement = [
  "            guidance += " + String.fromCharCode(96),
  "",
  "⚠️  WARNING: No mounted directories detected.",
  "Do not assume any host path is mounted inside this container.",
  "Verify the actual runtime mount configuration before translating or using a host-side path.",
  "Files outside verified persistent mounts may not survive container replacement." +
    String.fromCharCode(96) + ";"
].join("\n");
updated = replaceRangeOnce(
  updated, noMountStart, noMountEnd, noMountReplacement, "no-mounted-directories guidance"
);

const updatedPathOffset = updated.indexOf(pathGuidanceMarker);
if (updatedPathOffset < 0 || updated.slice(updatedPathOffset) !== originalPathGuidance) {
  throw new Error("getPathGuidance() changed; refusing to write the patch.");
}
const osStart = updated.indexOf("export function getOSSpecificGuidance(systemInfo) {");
const osEnd = updated.indexOf("export function getDevelopmentToolGuidance(systemInfo) {", osStart);
if (osStart < 0 || osEnd < 0) {
  throw new Error("Could not isolate getOSSpecificGuidance() for final validation.");
}
const osGuidance = updated.slice(osStart, osEnd);
if (osGuidance.includes("/home/") || osGuidance.includes("Docker installer") ||
    osGuidance.includes("PATH TRANSLATION IN DOCKER") || osGuidance.includes("Suggest user remount")) {
  throw new Error("Obsolete generic path guidance remains after patch; refusing to write.");
}
if (!osGuidance.includes("Do not infer host-to-container path mappings") ||
    !osGuidance.includes("Do not assume any host path is mounted")) {
  throw new Error("Required verified-mount guidance is missing; refusing to write.");
}
await writeFile(target, updated, "utf8");
const patchedHash = createHash("sha256").update(updated).digest("hex");
console.log("Patched Desktop Commander " + EXPECTED_VERSION + " system-info.js.");
console.log("Before SHA-256: " + originalHash);
console.log("After SHA-256:  " + patchedHash);
console.log("getPathGuidance(): byte-for-byte unchanged.");
