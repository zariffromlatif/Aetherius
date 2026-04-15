CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS clients (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  status TEXT NOT NULL,
  timezone TEXT NOT NULL DEFAULT 'America/New_York',
  primary_contact_name TEXT,
  primary_contact_email TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS operator_users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT NOT NULL UNIQUE,
  full_name TEXT,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'viewer',
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS client_configs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  client_id UUID NOT NULL REFERENCES clients(id),
  alert_mode TEXT NOT NULL,
  daily_brief_time TIME,
  daily_brief_delivery_channel TEXT,
  urgent_alert_channel TEXT,
  scenario_frequency_per_week INT NOT NULL DEFAULT 2,
  brief_tone TEXT NOT NULL DEFAULT 'institutional_concise',
  focus_tags JSONB,
  high_priority_event_types JSONB,
  urgent_alert_threshold NUMERIC,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS watchlists (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  client_id UUID NOT NULL REFERENCES clients(id),
  name TEXT NOT NULL,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS watchlist_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  watchlist_id UUID NOT NULL REFERENCES watchlists(id),
  ticker TEXT NOT NULL,
  company_name TEXT NOT NULL,
  sector TEXT,
  industry TEXT,
  priority_level TEXT NOT NULL,
  book_context TEXT NOT NULL,
  notes TEXT,
  custom_tags JSONB,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS entity_relationships (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  watchlist_item_id UUID NOT NULL REFERENCES watchlist_items(id),
  related_entity_name TEXT NOT NULL,
  related_ticker TEXT,
  relationship_type TEXT NOT NULL,
  strength NUMERIC,
  notes TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS company_aliases (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  canonical_name TEXT NOT NULL,
  alias TEXT NOT NULL UNIQUE,
  ticker TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS source_observations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_type TEXT NOT NULL,
  source_name TEXT NOT NULL,
  source_url TEXT,
  published_at TIMESTAMP,
  observed_at TIMESTAMP NOT NULL,
  ingested_at TIMESTAMP NOT NULL,
  content_hash TEXT NOT NULL,
  title TEXT,
  raw_text TEXT NOT NULL,
  structured_payload JSONB,
  source_confidence NUMERIC,
  freshness_score NUMERIC,
  dedupe_key TEXT,
  ingestion_status TEXT NOT NULL DEFAULT 'ingested',
  stale BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_source_observations_content_hash ON source_observations(content_hash);
CREATE INDEX IF NOT EXISTS idx_source_observations_dedupe_key ON source_observations(dedupe_key);

CREATE TABLE IF NOT EXISTS observation_entities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  observation_id UUID NOT NULL REFERENCES source_observations(id),
  entity_name TEXT NOT NULL,
  ticker TEXT,
  entity_type TEXT NOT NULL,
  match_confidence NUMERIC,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS evidence_links (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  observation_id UUID NOT NULL REFERENCES source_observations(id),
  watchlist_item_id UUID NOT NULL REFERENCES watchlist_items(id),
  relationship_type TEXT,
  relevance_score NUMERIC NOT NULL,
  evidence_summary TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS risk_signals (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  client_id UUID NOT NULL REFERENCES clients(id),
  watchlist_item_id UUID NOT NULL REFERENCES watchlist_items(id),
  signal_type TEXT NOT NULL,
  severity_level TEXT NOT NULL,
  confidence_level TEXT NOT NULL,
  risk_score NUMERIC NOT NULL,
  urgency_score NUMERIC NOT NULL,
  brief_priority_score NUMERIC NOT NULL,
  headline TEXT NOT NULL,
  why_it_matters TEXT NOT NULL,
  pathway TEXT,
  watch_next TEXT,
  invalidation_trigger TEXT,
  status TEXT NOT NULL DEFAULT 'open',
  generated_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS signal_evidence_refs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  risk_signal_id UUID NOT NULL REFERENCES risk_signals(id),
  evidence_link_id UUID NOT NULL REFERENCES evidence_links(id),
  rank_order INT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS briefing_runs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  client_id UUID NOT NULL REFERENCES clients(id),
  run_type TEXT NOT NULL,
  status TEXT NOT NULL,
  scheduled_for TIMESTAMP,
  generated_at TIMESTAMP,
  approved_at TIMESTAMP,
  sent_at TIMESTAMP,
  operator_user_id UUID,
  version INT NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS briefing_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  briefing_run_id UUID NOT NULL REFERENCES briefing_runs(id),
  watchlist_item_id UUID REFERENCES watchlist_items(id),
  section_type TEXT NOT NULL,
  display_order INT NOT NULL,
  title TEXT,
  body TEXT NOT NULL,
  severity_level TEXT,
  confidence_level TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS briefing_evidence_refs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  briefing_item_id UUID NOT NULL REFERENCES briefing_items(id),
  risk_signal_id UUID REFERENCES risk_signals(id),
  observation_id UUID REFERENCES source_observations(id),
  rank_order INT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS deliveries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  briefing_run_id UUID NOT NULL REFERENCES briefing_runs(id),
  channel TEXT NOT NULL,
  recipient TEXT NOT NULL,
  delivery_status TEXT NOT NULL,
  provider_message_id TEXT,
  attempt_count INT NOT NULL DEFAULT 0,
  last_attempt_at TIMESTAMP,
  error_message TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS client_feedback (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  client_id UUID NOT NULL REFERENCES clients(id),
  briefing_run_id UUID REFERENCES briefing_runs(id),
  feedback_type TEXT NOT NULL,
  feedback_text TEXT,
  recorded_by TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS operator_actions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  briefing_run_id UUID NOT NULL REFERENCES briefing_runs(id),
  action_type TEXT NOT NULL,
  operator_user_id UUID,
  before_payload JSONB,
  after_payload JSONB,
  reason TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
