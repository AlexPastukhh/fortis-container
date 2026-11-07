# Preserve the deployed path-guidance image and add a narrow MCP UI opt-out.
FROM fortis-repo-mode:dc-0.2.52-fortis-path-guidance-20261104

USER root
COPY apply-mcp-ui-headless.mjs /tmp/fortis-mcp-ui-headless/apply.mjs
COPY test-mcp-ui-headless.mjs /tmp/fortis-mcp-ui-headless/test.mjs

RUN node --check /tmp/fortis-mcp-ui-headless/apply.mjs \
 && node --check /tmp/fortis-mcp-ui-headless/test.mjs \
 && node /tmp/fortis-mcp-ui-headless/apply.mjs /opt/dc/node_modules/@wonderwhy-er/desktop-commander \
 && node /tmp/fortis-mcp-ui-headless/test.mjs /opt/dc/node_modules/@wonderwhy-er/desktop-commander \
 && test "$(sha256sum /opt/dc/node_modules/@wonderwhy-er/desktop-commander/dist/utils/system-info.js | cut -d' ' -f1)" = "128c7f8c29dab1dd95e277d7929bc6dc05ade62a00d0df8b345bf04d7929c2f1" \
 && rm -rf /tmp/fortis-mcp-ui-headless

# Image-level default covers Repo1, Repo2 and container-side DC children consistently.
ENV DESKTOP_COMMANDER_DISABLE_MCP_UI=1
USER 1000:1000
