param(
    [Parameter(Mandatory = $true)][string]$ClientId
)

$ErrorActionPreference = "Stop"

Set-Location -Path "e:\Aetherius-Quant"

Write-Host "Resuming client: $ClientId" -ForegroundColor Cyan

docker compose -f docker/docker-compose.yml exec -T db `
  psql -U postgres -d aetherius -c "
  UPDATE clients
  SET status = 'active', updated_at = NOW()
  WHERE id = '$ClientId';

  UPDATE client_configs
  SET active = TRUE, updated_at = NOW()
  WHERE client_id = '$ClientId';
"

Write-Host "Verification:" -ForegroundColor Yellow
docker compose -f docker/docker-compose.yml exec -T db `
  psql -U postgres -d aetherius -c "
  SELECT id, name, status FROM clients WHERE id = '$ClientId';
  SELECT client_id, active FROM client_configs WHERE client_id = '$ClientId';
"

Write-Host "Client resumed successfully." -ForegroundColor Green
