param(
    [string]$ProjectRoot = "e:\Aetherius-Quant",
    [string]$AdminEmail = "admin@example.com",
    [string]$AdminPassword = "Passw0rd!",
    [string]$DemoRecipient = "pilot.operator@example.com",
    [switch]$SkipMigrations
)

$ErrorActionPreference = "Stop"

function Write-Step($msg) {
    Write-Host ""
    Write-Host "=== $msg ===" -ForegroundColor Cyan
}

function Invoke-Api {
    param(
        [Parameter(Mandatory=$true)][ValidateSet("GET","POST","PUT","DELETE")] [string]$Method,
        [Parameter(Mandatory=$true)][string]$Uri,
        [hashtable]$Headers,
        [object]$Body
    )
    if ($null -ne $Body) {
        return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $Headers -ContentType "application/json" -Body ($Body | ConvertTo-Json -Depth 10)
    }
    return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $Headers
}

$base = "http://localhost:8000"

Write-Step "1) Start local docker stack"
Set-Location -Path $ProjectRoot
docker compose -f docker/docker-compose.yml up -d
docker compose -f docker/docker-compose.yml ps

Write-Step "2) Run migrations (optional)"
if (-not $SkipMigrations) {
    Set-Location -Path (Join-Path $ProjectRoot "aetherius")
    $env:PYTHONPATH = (Join-Path $ProjectRoot "aetherius")
    python -m alembic -c alembic.ini upgrade head
    Set-Location -Path $ProjectRoot
} else {
    Write-Host "Skipped migrations due to -SkipMigrations switch."
}

Write-Step "3) Health check"
$health = Invoke-Api -Method GET -Uri "$base/health"
$health | ConvertTo-Json

Write-Step "4) Bootstrap admin (first run) + login"
try {
    $bootstrap = @{
        email     = $AdminEmail
        full_name = "Pilot Admin"
        password  = $AdminPassword
    }
    $bootstrapResp = Invoke-Api -Method POST -Uri "$base/api/v1/auth/bootstrap-admin" -Body $bootstrap
    Write-Host "Bootstrap admin response:"
    $bootstrapResp | ConvertTo-Json
}
catch {
    Write-Host "Bootstrap skipped/failed (usually expected after first run): $($_.Exception.Message)" -ForegroundColor Yellow
}

$loginBody = @{
    email    = $AdminEmail
    password = $AdminPassword
}
$loginResp = Invoke-Api -Method POST -Uri "$base/api/v1/auth/login" -Body $loginBody
$token = $loginResp.access_token
$authHeaders = @{ Authorization = "Bearer $token" }

Write-Step "5) Create client + watchlist + items"
$clientResp = Invoke-Api -Method POST -Uri "$base/api/v1/clients/quick-create" -Headers $authHeaders -Body @{
    name     = "Pilot Fund $(Get-Date -Format 'yyyyMMdd-HHmmss')"
    status   = "active"
    timezone = "America/New_York"
}

$clientId = $clientResp.config.client_id
Write-Host "Client ID: $clientId"

$watchlistResp = Invoke-Api -Method POST -Uri "$base/api/v1/watchlists" -Headers $authHeaders -Body @{
    client_id = $clientId
    name      = "Pilot Watchlist"
    active    = $true
}
$watchlistId = $watchlistResp.id
Write-Host "Watchlist ID: $watchlistId"

$nvda = Invoke-Api -Method POST -Uri "$base/api/v1/watchlists/items" -Headers $authHeaders -Body @{
    watchlist_id  = $watchlistId
    ticker        = "NVDA"
    company_name  = "NVIDIA"
    priority_level= "high"
    book_context  = "core_position"
}
$amd = Invoke-Api -Method POST -Uri "$base/api/v1/watchlists/items" -Headers $authHeaders -Body @{
    watchlist_id  = $watchlistId
    ticker        = "AMD"
    company_name  = "Advanced Micro Devices"
    priority_level= "normal"
    book_context  = "near_book"
}

Invoke-Api -Method POST -Uri "$base/api/v1/watchlists/relationships" -Headers $authHeaders -Body @{
    watchlist_item_id    = $nvda.id
    related_entity_name  = "Advanced Micro Devices"
    related_ticker       = "AMD"
    relationship_type    = "peer"
    strength             = 0.55
}

Write-Step "6) Ingest observation"
$obsResp = Invoke-Api -Method POST -Uri "$base/api/v1/observations" -Headers $authHeaders -Body @{
    source_type       = "news"
    source_name       = "TestFeed"
    source_url        = "https://example.com/article"
    title             = "Hyperscalers slow AI capex"
    raw_text          = "Microsoft signals slower AI capex growth. NVIDIA (NVDA) read-through risk; AMD (AMD) peer readthrough."
    source_confidence = 0.9
}
$obsResp | ConvertTo-Json

Write-Step "7) Generate signals from newest evidence links (DB lookup)"
$evidenceIds = docker compose -f docker/docker-compose.yml exec -T db psql -U postgres -d aetherius -t -A -c "select id from evidence_links order by created_at desc limit 2;"
$evidenceIdList = $evidenceIds -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
foreach ($eid in $evidenceIdList) {
    Invoke-Api -Method POST -Uri "$base/api/v1/signals/from-evidence/$eid" -Headers $authHeaders | Out-Null
}

$signals = Invoke-Api -Method GET -Uri "$base/api/v1/signals?client_id=$clientId" -Headers $authHeaders
Write-Host "Signals generated: $($signals.Count)"

Write-Step "8) Draft, approve, and send daily brief"
$draftRun = Invoke-Api -Method POST -Uri "$base/api/v1/review/drafts/daily/$clientId" -Headers $authHeaders
$briefId = $draftRun.id
if (-not $briefId) {
    $queue = Invoke-Api -Method GET -Uri "$base/api/v1/review/queue" -Headers $authHeaders
    $briefId = $queue[0].id
}
Write-Host "Briefing ID: $briefId"

Invoke-Api -Method POST -Uri "$base/api/v1/review/briefings/$briefId/action" -Headers $authHeaders -Body @{
    action_type = "approve"
    reason      = "Local smoke test"
} | Out-Null

$sendHeaders = @{
    Authorization = "Bearer $token"
    "x-client-scope" = $clientId
}
$delivery = Invoke-Api -Method POST -Uri "$base/api/v1/delivery/briefings/$briefId" -Headers $sendHeaders -Body @{
    recipient = $DemoRecipient
    channel   = "email"
}
$delivery | ConvertTo-Json

Write-Step "9) Reporting + ops checks"
$weekly = Invoke-Api -Method GET -Uri "$base/api/v1/reporting/weekly/$clientId" -Headers $authHeaders
$pilot  = Invoke-Api -Method GET -Uri "$base/api/v1/reporting/pilot/$clientId" -Headers $authHeaders
$ops    = Invoke-Api -Method GET -Uri "$base/api/v1/ops/metrics" -Headers $authHeaders

Write-Host "Weekly report:"; $weekly | ConvertTo-Json
Write-Host "Pilot report:";  $pilot  | ConvertTo-Json
Write-Host "Ops metrics:";   $ops    | ConvertTo-Json

Write-Step "10) Mailpit inbox hint"
Write-Host "Open Mailpit UI: http://localhost:8025"
Write-Host "You should see subject: 'Aetherius Brief - daily_brief' if local SMTP succeeded."

Write-Step "Done"
Write-Host "Local readiness flow completed."
