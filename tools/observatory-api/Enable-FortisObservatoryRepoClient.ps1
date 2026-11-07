# Authorize the *existing* Fortis Repo container as a separate Gateway client.
# Does not restart containers or update Windows Viewer/Notifier.
# Default: metadata + history reads. -AllowWrites additionally grants staging
# of assistant messages/events into the existing Observatory inbox.
[CmdletBinding()]
param([switch] $AllowWrites)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Require-Docker([string] $Action) {
    if ($LASTEXITCODE -ne 0) { throw "$Action failed (Docker exit $LASTEXITCODE)" }
}
$repo = 'fortis-repo-test'
$gateway = 'fortis-observatory-api'
$gatewayTag = 'fortis-observatory-api:local'
$privateVolume = 'fortis-observatory-api-private'
$src = '/workspace/repo/Repos/fortis-container/tools/observatory-api'
$root = Join-Path $env:LOCALAPPDATA 'FortisObservatoryV1\ApiGateway'
$windowsToken = Join-Path $root 'windows-client-token.txt'
$requestPath = Join-Path $root ("repo-client-request-" + [guid]::NewGuid().ToString('N') + '.json')
$helperPath = Join-Path $env:TEMP ('fortis-repo-client-config-' + [guid]::NewGuid().ToString('N') + '.py')

if (-not (Test-Path -LiteralPath $root -PathType Container) -or
    -not (Get-Acl -LiteralPath $root).AreAccessRulesProtected) {
    throw 'Windows Gateway private directory missing or ACL inheritance enabled'
}
if (-not (Test-Path -LiteralPath $windowsToken -PathType Leaf)) {
    throw 'Missing Windows Gateway client token; no changes made'
}
foreach ($path in @($root, $windowsToken)) {
    if ((Get-Item -LiteralPath $path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
        throw "Unsafe reparse point: $path"
    }
}
$inspectRaw = & docker inspect $gateway
Require-Docker 'Inspect Gateway'
$inspect = ($inspectRaw -join "`n") | ConvertFrom-Json
if ($inspect[0].State.Running -ne $true) {
    throw 'Gateway is stopped; start/verify it before provisioning Repo'
}
if ($inspect[0].Config.Image -ne $gatewayTag) {
    throw 'Gateway image tag differs; no changes made'
}
$mounts = @($inspect[0].Mounts | Where-Object {
    $_.Type -eq 'volume' -and $_.Name -eq $privateVolume -and
    $_.Destination -eq '/data/private'
})
if ($mounts.Count -ne 1) {
    throw 'Gateway private volume mapping unexpectedly changed'
}

# Initialize a private Repo key without printing or transporting the secret.
# Only the SHA-256 digest is copied to the Windows provisioning process.
$initOut = & docker exec $repo python3 "$src/fortis_observatory_client.py" init-key
Require-Docker 'Prepare Repo client key'
$hashRows = @($initOut | Where-Object { $_ -match '^REPO_CLIENT_SHA256=[a-f0-9]{64}$' })
if ($hashRows.Count -ne 1) { throw 'No valid Repo client SHA-256 in initialization output' }
$tokenSha = [string]($hashRows[0] -replace '^REPO_CLIENT_SHA256=', '')

# All existing registered chats are authorized. This version of Gateway
# does not support *dynamic all_registered* for non-Windows clients;
# newly registered chats require an explicit future scope update.
$ownerToken = [IO.File]::ReadAllText($windowsToken, [Text.Encoding]::ASCII).Trim()
if ($ownerToken -notmatch '^[A-Za-z0-9_-]{32,128}$') {
    throw 'Invalid Windows client token'
}
try {
    $ownerHeaders = @{ Authorization = ('Bearer ' + $ownerToken) }
    $reply = Invoke-RestMethod -Uri 'http://127.0.0.1:18756/v1/sessions' -Headers $ownerHeaders -TimeoutSec 7
} finally {
    Remove-Variable ownerToken, ownerHeaders -ErrorAction SilentlyContinue
}
if ($reply.ok -ne $true) { throw 'Gateway owner sessions response invalid' }
$chats = @($reply.sessions | ForEach-Object { [string]$_.conversation_id } | Sort-Object -Unique)
if ($chats.Count -lt 1 -or $chats.Count -gt 200 -or
    @($chats | Where-Object { $_ -cnotmatch '^[A-Za-z0-9-]{8,100}$' }).Count -gt 0) {
    throw 'Refusing empty, oversized or malformed chat scope'
}
$permissions = @('read:metadata','read:history')
if ($AllowWrites) { $permissions += @('write:events','write:messages') }

$request = @{
    id = 'fortis-repo'
    token_sha256 = $tokenSha
    permissions = $permissions
    chats = $chats
}
$json = ConvertTo-Json $request -Depth 5
$utf8 = [Text.UTF8Encoding]::new($false)

try {
    [IO.File]::WriteAllText($requestPath, $json, $utf8)

    & docker cp "$($repo):$src/add_repo_client.py" $helperPath
    Require-Docker 'Copy one-shot config helper'

    & docker run --rm --user 0 --network none `
        --mount "type=volume,source=$privateVolume,target=/data" `
        --mount "type=bind,source=$helperPath,target=/tmp/add_repo_client.py,readonly" `
        --mount "type=bind,source=$requestPath,target=/tmp/repo-client.json,readonly" `
        --entrypoint python3 $gatewayTag /tmp/add_repo_client.py
    Require-Docker 'Register Repo Gateway client'

    Write-Host 'REPO_CLIENT_REGISTERED_IN_DISK_CONFIG=YES'
    Write-Host ("REPO_ALLOWED_CHATS={0}" -f $chats.Count)
    Write-Host ("REPO_WRITE_ACCESS={0}" -f [bool]$AllowWrites)
    Write-Host 'GATEWAY_RESTART_PERFORMED=NO'
    Write-Host 'NEXT_EXPLICIT_ACTION=docker restart fortis-observatory-api'
} finally {
    if (Test-Path -LiteralPath $requestPath) {
        Remove-Item -LiteralPath $requestPath -Force
    }
    if (Test-Path -LiteralPath $helperPath) {
        Remove-Item -LiteralPath $helperPath -Force
    }
}
