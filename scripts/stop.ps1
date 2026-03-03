# PowerShell stop script for Windows
param()

$containerName = 'pm-app'

$existing = docker ps -a --format "{{.Names}}" | Where-Object {$_ -eq $containerName}
if ($existing) {
    Write-Host "Stopping and removing container $containerName"
    docker rm -f $containerName | Out-Null
} else {
    Write-Host "No container named $containerName found"
}
