$ErrorActionPreference = 'Stop'

$containerName = 'fortis-repo-test'
$expectedContainerId = '3c4b50df90381ffd23809e0c7ba5e3bf8762ac33829ce2fb3a6d44a29da2d07c'
$baseImage = 'fortis-repo-mode:dc-0.2.52-fortis-path-guidance-20261104'
$expectedBaseImageId = 'sha256:1b582246edf85fa885736d1d9c325cc33697ab7cd511c73dcfb3394ed7b76750'
$candidateImage = 'fortis-repo-mode:dc-0.2.52-fortis-mcp-ui-headless-20261104'
$uiEnvironment = 'DESKTOP_COMMANDER_DISABLE_MCP_UI=1'

Write-Host '=== READ-ONLY ACTIVE CONTAINER PREFLIGHT ==='
$containerJson = docker inspect --type container $containerName
if ($LASTEXITCODE -ne 0) { throw "Cannot inspect $containerName." }
$container = @($containerJson | ConvertFrom-Json)[0]
if ($container.Id -ne $expectedContainerId) {
    throw "Container identity changed; expected $expectedContainerId, got $($container.Id)."
}
if ($container.State.Running -ne $true) { throw "$containerName is not running; stop for review." }
$acceptedConfigImageRefs = @($baseImage, $expectedBaseImageId)
if ($container.Config.Image -notin $acceptedConfigImageRefs -or
    $container.Image -ne $expectedBaseImageId) {
    throw "Active container image reference/ID differs from the reviewed path-guidance deployment. Config.Image='$($container.Config.Image)'; Image='$($container.Image)'."
}
if ($container.HostConfig.ReadonlyRootfs -ne $true) {
    throw 'Read-only rootfs security setting differs from the reviewed baseline.'
}
$containerEnv = @($container.Config.Env)
if (@($containerEnv | Where-Object { ([string]$_).StartsWith('DESKTOP_COMMANDER_DISABLE_MCP_UI=', [StringComparison]::Ordinal) }).Count -ne 0) {
    throw 'Active container explicitly overrides the UI switch; inspect container creation settings before building.'
}
Write-Host '=== READ-ONLY BASE IMAGE PREFLIGHT ==='
$baseJson = docker image inspect $baseImage
if ($LASTEXITCODE -ne 0) { throw "Base image $baseImage is not available locally." }
$base = @($baseJson | ConvertFrom-Json)[0]
if ($base.Id -ne $expectedBaseImageId) {
    throw "Base image tag moved; expected $expectedBaseImageId, got $($base.Id)."
}
$baseEnv = @($base.Config.Env)
if (@($baseEnv | Where-Object { ([string]$_).StartsWith('DESKTOP_COMMANDER_DISABLE_MCP_UI=', [StringComparison]::Ordinal) }).Count -ne 0) {
    throw 'Base image already defines the UI switch; review the image lineage before building.'
}

$buildContext = Join-Path $env:TEMP (
    'fortis-mcp-ui-headless-build-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
)
New-Item -ItemType Directory -Path $buildContext | Out-Null

Write-Host '=== COPY REVIEWED PATCH FROM WORKSPACE VOLUME ==='
docker cp "${containerName}:/workspace/repos/fortis-container/patches/desktop-commander-0.2.52-mcp-ui-headless/." $buildContext
if ($LASTEXITCODE -ne 0) { throw 'Patch copy failed; no image was built.' }
$required = @('Dockerfile','apply-mcp-ui-headless.mjs','test-mcp-ui-headless.mjs')
foreach ($name in $required) {
    if (!(Test-Path -LiteralPath (Join-Path $buildContext $name) -PathType Leaf)) {
        throw "Build context missing $name; no image was built."
    }
}
Write-Host '=== BUILD PATCH CANDIDATE IMAGE ONLY ==='
docker build --network=none --pull=false --file (Join-Path $buildContext 'Dockerfile') --tag $candidateImage $buildContext
if ($LASTEXITCODE -ne 0) { throw 'Candidate image build failed.' }
$baseAfter = docker image inspect --format '{{.Id}}' $baseImage
if ($LASTEXITCODE -ne 0 -or $baseAfter -ne $expectedBaseImageId) {
    throw 'Base image tag changed during build; candidate must not be used.'
}

Write-Host '=== VERIFY CANDIDATE IMAGE CONFIGURATION ==='
$candidateJson = docker image inspect $candidateImage
if ($LASTEXITCODE -ne 0) { throw 'Could not inspect candidate image.' }
$candidate = @($candidateJson | ConvertFrom-Json)[0]
if ($candidate.Config.User -cne $base.Config.User -or
    (($candidate.Config.Cmd | ConvertTo-Json -Compress -Depth 10) -cne ($base.Config.Cmd | ConvertTo-Json -Compress -Depth 10)) -or
    (($candidate.Config.Entrypoint | ConvertTo-Json -Compress -Depth 10) -cne ($base.Config.Entrypoint | ConvertTo-Json -Compress -Depth 10)) -or
    $candidate.Config.WorkingDir -cne $base.Config.WorkingDir) {
    throw 'Candidate changed user, command, entrypoint or workdir.'
}
$expectedEnv = @($baseEnv) + $uiEnvironment
$candidateEnv = @($candidate.Config.Env)
if ($candidateEnv.Count -ne $expectedEnv.Count) {
    throw 'Candidate environment differs by more than the single reviewed UI switch.'
}
for ($i = 0; $i -lt $expectedEnv.Count; $i++) {
    if ($candidateEnv[$i] -cne $expectedEnv[$i]) {
        throw "Unexpected candidate environment change at index $i."
    }
}
$candidateId = $candidate.Id

Write-Host "Base image:      $baseImage ($($base.Id))"
Write-Host "Candidate image: $candidateImage ($candidateId)"
Write-Host "Build context:   $buildContext"
Write-Host 'PASS: MCP UI patch candidate built; only the reviewed environment default was added.'
Write-Host 'No container was created, started, stopped, restarted, or replaced.'
