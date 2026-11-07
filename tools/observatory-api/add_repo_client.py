#!/usr/bin/env python3
"""One-shot offline Gateway configuration update. Runs in a disposable Docker
container with --network none; only the dedicated Gateway private volume and
a read-only request file are mounted. Never reads a raw token.
"""
import json
import os
from pathlib import Path
import re
import stat
import sys
import time

PRIVATE = Path("/data")
CONFIG = PRIVATE / "clients.json"
REQUEST = Path("/tmp/repo-client.json")
SAFE_CHAT = re.compile(r"[A-Za-z0-9-]{8,100}\Z")
SAFE_SHA = re.compile(r"[a-f0-9]{64}\Z")


def reject(message):
    raise ValueError(message)


def checked_read_regular(path: Path, limit: int) -> bytes:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
        reject("unsafe_file")
    return path.read_bytes()


def atomic_new(path: Path, raw: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(raw)
            out.flush()
            os.fsync(out.fileno())
    finally:
        if path.exists():
            os.chown(path, 1000, 1000)
            os.chmod(path, 0o600)


def main() -> None:
    if not PRIVATE.is_dir() or PRIVATE.is_symlink():
        reject("gateway_private_volume_not_available")
    current_raw = checked_read_regular(CONFIG, 65536)
    if (CONFIG.stat().st_uid != 1000 or
            stat.S_IMODE(CONFIG.stat().st_mode) != 0o600):
        reject("invalid_gateway_client_config_permissions")
    current = json.loads(current_raw)
    request = json.loads(checked_read_regular(REQUEST, 65536))
    if (not isinstance(current, dict) or set(current) != {"version", "clients"}
            or current["version"] != 1 or not isinstance(current["clients"], list)):
        reject("unexpected_client_config")
    if (not isinstance(request, dict) or set(request) != {"id", "token_sha256", "permissions", "chats"}
            or request["id"] != "fortis-repo" or
            not isinstance(request["token_sha256"], str) or
            not SAFE_SHA.fullmatch(request["token_sha256"])):
        reject("invalid_repo_client_request")
    permissions = request["permissions"]
    chats = request["chats"]
    allowed = {"read:metadata", "read:history", "write:events", "write:messages"}
    if (not isinstance(permissions, list) or not permissions or
            len(permissions) != len(set(permissions)) or
            not set(permissions) <= allowed or
            not isinstance(chats, list) or not chats or len(chats) > 200 or
            any(not isinstance(c, str) or not SAFE_CHAT.fullmatch(c) for c in chats) or
            len(set(chats)) != len(chats)):
        reject("invalid_scope_or_permissions")

    existing = [c for c in current["clients"] if c.get("id") == "fortis-repo"]
    if existing:
        if len(existing) != 1 or existing[0] != request:
            reject("repo_client_already_exists_and_differs")
        print("REPO_GATEWAY_CLIENT=UNCHANGED")
        return
    if len(current["clients"]) >= 32 or any(
            c.get("token_sha256") == request["token_sha256"] for c in current["clients"]):
        reject("client_capacity_or_duplicate_hash")

    current["clients"].append(request)
    rendered = json.dumps(current, ensure_ascii=True, separators=(",", ":")).encode("ascii")
    if len(rendered) > 65536:
        reject("client_config_exceeds_size_limit")

    # Immutable backup before any mutation. Never delete other client entries.
    backup = PRIVATE / ("clients.json.before-fortis-repo-" + str(time.time_ns()))
    atomic_new(backup, current_raw)
    staged = PRIVATE / ("clients.json.pending-fortis-repo-" + str(time.time_ns()))
    try:
        atomic_new(staged, rendered)
        os.replace(staged, CONFIG)
        dirfd = os.open(PRIVATE, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    finally:
        if staged.exists():
            staged.unlink()
    print("REPO_GATEWAY_CLIENT=ADDED")
    print("GATEWAY_CONFIG_BACKUP=CREATED")
    print("GATEWAY_RESTART_REQUIRED=YES")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        print("REPO_CLIENT_UPDATE_REFUSED: " + type(error).__name__, file=sys.stderr)
        sys.exit(1)
