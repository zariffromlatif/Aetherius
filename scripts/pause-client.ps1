param(
    [Parameter(Mandatory = $true)][string]$ClientId,
    [switch]$CloseOpenSignals
)

$ErrorActionPreference = "Stop"

Set-Location -Path "e:\Aetherius-Quant"

Write-Host "Pausing client: $ClientId" -ForegroundColor Cyan

docker compose -f docker/docker-compose.yml exec -T db `
  psql -U postgres -d aetherius -c "
  UPDATE clients
  SET status = 'paused', updated_at = NOW()
  WHERE id = '$ClientId';

  UPDATE client_configs
  SET active = FALSE, updated_at = NOW()
  WHERE client_id = '$ClientId';

  UPDATE briefing_runs
  SET status = 'suppressed', updated_at = NOW()
  WHERE client_id = '$ClientId'
    AND status IN ('draft','pending_review','approved');
"

if ($CloseOpenSignals) {
    docker compose -f docker/docker-compose.yml exec -T db `
      psql -U postgres -d aetherius -c "
      UPDATE risk_signals
      SET status = 'closed', updated_at = NOW()
      WHERE client_id = '$ClientId' AND status = 'open';
    "
}

Write-Host "Verification:" -ForegroundColor Yellow
docker compose -f docker/docker-compose.yml exec -T db `
  psql -U postgres -d aetherius -c "
  SELECT id, name, status FROM clients WHERE id = '$ClientId';
  SELECT client_id, active FROM client_configs WHERE client_id = '$ClientId';
  SELECT status, count(*) FROM briefing_runs
  WHERE client_id = '$ClientId'
  GROUP BY status ORDER BY status;
"

Write-Host "Client paused successfully." -ForegroundColor Green
