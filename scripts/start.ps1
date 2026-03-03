# PowerShell start script for Windows
param()

$imageName = 'pm-app'
$containerName = 'pm-app'

# compute project root relative to this script
$scriptPath = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
$projectRoot = Split-Path -Path $scriptPath -Parent

Write-Host "Building Docker image..."
docker build -t $imageName $projectRoot

$existing = docker ps -a --format "{{.Names}}" | Where-Object {$_ -eq $containerName}
if ($existing) {
    Write-Host "Removing existing container $containerName"
    docker rm -f $containerName | Out-Null
}

Write-Host "Running container..."
docker run --name $containerName -p 8000:8000 -d $imageName
Write-Host "Container started on http://localhost:8000"