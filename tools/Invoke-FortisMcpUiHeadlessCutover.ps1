# Fortis shared-container MCP UI-headless cutover.
# Windows PowerShell 5.1; run in a normal, non-elevated owner session.
# Preview is read-only. Cutover preserves the current container as rollback.
[CmdletBinding()]
param(
    [ValidateSet('Preview','Cutover')][string]$Action = 'Preview'
)
$ErrorActionPreference = 'Stop'

$containerName = 'fortis-repo-test'
$expectedActiveId = '3c4b50df90381ffd23809e0c7ba5e3bf8762ac33829ce2fb3a6d44a29da2d07c'
$expectedBaseImageId = 'sha256:1b582246edf85fa885736d1d9c325cc33697ab7cd511c73dcfb3394ed7b76750'
$baseImage = 'fortis-repo-mode:dc-0.2.52-fortis-path-guidance-20261104'
$candidateImage = 'fortis-repo-mode:dc-0.2.52-fortis-mcp-ui-headless-20261104'
$expectedCandidateId = 'sha256:f6d21fea25a8b67da533a8400f6eb7923a3d22605a00a784d35e3625253496d9'
$uiEnvironment = 'DESKTOP_COMMANDER_DISABLE_MCP_UI=1'
$oldRollbackName = 'fortis-repo-test-pre-path-guidance-20261104'
$expectedOldRollbackId = '04fed7b726a8536d63c4d2533cfc7ee3072956ff0c3f571504d7f709f7909030'
$rollbackName = 'fortis-repo-test-pre-mcp-ui-headless-20261104'
$stageName = 'fortis-repo-test-ui-headless-stage-20261104'
$failedName = 'fortis-repo-test-ui-headless-failed-20261104'

if ($env:OS -ne 'Windows_NT') { throw 'Windows PowerShell is required.' }
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
if ($null -eq $identity.User -or $identity.User.Value -cne 'S-1-5-21-303538662-3368424508-2654684973-1001') {
    throw 'Run from the original Fortis owner Windows account.'
}
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
if ($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Use a normal, non-elevated PowerShell window.'
}
$dockerPath = (Get-Command docker.exe -CommandType Application -ErrorAction Stop).Source

function Get-Value {
    param($Object, [string]$Name, $Default = $null)
    if ($null -eq $Object) { return $Default }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) { return $Default }
    return $property.Value
}
function Invoke-Docker {
    param([string[]]$Arguments)
    $output = @(& $script:dockerPath @Arguments 2>&1)
    $code = $LASTEXITCODE
    if ($code -ne 0) {
        throw ("docker " + ($Arguments -join ' ') + " failed (" + $code + "): " + ($output -join [Environment]::NewLine))
    }
    return $output
}
function Get-ContainerInspect {
    param([string]$Name)
    $output = Invoke-Docker @('inspect','--type','container',$Name)
    $items = @(ConvertFrom-Json -InputObject ($output -join [Environment]::NewLine) -ErrorAction Stop)
    if ($items.Count -ne 1) { throw "Expected one container inspect result for $Name." }
    return $items[0]
}
function Get-ImageInspect {
    param([string]$Name)
    $output = Invoke-Docker @('image','inspect',$Name)
    $items = @(ConvertFrom-Json -InputObject ($output -join [Environment]::NewLine) -ErrorAction Stop)
    if ($items.Count -ne 1) { throw "Expected one image inspect result for $Name." }
    return $items[0]
}
function Assert-StringSet {
    param([object[]]$Actual, [object[]]$Expected, [string]$Label)
    $a = @($Actual | ForEach-Object { [string]$_ } | Sort-Object -CaseSensitive)
    $e = @($Expected | ForEach-Object { [string]$_ } | Sort-Object -CaseSensitive)
    if (($a -join [Environment]::NewLine) -cne ($e -join [Environment]::NewLine)) {
        throw "$Label mismatch. Actual=[$($a -join ', ')]; Expected=[$($e -join ', ')]."
    }
}
function Assert-MountContract {
    param($Info)
    $rules = @(
        [pscustomobject]@{Type='volume';Source='fortis-repo-workspace';Target='/workspace/repo';Subpath='';ReadOnly=$false}
        [pscustomobject]@{Type='volume';Source='fortis-repo-workspace';Target='/workspace/repos';Subpath='Repos';ReadOnly=$false}
        [pscustomobject]@{Type='volume';Source='fortis-repo-workspace';Target='/workspace/files';Subpath='Workfiles';ReadOnly=$false}
        [pscustomobject]@{Type='volume';Source='fortis-r7-client';Target='/run/fortis-client';Subpath='';ReadOnly=$true}
    )
    $requested = @(Get-Value $Info.HostConfig 'Mounts' @())
    if ($requested.Count -ne 4) { throw 'Requested Docker mount count is not exactly four.' }
    foreach ($rule in $rules) {
        $matches = @($requested | Where-Object { (Get-Value $_ 'Target' '') -ceq $rule.Target })
        if ($matches.Count -ne 1) { throw "Requested mount missing or duplicated: $($rule.Target)" }
        $mount = $matches[0]
        $volumeOptions = Get-Value $mount 'VolumeOptions'
        $subpath = [string](Get-Value $volumeOptions 'Subpath' '')
        $readOnly = [bool](Get-Value $mount 'ReadOnly' $false)
        if ((Get-Value $mount 'Type' '') -cne $rule.Type -or
            (Get-Value $mount 'Source' '') -cne $rule.Source -or
            $subpath -cne $rule.Subpath -or $readOnly -ne $rule.ReadOnly) {
            throw "Requested mount differs from the reviewed contract: $($rule.Target)"
        }
    }
    $effective = @((Get-Value $Info 'Mounts' @()) | Where-Object { (Get-Value $_ 'Type' '') -cne 'tmpfs' })
    if ($effective.Count -ne 4) { throw 'Effective Docker mount count is not exactly four.' }
    foreach ($rule in $rules) {
        $matches = @($effective | Where-Object { (Get-Value $_ 'Destination' '') -ceq $rule.Target })
        $expectedRw = -not $rule.ReadOnly
        if ($matches.Count -ne 1 -or
            (Get-Value $matches[0] 'Type' '') -cne 'volume' -or
            (Get-Value $matches[0] 'Name' '') -cne $rule.Source -or
            [bool](Get-Value $matches[0] 'RW' $false) -ne $expectedRw) {
            throw "Effective Docker mount differs from the reviewed contract: $($rule.Target)"
        }
    }
}
function Assert-ContainerContract {
    param($Info, [string]$ExpectedName, [string]$ExpectedImageId, [bool]$UiEnabled, [bool]$CheckNetworks)
    if ($Info.Name -cne ('/' + $ExpectedName) -or $Info.Image -cne $ExpectedImageId) {
        throw "Container name/image identity mismatch for $ExpectedName."
    }
    if ($Info.Config.User -cne '1000:1000' -or $Info.Config.WorkingDir -cne '/workspace/repos') {
        throw 'Container Linux user or working directory changed.'
    }
    if (@($Info.Config.Cmd).Count -ne 2 -or $Info.Config.Cmd[0] -cne 'sleep' -or $Info.Config.Cmd[1] -cne 'infinity') {
        throw 'Container command differs from the reviewed sleep-infinity host command.'
    }
    $envEntries = @($Info.Config.Env | ForEach-Object { [string]$_ })
    $uiEntries = @($envEntries | Where-Object { $_.StartsWith('DESKTOP_COMMANDER_DISABLE_MCP_UI=',[StringComparison]::Ordinal) })
    if ($UiEnabled) {
        if ($uiEntries.Count -ne 1 -or $uiEntries[0] -cne $script:uiEnvironment) {
            throw 'New container does not expose exactly DESKTOP_COMMANDER_DISABLE_MCP_UI=1.'
        }
    } elseif ($uiEntries.Count -ne 0) {
        throw 'Active container unexpectedly overrides the MCP UI environment switch.'
    }
    $hc = $Info.HostConfig
    if ($hc.ReadonlyRootfs -ne $true -or $hc.Privileged -ne $false) {
        throw 'Read-only rootfs / non-privileged policy changed.'
    }
    # Docker inspect commonly serializes an unset CapAdd as JSON null. In PowerShell 5.1,
    # @($null).Count is 1, so filter null entries before checking for capability additions.
    $capDropAll = @($hc.CapDrop | Where-Object { $null -ne $_ -and ([string]$_) -ceq 'ALL' })
    $capAddEntries = @($hc.CapAdd | Where-Object { $null -ne $_ })
    if ($capDropAll.Count -ne 1 -or $capAddEntries.Count -ne 0) {
        $dropText = (@($hc.CapDrop | ForEach-Object { if ($null -eq $_) { '<null>' } else { [string]$_ } }) -join ',')
        $addText = (@($hc.CapAdd | ForEach-Object { if ($null -eq $_) { '<null>' } else { [string]$_ } }) -join ',')
        throw "Capabilities must remain fully dropped with no additions (CapDrop=[$dropText]; CapAdd=[$addText])."
    }
    $security = @($hc.SecurityOpt | ForEach-Object { [string]$_ })
    if (@($security | Where-Object { $_ -match '^no-new-privileges(?::true)?$' }).Count -ne 1 -or
        @($security | Where-Object { $_ -match '^(seccomp|apparmor)=unconfined$' }).Count -ne 0) {
        throw 'no-new-privileges or confined security policy changed.'
    }
    foreach ($field in @('Devices','DeviceRequests','VolumesFrom','GroupAdd','Binds')) {
        if (@(Get-Value $hc $field @() | Where-Object { $null -ne $_ }).Count -ne 0) {
            throw "Unexpected host device, inherited volume or bind setting: $field"
        }
    }
    # Docker inspect represents no published ports as either null or an empty JSON object ({}).
    # ConvertFrom-Json turns {} into an empty PSCustomObject, which is still one scalar in @(...).
    # Inspect its properties/keys instead; any actual port/protocol key remains a hard failure.
    $portBindings = Get-Value $hc 'PortBindings'
    $portBindingKeys = @()
    if ($null -ne $portBindings) {
        if ($portBindings -is [System.Collections.IDictionary]) {
            $portBindingKeys = @($portBindings.Keys)
        } elseif ($portBindings -is [System.Management.Automation.PSCustomObject]) {
            $portBindingKeys = @($portBindings.PSObject.Properties | ForEach-Object { $_.Name })
        } else {
            throw "Unexpected PortBindings representation: $($portBindings.GetType().FullName)"
        }
    }
    if ($portBindingKeys.Count -ne 0) {
        throw "Unexpected published port binding(s): $($portBindingKeys -join ', ')"
    }
    if ($hc.PublishAllPorts -eq $true) { throw 'PublishAllPorts must remain false.' }
    foreach ($field in @('PidMode','IpcMode','UTSMode','UsernsMode','CgroupnsMode')) {
        $mode = [string](Get-Value $hc $field '')
        if ($mode -notin @('', 'private')) { throw "Host namespace sharing is not allowed: $field" }
    }
    if ([long]$hc.Memory -ne 4294967296 -or [long]$hc.MemorySwap -ne 5368709120 -or
        [long]$hc.NanoCpus -ne 2000000000 -or [long]$hc.PidsLimit -ne 512 -or
        [long]$hc.ShmSize -ne 67108864 -or $hc.RestartPolicy.Name -cne 'unless-stopped') {
        throw 'Resource limits, shared memory or restart policy differ from the reviewed baseline.'
    }
    if ($hc.NetworkMode -cne 'fortis-repo-egress') { throw 'Primary network mode changed.' }
    $tmpfs = Get-Value $hc 'Tmpfs'
    # In Windows PowerShell 5.1, direct PSObject.Properties['/path'] lookup is unreliable
    # for Docker tmpfs keys containing slashes. Enumerate properties and compare names ordinally.
    $tmpfsProperties = @($tmpfs.PSObject.Properties)
    $homeEntries = @($tmpfsProperties | Where-Object { $_.Name -ceq '/home/node' })
    $tempEntries = @($tmpfsProperties | Where-Object { $_.Name -ceq '/tmp' })
    if ($homeEntries.Count -ne 1 -or
        [string]$homeEntries[0].Value -cne 'rw,nosuid,nodev,noexec,uid=1000,gid=1000,mode=700,size=128m' -or
        $tempEntries.Count -ne 1 -or
        [string]$tempEntries[0].Value -cne 'rw,nosuid,nodev,noexec,mode=1777,size=128m' -or
        $tmpfsProperties.Count -ne 2) {
        throw 'The exact reviewed /home/node and /tmp tmpfs contract changed.'
    }
    Assert-MountContract $Info
    if ($CheckNetworks) {
        $networkNames = @($Info.NetworkSettings.Networks.PSObject.Properties | ForEach-Object { $_.Name })
        Assert-StringSet $networkNames @('fortis-repo-egress','rdg-personal_agents') 'Attached Docker networks'
        foreach ($networkName in $networkNames) {
            $endpoint = $Info.NetworkSettings.Networks.PSObject.Properties[$networkName].Value
            $ipam = Get-Value $endpoint 'IPAMConfig'
            if ($null -ne $ipam -and
                (-not [string]::IsNullOrWhiteSpace([string](Get-Value $ipam 'IPv4Address' '')) -or
                 -not [string]::IsNullOrWhiteSpace([string](Get-Value $ipam 'IPv6Address' '')))) {
                throw "Static IPAM address on $networkName requires a separately reviewed cutover."
            }
            # Docker inspect may serialize an unset Links array as JSON null.
            # PowerShell 5.1 counts @($null) as one item; filter null/blank entries first.
            $links = Get-Value $endpoint 'Links'
            $legacyLinks = @($links | Where-Object {
                $null -ne $_ -and -not [string]::IsNullOrWhiteSpace([string]$_)
            })
            if ($legacyLinks.Count -ne 0) {
                throw "Legacy network links on $networkName are not supported: $($legacyLinks -join ', ')"
            }
        }
    }
}
function Read-ExactPipeBytes {
    param([System.IO.Stream]$Stream, [int]$Count)
    $buffer = New-Object byte[] $Count
    $offset = 0
    while ($offset -lt $Count) {
        $read = $Stream.Read($buffer,$offset,$Count-$offset)
        if ($read -le 0) { throw 'Docker named-pipe response ended unexpectedly.' }
        $offset += $read
    }
    return ,$buffer
}
function Read-PipeLine {
    param([System.IO.Stream]$Stream)
    $bytes = New-Object System.Collections.Generic.List[byte]
    while ($bytes.Count -lt 8192) {
        $value = $Stream.ReadByte()
        if ($value -lt 0) { throw 'Docker named-pipe response ended inside a header.' }
        if ($value -eq 10) { break }
        $bytes.Add([byte]$value)
    }
    return [Text.Encoding]::ASCII.GetString($bytes.ToArray()).TrimEnd([char]13)
}
function Read-DockerHttpResponse {
    param([System.IO.Stream]$Stream)
    $headerBytes = New-Object System.Collections.Generic.List[byte]
    $delimiterFound = $false
    while ($headerBytes.Count -lt 65536) {
        $value = $Stream.ReadByte()
        if ($value -lt 0) { throw 'Docker API returned no complete HTTP headers.' }
        $headerBytes.Add([byte]$value)
        $n = $headerBytes.Count
        if ($n -ge 4) {
            $tail = [Text.Encoding]::ASCII.GetString($headerBytes.ToArray(),$n-4,4)
            if ($tail -ceq ([string][char]13 + [char]10 + [char]13 + [char]10)) {
                $delimiterFound = $true
                break
            }
        }
    }
    if (-not $delimiterFound) { throw 'Docker API HTTP headers exceeded the safety limit.' }
    $headerText = [Text.Encoding]::ASCII.GetString($headerBytes.ToArray())
    $lines = $headerText -split ([string][char]13 + [char]10)
    if ($lines[0] -notmatch '^HTTP/\d\.\d\s+(\d{3})') { throw 'Docker API returned an invalid HTTP status line.' }
    $statusCode = [int]$Matches[1]
    $headers = @{}
    foreach ($line in $lines | Select-Object -Skip 1) {
        if ($line -match '^([^:]+):\s*(.*)$') { $headers[$Matches[1].ToLowerInvariant()] = $Matches[2] }
    }
    $bodyBytes = New-Object byte[] 0
    if ($headers.ContainsKey('content-length')) {
        $bodyBytes = Read-ExactPipeBytes $Stream ([int]$headers['content-length'])
    } elseif ($headers.ContainsKey('transfer-encoding') -and $headers['transfer-encoding'] -match 'chunked') {
        $memory = New-Object System.IO.MemoryStream
        while ($true) {
            $sizeLine = Read-PipeLine $Stream
            $sizeToken = ($sizeLine -split ';')[0]
            $size = [Convert]::ToInt32($sizeToken,16)
            if ($size -eq 0) {
                while ((Read-PipeLine $Stream) -ne '') {}
                break
            }
            $chunk = Read-ExactPipeBytes $Stream $size
            $memory.Write($chunk,0,$chunk.Length)
            $null = Read-ExactPipeBytes $Stream 2
        }
        $bodyBytes = $memory.ToArray()
        $memory.Dispose()
    }
    $body = [Text.Encoding]::UTF8.GetString($bodyBytes)
    return [pscustomobject]@{StatusCode=$statusCode;Body=$body}
}
function Invoke-DockerEngineCreate {
    param([string]$PipeName, [string]$ApiVersion, [string]$Name, [string]$JsonBody)
    $pipe = New-Object System.IO.Pipes.NamedPipeClientStream('.', $PipeName, [IO.Pipes.PipeDirection]::InOut, [IO.Pipes.PipeOptions]::None)
    try {
        $pipe.Connect(10000)
        $bodyBytes = [Text.Encoding]::UTF8.GetBytes($JsonBody)
        $path = '/v' + $ApiVersion + '/containers/create?name=' + [Uri]::EscapeDataString($Name)
        $crlf = [string][char]13 + [char]10
        $header = 'POST ' + $path + ' HTTP/1.1' + $crlf + 'Host: docker' + $crlf +
            'Content-Type: application/json' + $crlf + 'Content-Length: ' + $bodyBytes.Length +
            $crlf + 'Connection: close' + $crlf + $crlf
        $headerBytes = [Text.Encoding]::ASCII.GetBytes($header)
        $pipe.Write($headerBytes,0,$headerBytes.Length)
        $pipe.Write($bodyBytes,0,$bodyBytes.Length)
        $pipe.Flush()
        $response = Read-DockerHttpResponse $pipe
        if ($response.StatusCode -ne 201) {
            throw "Docker Engine create API returned HTTP $($response.StatusCode): $($response.Body)"
        }
        return (ConvertFrom-Json -InputObject $response.Body -ErrorAction Stop)
    } finally {
        $pipe.Dispose()
    }
}
function Assert-NameAbsent {
    param([string]$Name)
    $names = Invoke-Docker @('ps','-a','--format','{{.Names}}')
    if (@($names | Where-Object { ([string]$_).Trim() -ceq $Name }).Count -ne 0) {
        throw "Container name already exists; refusing to overwrite: $Name"
    }
}
function Get-CustomAliases {
    param($Endpoint, [string]$OldId, [string]$OldName, [string]$Hostname)
    $defaults = @($OldName,$OldId,$OldId.Substring(0,12),$Hostname) | Where-Object { $_ }
    @((Get-Value $Endpoint 'Aliases' @()) | Where-Object { $_ -and $_ -cnotin $defaults })
}
function Invoke-Rollback {
    param([string]$Reason, [bool]$OldRenamed, [bool]$NewRenamed, [bool]$StageCreated)
    try {
        if ($NewRenamed) {
            $newInfo = Get-ContainerInspect $containerName
            if ($newInfo.State.Running) { Invoke-Docker @('stop','--time','20',$containerName) | Out-Null }
            Invoke-Docker @('rename',$containerName,$failedName) | Out-Null
        } elseif ($StageCreated) {
            $stageInfo = Get-ContainerInspect $stageName
            if ($stageInfo.State.Running) { Invoke-Docker @('stop','--time','20',$stageName) | Out-Null }
            Invoke-Docker @('rm',$stageName) | Out-Null
        }
        if ($OldRenamed) { Invoke-Docker @('rename',$rollbackName,$containerName) | Out-Null }
        $restored = Get-ContainerInspect $containerName
        if ($restored.Id -cne $expectedActiveId) { throw 'Rollback container ID does not match the original active ID.' }
        if (-not $restored.State.Running) { Invoke-Docker @('start',$containerName) | Out-Null }
        $restored = Get-ContainerInspect $containerName
        if (-not $restored.State.Running -or $restored.Image -cne $expectedBaseImageId) {
            throw 'Original container did not return to its verified running/base-image state.'
        }
        throw "CUTOVER_FAILED_ROLLBACK_PASS: $Reason"
    } catch {
        if ($_.Exception.Message -like 'CUTOVER_FAILED_ROLLBACK_PASS:*') { throw }
        throw "CUTOVER_FAILED_ROLLBACK_FAILED: $Reason ; $($_.Exception.Message). Preserve all containers and volumes for manual recovery."
    }
}

Write-Host '=== READ-ONLY CUTOVER PREFLIGHT ==='
$active = Get-ContainerInspect $containerName
if ($active.Id -cne $expectedActiveId -or -not $active.State.Running) {
    throw 'Active container identity/state changed; no cutover performed.'
}
if ($active.Config.Image -notin @($baseImage,$expectedBaseImageId) -or $active.Image -cne $expectedBaseImageId) {
    throw 'Active container is not on the reviewed path-guidance base image.'
}
if (-not [string]::IsNullOrWhiteSpace([string]$active.Config.MacAddress)) {
    throw 'An explicitly configured container MAC address requires a separately reviewed cutover.'
}
$base = Get-ImageInspect $baseImage
$candidate = Get-ImageInspect $candidateImage
if ($base.Id -cne $expectedBaseImageId -or $candidate.Id -cne $expectedCandidateId) {
    throw 'Base or candidate image tag no longer resolves to its reviewed immutable ID.'
}
if ($candidate.Config.User -cne $base.Config.User -or
    $candidate.Config.WorkingDir -cne $base.Config.WorkingDir -or
    (ConvertTo-Json -InputObject $candidate.Config.Cmd -Compress -Depth 10) -cne (ConvertTo-Json -InputObject $base.Config.Cmd -Compress -Depth 10) -or
    (ConvertTo-Json -InputObject $candidate.Config.Entrypoint -Compress -Depth 10) -cne (ConvertTo-Json -InputObject $base.Config.Entrypoint -Compress -Depth 10)) {
    throw 'Candidate changed the base image user, workdir, command or entrypoint.'
}
$baseEnv = @($base.Config.Env | ForEach-Object { [string]$_ })
$candidateEnv = @($candidate.Config.Env | ForEach-Object { [string]$_ })
Assert-StringSet $candidateEnv (@($baseEnv) + $uiEnvironment) 'Candidate image environment'
Assert-StringSet @($active.Config.Env | ForEach-Object { [string]$_ }) $baseEnv 'Active container/base environment'
Assert-ContainerContract $active $containerName $expectedBaseImageId $false $true
$oldRollback = Get-ContainerInspect $oldRollbackName
if ($oldRollback.Id -cne $expectedOldRollbackId -or $oldRollback.State.Running) {
    throw 'The existing pre-path-guidance rollback is missing, changed or running.'
}
Assert-NameAbsent $rollbackName
Assert-NameAbsent $stageName
Assert-NameAbsent $failedName
$networks = $active.NetworkSettings.Networks
$primaryEndpoint = $networks.PSObject.Properties['fortis-repo-egress'].Value
$secondaryEndpoint = $networks.PSObject.Properties['rdg-personal_agents'].Value
if ($null -eq $primaryEndpoint -or $null -eq $secondaryEndpoint) { throw 'Expected network endpoint metadata is missing.' }
$primaryAliases = Get-CustomAliases $primaryEndpoint $active.Id $containerName $active.Config.Hostname
if ($primaryAliases.Count -ne 0) { throw 'Custom aliases on the primary network require a separately reviewed cutover.' }
$secondaryAliases = Get-CustomAliases $secondaryEndpoint $active.Id $containerName $active.Config.Hostname
$secondaryNetwork = @(ConvertFrom-Json -InputObject ((Invoke-Docker @('network','inspect','rdg-personal_agents')) -join [Environment]::NewLine))[0]
if ($secondaryNetwork.Driver -cne 'bridge' -or $secondaryNetwork.Internal -ne $true) {
    throw 'rdg-personal_agents must remain an internal bridge network.'
}
$contextName = ((Invoke-Docker @('context','show')) -join '').Trim()
$context = @(ConvertFrom-Json -InputObject ((Invoke-Docker @('context','inspect',$contextName)) -join [Environment]::NewLine))[0]
$dockerHost = [string]$context.Endpoints.docker.Host
if ($dockerHost -notmatch '^npipe:////\./pipe/(?<PipeName>[^/]+)$') {
    throw "Expected a Windows Docker named-pipe context; found '$dockerHost'."
}
$pipeName = $Matches.PipeName
$apiVersion = ((Invoke-Docker @('version','--format','{{.Server.APIVersion}}')) -join '').Trim()
if ($apiVersion -notmatch '^\d+\.\d+$') { throw 'Could not determine Docker Engine API version.' }
Write-Host "Active container: $($active.Id)"
Write-Host "Rollback target:  $rollbackName"
Write-Host "Candidate image:  $($candidate.Id)"
Write-Host 'Networks:         fortis-repo-egress; rdg-personal_agents'
Write-Host 'PREFLIGHT_PASS; no container lifecycle or volume operation performed.'
if ($Action -eq 'Preview') { return }
$confirmation = Read-Host 'Type CUTOVER MCP UI HEADLESS to replace the shared Repo1/Repo2/Qwen container'
if ($confirmation -cne 'CUTOVER MCP UI HEADLESS') { throw 'Owner confirmation missing; no cutover performed.' }
Write-Warning 'This will interrupt Repo1, Repo2, Qwen and this Fortis MCP connection. Keep this PowerShell window open.'
$stageCreated = $false
$oldRenamed = $false
$newRenamed = $false
$newContainerId = $null
try {
    # Clone the inspected container Config and HostConfig through the Docker Engine API.
    # No --volumes-from, host bind, volume deletion, image pull or compose action is used.
    $payload = [ordered]@{}
    foreach ($property in $active.Config.PSObject.Properties) {
        $payload[$property.Name] = $property.Value
    }
    $payload['Image'] = $candidate.Id
    # Docker inspect reports the old generated hostname as Config.Hostname; let the new ID generate its own default.
    if ([string]$active.Config.Hostname -ceq $active.Id.Substring(0,12)) { $payload['Hostname'] = '' }
    $payload['HostConfig'] = $active.HostConfig
    $jsonBody = ConvertTo-Json -InputObject $payload -Depth 100 -Compress
    $created = Invoke-DockerEngineCreate $pipeName $apiVersion $stageName $jsonBody
    if ([string]$created.Id -notmatch '^[0-9a-f]{64}$') { throw 'Docker Engine did not return a full staged container ID.' }
    $stageCreated = $true
    $newContainerId = [string]$created.Id
    $staged = Get-ContainerInspect $stageName
    if ($staged.Id -cne $newContainerId) { throw 'Staged container ID changed after create.' }
    Assert-ContainerContract $staged $stageName $expectedCandidateId $true $false
    Assert-StringSet @($staged.Config.Env | ForEach-Object { [string]$_ }) (@($active.Config.Env | ForEach-Object { [string]$_ }) + $uiEnvironment) 'Staged container environment'
    Write-Host "STAGED_CONTAINER_PASS: $newContainerId"
    # Stop the active service only after the stopped candidate container is fully created and inspected.
    Invoke-Docker @('stop','--time','30',$containerName) | Out-Null
    $stopped = Get-ContainerInspect $containerName
    if ($stopped.Id -cne $expectedActiveId -or $stopped.State.Running) {
        throw 'Original container did not stop cleanly; entering rollback.'
    }
    Invoke-Docker @('rename',$containerName,$rollbackName) | Out-Null
    $oldRenamed = $true
    Invoke-Docker @('rename',$stageName,$containerName) | Out-Null
    $newRenamed = $true
    # The primary egress network is restored from HostConfig.NetworkMode.
    # Reattach the optional internal network and preserve any non-default aliases.
    $connectArgs = @('network','connect')
    foreach ($alias in $secondaryAliases) { $connectArgs += @('--alias',[string]$alias) }
    $connectArgs += @('rdg-personal_agents',$containerName)
    Invoke-Docker $connectArgs | Out-Null
    Invoke-Docker @('start',$containerName) | Out-Null
    $live = Get-ContainerInspect $containerName
    if (-not $live.State.Running) { throw 'Candidate container did not reach running state.' }
    Assert-ContainerContract $live $containerName $expectedCandidateId $true $true
    $envValue = ((Invoke-Docker @('exec','--user','1000:1000',$containerName,'/usr/local/bin/node','-p','process.env.DESKTOP_COMMANDER_DISABLE_MCP_UI')) -join '').Trim()
    if ($envValue -cne '1') { throw 'Live container process environment does not expose the UI opt-out.' }
    $runtimeTest = Invoke-Docker @('exec','--user','1000:1000',$containerName,'/usr/local/bin/node','/workspace/repos/fortis-container/patches/desktop-commander-0.2.52-mcp-ui-headless/test-mcp-ui-headless.mjs','/opt/dc/node_modules/@wonderwhy-er/desktop-commander')
    if (@($runtimeTest | Where-Object { ([string]$_) -match 'PASS: UI metadata decision, resources/list, resource reads' }).Count -ne 1) {
        throw 'Live Desktop Commander package runtime test did not emit its success marker.'
    }
    Write-Host 'LIVE_MCP_UI_RUNTIME_PASS'
    # Run canonical read-only Repo1/Repo2 Guard Previews against the new full container ID.
    $dispatcher = Join-Path $env:USERPROFILE 'Repos\tunnel\runtime\windows-repo\Invoke-FortisRepo.ps1'
    if (-not (Test-Path -LiteralPath $dispatcher -PathType Leaf)) { throw 'Canonical Tunnel Repo dispatcher is missing.' }

    # A fresh /home/node tmpfs starts empty after container recreation.
    # First use the canonical dispatcher to validate the paired source and inspect the new ID.
    $initialRepo2 = @(& $dispatcher -Repo Repo2 -Action Preview 2>&1)
    if (-not $?) { throw 'Initial Repo2 read-only Guard Preview failed.' }
    $initialRepo2Text = $initialRepo2 -join [Environment]::NewLine
    if (($initialRepo2Text -notmatch '"Preflight"\s*:\s*"(PASS|REBOOT_REPAIR_REQUIRED)"') -or
        $initialRepo2Text -notmatch ('"ContainerId"\s*:\s*"' + [regex]::Escape($newContainerId) + '"') -or
        $initialRepo2Text -notmatch ('"ImageId"\s*:\s*"' + [regex]::Escape($expectedCandidateId) + '"')) {
        throw 'Initial Repo2 Preview did not identify the new container/image or reported unexpected drift.'
    }

    # The canonical Repo2 Direct Guard repairs only a recognized missing/factory-default tmpfs config.
    # It does not start a tunnel. Verify its source hash against the manifest after dispatcher validation.
    $currentRoot = Join-Path $env:USERPROFILE 'Repos\tunnel\runtime\windows-repo\current'
    $manifestPath = Join-Path $currentRoot 'source-manifest.json'
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $guardRelative = 'launchers/FortisRepoPlus2/Repo2DirectGuard.ps1'
    $guardEntry = @($manifest.files | Where-Object { $_.path -ceq $guardRelative })
    $repo2Guard = Join-Path $currentRoot 'launchers\FortisRepoPlus2\Repo2DirectGuard.ps1'
    if ($guardEntry.Count -ne 1 -or -not (Test-Path -LiteralPath $repo2Guard -PathType Leaf) -or
        (Get-FileHash -LiteralPath $repo2Guard -Algorithm SHA256).Hash -cne $guardEntry[0].sha256) {
        throw 'Repo2 Direct Guard source hash differs from the canonical source manifest.'
    }
    $repairOutput = @(& $repo2Guard -Mode Run -ContainerId $newContainerId 2>&1)
    if (-not $? -or @($repairOutput | Where-Object { ([string]$_) -ceq ('REPO2_DIRECT_GUARD_PASS:' + $newContainerId) }).Count -ne 1) {
        throw 'Guarded tmpfs runtime-config bootstrap did not pass; no tunnel was started.'
    }
    Write-Host 'GUARDED_RUNTIME_CONFIG_REPAIR_PASS'

    foreach ($repo in @('Repo1','Repo2')) {
        $guardOutput = @(& $dispatcher -Repo $repo -Action Preview 2>&1)
        if (-not $?) { throw "$repo canonical Guard Preview failed." }
        $guardText = $guardOutput -join [Environment]::NewLine
        if ($guardText -notmatch '"Preflight"\s*:\s*"PASS"' -or
            $guardText -notmatch ('"ContainerId"\s*:\s*"' + [regex]::Escape($newContainerId) + '"') -or
            $guardText -notmatch ('"ImageId"\s*:\s*"' + [regex]::Escape($expectedCandidateId) + '"')) {
            throw "$repo Guard Preview did not report PASS for the new container and candidate image."
        }
        Write-Host "$($repo.ToUpperInvariant())_GUARD_PREVIEW_PASS"
    }
    $finalRollback = Get-ContainerInspect $rollbackName
    if ($finalRollback.Id -cne $expectedActiveId -or $finalRollback.State.Running) {
        throw 'The original path-guidance container was not preserved as a stopped rollback.'
    }
    Write-Host 'DOCKER_CUTOVER_PASS'
    Write-Host 'LIVE_MCP_DISCOVERY_PENDING; REPO1_REPO2_RECONNECT_PENDING; QWEN_RECONNECT_PENDING'
    Write-Host "New container ID: $newContainerId"
    Write-Host "Rollback container: $rollbackName"
    Write-Host 'No named volume was deleted. No Windows profile or tunnel lifecycle action was requested.'
} catch {
    $failure = $_.Exception.Message
    Write-Warning "Cutover failed: $failure"
    Invoke-Rollback $failure $oldRenamed $newRenamed $stageCreated
}
