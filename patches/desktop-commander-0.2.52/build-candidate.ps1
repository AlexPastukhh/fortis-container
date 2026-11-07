$ErrorActionPreference = 'Stop'

$containerName = 'fortis-repo-test'
$expectedContainerId = '04fed7b726a8536d63c4d2533cfc7ee3072956ff0c3f571504d7f709f7909030'
$baseImage = 'fortis-repo-mode:dc-0.2.52'
$expectedBaseImageId = 'sha256:2c84fabebb34265e53b020f21a11683a4c68cbb41a08f5f11f9b01c7de5ed8c9'
$candidateImage = 'fortis-repo-mode:dc-0.2.52-fortis-path-guidance-20261104'

Write-Host '=== READ-ONLY BASE CONTAINER PREFLIGHT ==='
$containerJson = docker inspect $containerName
if ($LASTEXITCODE -ne 0) { throw "Cannot inspect $containerName." }
$container = @($containerJson | ConvertFrom-Json)[0]
if ($container.Id -ne $expectedContainerId) {
    throw "Container identity changed; expected $expectedContainerId, got $($container.Id)."
}
if ($container.State.Running -ne $true) { throw "$containerName is not running; stop for review." }
if ($container.Config.Image -ne $baseImage) {
    throw "Unexpected container image tag: $($container.Config.Image)."
}
if ($container.Image -ne $expectedBaseImageId) {
    throw "Unexpected base image ID: $($container.Image)."
}
if ($container.HostConfig.ReadonlyRootfs -ne $true) {
    throw 'Root filesystem security setting differs from the reviewed baseline.'
}

Write-Host '=== READ-ONLY BASE IMAGE PREFLIGHT ==='
$baseImageId = docker image inspect --format '{{.Id}}' $baseImage
if ($LASTEXITCODE -ne 0) { throw "Base image $baseImage is not available locally." }
if ($baseImageId -ne $expectedBaseImageId) {
    throw "Base image tag moved; expected $expectedBaseImageId, got $baseImageId."
}

$buildContext = Join-Path $env:TEMP (
    'fortis-dc-guidance-build-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
)
New-Item -ItemType Directory -Path $buildContext | Out-Null

Write-Host '=== COPY REVIEWED PATCH FROM WORKSPACE VOLUME ==='
docker cp "${containerName}:/workspace/repos/fortis-container/patches/desktop-commander-0.2.52/." $buildContext
if ($LASTEXITCODE -ne 0) { throw 'Patch copy failed; no image was built.' }
$dockerfile = Join-Path $buildContext 'Dockerfile'
if (!(Test-Path $dockerfile) -or
    !(Test-Path (Join-Path $buildContext 'apply-system-info-guidance.mjs')) -or
    !(Test-Path (Join-Path $buildContext 'test-system-info-guidance.mjs'))) {
    throw 'Build context is incomplete; no image was built.'
}

Write-Host '=== BUILD PATCH CANDIDATE IMAGE ONLY ==='
docker build --network=none --pull=false --file $dockerfile --tag $candidateImage $buildContext
if ($LASTEXITCODE -ne 0) { throw 'Candidate image build failed.' }
$baseImageIdAfterBuild = docker image inspect --format '{{.Id}}' $baseImage
if ($LASTEXITCODE -ne 0 -or $baseImageIdAfterBuild -ne $expectedBaseImageId) {
    throw 'Base image tag changed during build; candidate must not be used.'
}

Write-Host '=== VERIFY CANDIDATE IMAGE CONFIGURATION ==='
$baseConfig = docker image inspect --format '{{.Config.User}}|{{json .Config.Cmd}}|{{json .Config.Entrypoint}}|{{.Config.WorkingDir}}' $baseImage
if ($LASTEXITCODE -ne 0) { throw 'Could not inspect base image configuration.' }
$candidateConfig = docker image inspect --format '{{.Config.User}}|{{json .Config.Cmd}}|{{json .Config.Entrypoint}}|{{.Config.WorkingDir}}' $candidateImage
if ($LASTEXITCODE -ne 0) { throw 'Could not inspect candidate image configuration.' }
if ($candidateConfig -ne $baseConfig) {
    throw "Candidate changed runtime defaults. Base=[$baseConfig] Candidate=[$candidateConfig]"
}
$candidateId = docker image inspect --format '{{.Id}}' $candidateImage
if ($LASTEXITCODE -ne 0) { throw 'Could not obtain candidate image ID.' }

Write-Host "Base image:      $baseImage ($baseImageId)"
Write-Host "Candidate image: $candidateImage ($candidateId)"
Write-Host "Build context:   $buildContext"
Write-Host 'PASS: candidate built and default runtime config preserved.'
Write-Host 'No container was started, stopped, restarted, or replaced.'
