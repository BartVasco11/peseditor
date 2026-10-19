-- PESEditor football knowledge domains (non-canonical data only).
-- Supabase remains the canonical store for canonical players and canonical staff.
-- Apply to the Neon football_rag schema after database quota/access is restored.
-- This migration is additive and deliberately does not move or delete existing records.

CREATE SCHEMA IF NOT EXISTS football_rag;

CREATE TABLE IF NOT EXISTS football_rag.game_catalog (
  game_id BIGSERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  publisher TEXT,
  developer TEXT,
  platform TEXT,
  release_year SMALLINT,
  edition TEXT,
  region TEXT,
  language TEXT,
  source_url TEXT,
  notes TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS game_catalog_identity_idx
  ON football_rag.game_catalog (lower(title), coalesce(platform, ''), coalesce(release_year, 0), coalesce(edition, ''), coalesce(region, ''));

CREATE TABLE IF NOT EXISTS football_rag.alternative_player_records (
  record_id BIGSERIAL PRIMARY KEY,
  canonical_player_id BIGINT,
  player_name TEXT NOT NULL,
  nation TEXT,
  version_label TEXT NOT NULL,
  game_title TEXT,
  season_label TEXT,
  source_type TEXT NOT NULL DEFAULT 'editorial',
  attributes JSONB NOT NULL DEFAULT '{}'::jsonb,
  complementary_data JSONB NOT NULL DEFAULT '{}'::jsonb,
  special_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
  playing_styles JSONB NOT NULL DEFAULT '[]'::jsonb,
  source_urls JSONB NOT NULL DEFAULT '[]'::jsonb,
  review_status TEXT NOT NULL DEFAULT 'draft'
    CHECK (review_status IN ('draft','in_review','approved','rejected','archived')),
  provenance JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS alternative_player_records_name_idx
  ON football_rag.alternative_player_records (lower(player_name));
CREATE INDEX IF NOT EXISTS alternative_player_records_canonical_id_idx
  ON football_rag.alternative_player_records (canonical_player_id);
CREATE INDEX IF NOT EXISTS alternative_player_records_review_status_idx
  ON football_rag.alternative_player_records (review_status);

CREATE TABLE IF NOT EXISTS football_rag.football_people (
  person_id BIGSERIAL PRIMARY KEY,
  full_name TEXT NOT NULL,
  nationality TEXT,
  person_types TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
  roles TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
  active_from SMALLINT,
  active_to SMALLINT,
  biography TEXT,
  aliases JSONB NOT NULL DEFAULT '[]'::jsonb,
  source_urls JSONB NOT NULL DEFAULT '[]'::jsonb,
  attributes JSONB NOT NULL DEFAULT '{}'::jsonb,
  review_status TEXT NOT NULL DEFAULT 'draft'
    CHECK (review_status IN ('draft','in_review','approved','rejected','archived')),
  provenance JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS football_people_name_idx
  ON football_rag.football_people (lower(full_name));
CREATE INDEX IF NOT EXISTS football_people_types_gin_idx
  ON football_rag.football_people USING GIN (person_types);
CREATE INDEX IF NOT EXISTS football_people_roles_gin_idx
  ON football_rag.football_people USING GIN (roles);
CREATE INDEX IF NOT EXISTS football_people_review_status_idx
  ON football_rag.football_people (review_status);

CREATE TABLE IF NOT EXISTS football_rag.terminology_terms (
  term_id BIGSERIAL PRIMARY KEY,
  term_key TEXT NOT NULL UNIQUE,
  domain TEXT NOT NULL DEFAULT 'football',
  concept_type TEXT NOT NULL DEFAULT 'general',
  preferred_terms JSONB NOT NULL DEFAULT '{}'::jsonb,
  definitions JSONB NOT NULL DEFAULT '{}'::jsonb,
  synonyms JSONB NOT NULL DEFAULT '{}'::jsonb,
  source_urls JSONB NOT NULL DEFAULT '[]'::jsonb,
  provenance JSONB NOT NULL DEFAULT '{}'::jsonb,
  review_status TEXT NOT NULL DEFAULT 'draft'
    CHECK (review_status IN ('draft','in_review','approved','rejected','archived')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS terminology_terms_domain_idx
  ON football_rag.terminology_terms (domain);
CREATE INDEX IF NOT EXISTS terminology_terms_review_status_idx
  ON football_rag.terminology_terms (review_status);

CREATE TABLE IF NOT EXISTS football_rag.domain_audit_log (
  audit_id BIGSERIAL PRIMARY KEY,
  domain TEXT NOT NULL,
  entity_table TEXT NOT NULL,
  entity_id TEXT,
  action TEXT NOT NULL CHECK (action IN ('create','read','update','delete','import','export','approve','reject')),
  actor TEXT,
  changed_fields JSONB NOT NULL DEFAULT '{}'::jsonb,
  operation_id UUID NOT NULL DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS domain_audit_log_domain_created_idx
  ON football_rag.domain_audit_log (domain, created_at DESC);
