# Build a patch-only derivative of the verified Fortis Repo base image.
# The base image is checked by build-candidate.ps1 before this Dockerfile is used.
FROM fortis-repo-mode:dc-0.2.52

USER root
COPY apply-system-info-guidance.mjs /tmp/fortis-dc-guidance-patch/apply.mjs
COPY test-system-info-guidance.mjs /tmp/fortis-dc-guidance-patch/test.mjs

RUN node --check /tmp/fortis-dc-guidance-patch/apply.mjs \
 && node --check /tmp/fortis-dc-guidance-patch/test.mjs \
 && node /tmp/fortis-dc-guidance-patch/apply.mjs /opt/dc/node_modules/@wonderwhy-er/desktop-commander \
 && node /tmp/fortis-dc-guidance-patch/test.mjs /opt/dc/node_modules/@wonderwhy-er/desktop-commander \
 && rm -rf /tmp/fortis-dc-guidance-patch

# Preserve the original runtime user; inherited WORKDIR, ENV, ENTRYPOINT and CMD stay unchanged.
USER 1000:1000
