-- ============================================================================
-- MARKOS-WEB — FULL SUPABASE SCHEMA (gộp 1 phát cho Supabase MỚI)
-- ----------------------------------------------------------------------------
-- Cách dùng: Supabase → SQL Editor → dán TOÀN BỘ file này → Run. Chạy 1 lần.
-- An toàn chạy lại (idempotent): mọi CREATE dùng IF NOT EXISTS / OR REPLACE;
-- phần realtime bọc DO/EXCEPTION nên re-run không lỗi.
-- Gộp từ storage/migrations/001..012 + webapp/supabase_schema.sql (2026-07-09).
--
-- Ghi chú: lớp R-1 (research→strategy→intake) cần: sessions, users,
-- user_business_profile(+intake_extra), user_sessions_slim, skill_runs.
-- Phần pgvector (vector/hnsw) chỉ dùng cho semantic search — nếu Supabase báo lỗi
-- extension/hnsw, có thể bỏ các dòng "vector"/"hnsw"/"match_campaign_history"
-- mà KHÔNG ảnh hưởng R-1.
-- ============================================================================

-- ── Extensions (đầu tiên) ───────────────────────────────────────────────────
create extension if not exists pgcrypto;   -- gen_random_uuid()
create extension if not exists vector;      -- pgvector (Supabase pre-install)


-- ============================================================================
-- 001 — sessions (v1, dùng bởi storage.session cho intake)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sessions (
    user_id        BIGINT PRIMARY KEY,
    stage          TEXT    NOT NULL DEFAULT 'idle',
    profile        JSONB   NOT NULL DEFAULT '{}',
    intake_history JSONB   NOT NULL DEFAULT '[]',
    results        JSONB   NOT NULL DEFAULT '{}',
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION update_sessions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS sessions_updated_at ON sessions;
CREATE TRIGGER sessions_updated_at
    BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION update_sessions_updated_at();

CREATE INDEX IF NOT EXISTS idx_sessions_stage ON sessions(stage);
CREATE INDEX IF NOT EXISTS idx_sessions_updated_at ON sessions(updated_at DESC);


-- ============================================================================
-- 002 — tracked_competitors (auto-monitor ads)
-- ============================================================================
CREATE TABLE IF NOT EXISTS tracked_competitors (
    id             BIGSERIAL PRIMARY KEY,
    user_id        BIGINT NOT NULL,
    page_id        TEXT NOT NULL,
    page_name      TEXT,
    interval_hours INT NOT NULL DEFAULT 24,
    last_check_at  TIMESTAMPTZ DEFAULT NOW(),
    last_ad_ids    JSONB DEFAULT '[]'::jsonb,
    is_active      BOOLEAN DEFAULT TRUE,
    created_at     TIMESTAMPTZ DEFAULT NOW(),
    updated_at     TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, page_id)
);
CREATE INDEX IF NOT EXISTS idx_tracked_user ON tracked_competitors(user_id);
CREATE INDEX IF NOT EXISTS idx_tracked_due  ON tracked_competitors(last_check_at, is_active)
    WHERE is_active = TRUE;

CREATE OR REPLACE FUNCTION update_tracked_competitors_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_tracked_competitors_updated_at ON tracked_competitors;
CREATE TRIGGER trg_tracked_competitors_updated_at
    BEFORE UPDATE ON tracked_competitors
    FOR EACH ROW EXECUTE FUNCTION update_tracked_competitors_updated_at();


-- ============================================================================
-- 003 — feedback_log
-- ============================================================================
CREATE TABLE IF NOT EXISTS feedback_log (
    id            BIGSERIAL PRIMARY KEY,
    user_id       BIGINT NOT NULL,
    skill_name    TEXT NOT NULL,
    rating        SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    industry      TEXT,
    stage         TEXT,
    business_name TEXT,
    output_excerpt TEXT,
    user_correction TEXT,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_feedback_skill_industry ON feedback_log(skill_name, industry);
CREATE INDEX IF NOT EXISTS idx_feedback_created       ON feedback_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_low_rating    ON feedback_log(rating) WHERE rating <= 3;


-- ============================================================================
-- 004 — user_brand_voice
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_brand_voice (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           BIGINT NOT NULL,
    version           INT NOT NULL DEFAULT 1,
    do_rules          JSONB DEFAULT '[]'::jsonb,
    dont_rules        JSONB DEFAULT '[]'::jsonb,
    tone_descriptors  JSONB DEFAULT '[]'::jsonb,
    banned_words      JSONB DEFAULT '[]'::jsonb,
    preferred_words   JSONB DEFAULT '[]'::jsonb,
    sample_content    TEXT,
    rules_markdown    TEXT,
    industry_context  TEXT,
    is_active         BOOLEAN DEFAULT true,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_brand_voice_user
    ON user_brand_voice(user_id) WHERE is_active = true;

CREATE OR REPLACE FUNCTION update_brand_voice_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_brand_voice_updated_at ON user_brand_voice;
CREATE TRIGGER trg_brand_voice_updated_at
    BEFORE UPDATE ON user_brand_voice
    FOR EACH ROW EXECUTE FUNCTION update_brand_voice_timestamp();


-- ============================================================================
-- 005 — pgvector: user_campaign_history + match RPC  (OPTIONAL — semantic search)
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_campaign_history (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         BIGINT NOT NULL,
    business_name   TEXT,
    industry        TEXT,
    stage           TEXT,
    primary_goal    TEXT,
    usp             TEXT,
    summary         TEXT NOT NULL,
    market_research     TEXT,
    competitor          TEXT,
    customer_insight    TEXT,
    synthesis           TEXT,
    campaign_brief      TEXT,
    embedding       vector(1536),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_campaign_history_user ON user_campaign_history(user_id);
CREATE INDEX IF NOT EXISTS idx_campaign_history_embedding
    ON user_campaign_history USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE OR REPLACE FUNCTION match_campaign_history(
    query_embedding vector(1536),
    match_user_id   bigint,
    match_count     int DEFAULT 3
)
RETURNS TABLE (
    id uuid, business_name text, industry text, primary_goal text,
    summary text, created_at timestamptz, similarity float
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT h.id, h.business_name, h.industry, h.primary_goal, h.summary, h.created_at,
           1 - (h.embedding <=> query_embedding) AS similarity
    FROM user_campaign_history h
    WHERE h.user_id = match_user_id AND h.embedding IS NOT NULL
    ORDER BY h.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;


-- ============================================================================
-- 006 — LÕI BIZ: users · user_business_profile · user_sessions_slim ·
--        skill_runs · campaigns · posts + triggers/functions
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    user_id         BIGINT PRIMARY KEY,
    name            TEXT,
    en_level        TEXT DEFAULT 'moderate',
    token_quota     INT DEFAULT 500000,
    token_used      INT DEFAULT 0,
    plan            TEXT DEFAULT 'free',
    industry_cached TEXT,
    last_active_at  TIMESTAMPTZ DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_users_active
    ON users(last_active_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_users_industry
    ON users(industry_cached) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_users_quota_warning
    ON users(user_id) WHERE token_used > token_quota * 0.8 AND deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS user_business_profile (
    user_id                   BIGINT PRIMARY KEY,
    business_name             TEXT,
    industry                  TEXT,
    stage                     TEXT,
    product_service           TEXT,
    target_customer           TEXT,
    monthly_revenue           TEXT,
    team_size                 TEXT,
    monthly_marketing_budget  TEXT,
    primary_goal              TEXT,
    current_channels          TEXT,
    main_challenge            TEXT,
    competitors               TEXT,
    location                  TEXT,
    usp                       TEXT,
    usp_confidence            TEXT,
    updated_at                TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_profile_industry ON user_business_profile(industry);
CREATE INDEX IF NOT EXISTS idx_profile_stage    ON user_business_profile(stage);

CREATE TABLE IF NOT EXISTS user_sessions_slim (
    user_id              BIGINT PRIMARY KEY,
    stage                TEXT NOT NULL DEFAULT 'idle',
    selected_task        TEXT,
    pending_intake       JSONB DEFAULT '{}'::jsonb,
    intake_history       JSONB DEFAULT '[]'::jsonb,
    tone_calibration     JSONB DEFAULT '{}'::jsonb,
    last_message_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at           TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_sessions_stale
    ON user_sessions_slim(last_message_at) WHERE stage != 'idle';

CREATE TABLE IF NOT EXISTS skill_runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         BIGINT NOT NULL,
    skill_name      TEXT NOT NULL,
    version         INT NOT NULL DEFAULT 1,
    content         TEXT NOT NULL,
    tokens_used     INT,
    model_used      TEXT,
    rating          SMALLINT,
    feedback_text   TEXT,
    campaign_id     UUID,
    parent_run_id   UUID,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_skill_runs_user_skill
    ON skill_runs(user_id, skill_name, version DESC);
CREATE INDEX IF NOT EXISTS idx_skill_runs_rating
    ON skill_runs(skill_name, rating) WHERE rating IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_skill_runs_recent
    ON skill_runs(created_at DESC);

CREATE TABLE IF NOT EXISTS campaigns (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id              BIGINT NOT NULL,
    name                 TEXT,
    status               TEXT DEFAULT 'draft',
    industry             TEXT,
    primary_goal         TEXT,
    offer_lever          TEXT,
    start_date           DATE,
    end_date             DATE,
    brief_skill_run_id   UUID,
    calendar_skill_run_id UUID,
    summary              TEXT,
    embedding            vector(1536),
    created_at           TIMESTAMPTZ DEFAULT NOW(),
    updated_at           TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (brief_skill_run_id) REFERENCES skill_runs(id) ON DELETE SET NULL,
    FOREIGN KEY (calendar_skill_run_id) REFERENCES skill_runs(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_campaigns_user_status
    ON campaigns(user_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_campaigns_active
    ON campaigns(user_id) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_campaigns_embedding
    ON campaigns USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE TABLE IF NOT EXISTS posts (
    post_id              TEXT PRIMARY KEY,
    user_id              BIGINT NOT NULL,
    campaign_id          UUID,
    week                 INT,
    day                  TEXT,
    channel              TEXT,
    pillar               TEXT,
    funnel               TEXT,
    content              TEXT NOT NULL,
    status               TEXT DEFAULT 'draft',
    parent_post_id       TEXT,
    adapt_type           TEXT,
    created_at           TIMESTAMPTZ DEFAULT NOW(),
    updated_at           TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_post_id) REFERENCES posts(post_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_posts_user_channel ON posts(user_id, channel, status);
CREATE INDEX IF NOT EXISTS idx_posts_campaign     ON posts(campaign_id, week, day);
CREATE INDEX IF NOT EXISTS idx_posts_parent       ON posts(parent_post_id) WHERE parent_post_id IS NOT NULL;

CREATE OR REPLACE FUNCTION touch_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_touch ON users;
CREATE TRIGGER trg_users_touch BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION touch_updated_at();
DROP TRIGGER IF EXISTS trg_profile_touch ON user_business_profile;
CREATE TRIGGER trg_profile_touch BEFORE UPDATE ON user_business_profile
    FOR EACH ROW EXECUTE FUNCTION touch_updated_at();
DROP TRIGGER IF EXISTS trg_session_touch ON user_sessions_slim;
CREATE TRIGGER trg_session_touch BEFORE UPDATE ON user_sessions_slim
    FOR EACH ROW EXECUTE FUNCTION touch_updated_at();
DROP TRIGGER IF EXISTS trg_campaigns_touch ON campaigns;
CREATE TRIGGER trg_campaigns_touch BEFORE UPDATE ON campaigns
    FOR EACH ROW EXECUTE FUNCTION touch_updated_at();
DROP TRIGGER IF EXISTS trg_posts_touch ON posts;
CREATE TRIGGER trg_posts_touch BEFORE UPDATE ON posts
    FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

CREATE OR REPLACE FUNCTION reset_stale_sessions()
RETURNS INT AS $$
DECLARE affected_rows INT;
BEGIN
    UPDATE user_sessions_slim
    SET stage = 'idle', pending_intake = '{}'::jsonb
    WHERE stage NOT IN ('idle', 'complete')
      AND last_message_at < NOW() - INTERVAL '24 hours';
    GET DIAGNOSTICS affected_rows = ROW_COUNT;
    RETURN affected_rows;
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- 007 — Engagement Spine: engagements · diagnostic_briefs · strategies
-- ============================================================================
CREATE TABLE IF NOT EXISTS engagements (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         BIGINT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'discovery',
    title           TEXT,
    discovery_input JSONB DEFAULT '{}'::jsonb,
    brief_id        UUID,
    strategy_id     UUID,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_engagements_user_status
    ON engagements(user_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_engagements_has_strategy
    ON engagements(user_id, created_at DESC) WHERE strategy_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS diagnostic_briefs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id   UUID NOT NULL,
    user_id         BIGINT NOT NULL,
    facts           JSONB DEFAULT '[]'::jsonb,
    hypotheses      JSONB DEFAULT '[]'::jsonb,
    gaps            JSONB DEFAULT '[]'::jsonb,
    sources         JSONB DEFAULT '[]'::jsonb,
    grounded        BOOLEAN DEFAULT FALSE,
    confidence_note TEXT,
    model_used      TEXT,
    tokens_used     INT,
    content         TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (engagement_id) REFERENCES engagements(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)       REFERENCES users(user_id)  ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_briefs_engagement
    ON diagnostic_briefs(engagement_id, created_at DESC);

CREATE TABLE IF NOT EXISTS strategies (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id     UUID NOT NULL,
    user_id           BIGINT NOT NULL,
    brief_id          UUID,
    version           INT NOT NULL DEFAULT 1,
    positioning       JSONB DEFAULT '{}'::jsonb,
    wedge             JSONB DEFAULT '{}'::jsonb,
    roadmap_90d       JSONB DEFAULT '[]'::jsonb,
    budget_allocation JSONB DEFAULT '{}'::jsonb,
    content_pillars   JSONB DEFAULT '[]'::jsonb,
    kpi_dashboard     JSONB DEFAULT '[]'::jsonb,
    kill_criteria     JSONB DEFAULT '[]'::jsonb,
    content           TEXT,
    model_used        TEXT,
    tokens_used       INT,
    rating            SMALLINT,
    feedback_text     TEXT,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (engagement_id) REFERENCES engagements(id)        ON DELETE CASCADE,
    FOREIGN KEY (user_id)       REFERENCES users(user_id)         ON DELETE CASCADE,
    FOREIGN KEY (brief_id)      REFERENCES diagnostic_briefs(id)  ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_strategies_engagement
    ON strategies(engagement_id, version DESC);
CREATE INDEX IF NOT EXISTS idx_strategies_user_recent
    ON strategies(user_id, created_at DESC);

ALTER TABLE skill_runs
    ADD COLUMN IF NOT EXISTS strategy_id   UUID,
    ADD COLUMN IF NOT EXISTS engagement_id UUID;
CREATE INDEX IF NOT EXISTS idx_skill_runs_strategy
    ON skill_runs(strategy_id) WHERE strategy_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_skill_runs_engagement
    ON skill_runs(engagement_id) WHERE engagement_id IS NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints
                   WHERE constraint_name = 'fk_engagements_brief') THEN
        ALTER TABLE engagements ADD CONSTRAINT fk_engagements_brief
            FOREIGN KEY (brief_id) REFERENCES diagnostic_briefs(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints
                   WHERE constraint_name = 'fk_engagements_strategy') THEN
        ALTER TABLE engagements ADD CONSTRAINT fk_engagements_strategy
            FOREIGN KEY (strategy_id) REFERENCES strategies(id) ON DELETE SET NULL;
    END IF;
END $$;

DROP TRIGGER IF EXISTS trg_engagements_touch ON engagements;
CREATE TRIGGER trg_engagements_touch BEFORE UPDATE ON engagements
    FOR EACH ROW EXECUTE FUNCTION touch_updated_at();


-- ============================================================================
-- 008 — cột bổ sung V2
-- ============================================================================
ALTER TABLE user_sessions_slim
    ADD COLUMN IF NOT EXISTS pending_followup_skill TEXT;
ALTER TABLE user_sessions_slim
    ADD COLUMN IF NOT EXISTS content_outputs JSONB DEFAULT '{}'::jsonb;
ALTER TABLE user_sessions_slim
    ADD COLUMN IF NOT EXISTS token_log JSONB DEFAULT '[]'::jsonb;
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS cost_used_usd NUMERIC(12,6) DEFAULT 0;


-- ============================================================================
-- 009 — campaign_intelligence (học ngầm)
-- ============================================================================
CREATE TABLE IF NOT EXISTS campaign_intelligence (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    industry        TEXT,
    target_customer TEXT,
    campaign_goal   TEXT,
    stage           TEXT,
    event_type      TEXT NOT NULL,
    fields_added    TEXT[] DEFAULT '{}',
    fields_removed  TEXT[] DEFAULT '{}',
    edit_comment    TEXT,
    brief_excerpt   TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_campintel_industry ON campaign_intelligence(industry);
CREATE INDEX IF NOT EXISTS idx_campintel_event    ON campaign_intelligence(event_type);
CREATE INDEX IF NOT EXISTS idx_campintel_created  ON campaign_intelligence(created_at DESC);


-- ============================================================================
-- 010 — FB OAuth per-user + Ads scheduler
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_fb_connections (
    user_id              BIGINT PRIMARY KEY,
    encrypted_token      TEXT NOT NULL,
    ad_account_id        TEXT NOT NULL,
    account_name         TEXT,
    expires_at           TIMESTAMPTZ,
    connected_at         TIMESTAMPTZ DEFAULT NOW(),
    last_pull_at         TIMESTAMPTZ,
    notification_enabled BOOLEAN DEFAULT TRUE,
    notify_time          TEXT DEFAULT '08:00',
    timezone             TEXT DEFAULT 'Asia/Ho_Chi_Minh',
    tracked_metrics      TEXT[] DEFAULT ARRAY['spend','roas','cpl','frequency'],
    alert_frequency_max  FLOAT,
    alert_roas_drop_pct  FLOAT,
    alert_cpm_spike_pct  FLOAT,
    -- 011: danh sách account để switch không cần re-OAuth
    available_accounts   JSONB DEFAULT '[]'::jsonb
);

CREATE TABLE IF NOT EXISTS oauth_states (
    state_token TEXT PRIMARY KEY,
    user_id     BIGINT NOT NULL,
    expires_at  TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS ads_snapshots (
    user_id        BIGINT NOT NULL,
    snapshot_date  DATE NOT NULL,
    campaign_id    TEXT NOT NULL,
    campaign_name  TEXT,
    spend          NUMERIC DEFAULT 0,
    impressions    NUMERIC DEFAULT 0,
    reach          NUMERIC DEFAULT 0,
    clicks         NUMERIC DEFAULT 0,
    ctr            FLOAT DEFAULT 0,
    cpm            FLOAT DEFAULT 0,
    frequency      FLOAT DEFAULT 0,
    leads          NUMERIC DEFAULT 0,
    purchases      NUMERIC DEFAULT 0,
    purchase_value NUMERIC DEFAULT 0,
    video_views_3s NUMERIC DEFAULT 0,
    roas           FLOAT DEFAULT 0,
    cpl            FLOAT DEFAULT 0,
    vtr_3s         FLOAT DEFAULT 0,
    created_at     TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, snapshot_date, campaign_id)
);
CREATE INDEX IF NOT EXISTS idx_ads_snapshots_user_date
    ON ads_snapshots (user_id, snapshot_date DESC);

CREATE TABLE IF NOT EXISTS ads_alert_cooldowns (
    user_id      BIGINT NOT NULL,
    campaign_id  TEXT NOT NULL,
    alert_type   TEXT NOT NULL,
    last_sent_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (user_id, campaign_id, alert_type)
);


-- ============================================================================
-- 012 — intake_extra (câu hỏi chiến lược tầng CMO + provenance)
-- ============================================================================
ALTER TABLE user_business_profile
    ADD COLUMN IF NOT EXISTS intake_extra JSONB DEFAULT '{}'::jsonb;
COMMENT ON COLUMN user_business_profile.intake_extra IS
    'D-032: {answers:{jtbd,competitive_alternative,differentiation,objection,price_point}, provenance:{field:typed|suggested|inferred}}';


-- ============================================================================
-- WEB DASHBOARD — bảng web_* (store.py phục vụ dashboard ads)
-- ============================================================================
create table if not exists web_tracked (
  id bigint generated always as identity primary key,
  name text, ads int default 0, status text, last text);
create table if not exists web_jobs (
  name text primary key, when_text text, status text);
create table if not exists web_optimizations (
  id bigint generated always as identity primary key,
  action text, text text, why text);
create table if not exists web_alerts (
  id bigint generated always as identity primary key,
  sev text, icon text, title text, meta text);
create table if not exists web_settings (
  key text primary key, value int);
create table if not exists web_campaigns (
  id bigint generated always as identity primary key,
  name text, status text, budget text, objective text);
create table if not exists web_calendar_posts (
  id bigint generated always as identity primary key,
  day int, pillar text, title text);
create table if not exists web_content_items (
  id bigint generated always as identity primary key,
  idx int, hook text, format text, status text);
create table if not exists web_reports (
  id bigint generated always as identity primary key,
  name text, type text, date text);
create table if not exists web_accounts (
  id bigint generated always as identity primary key,
  name text, acc_id text, status text, spend text);
create table if not exists web_users (
  id bigint generated always as identity primary key,
  uid text, plan text, quota int, used int);
create table if not exists web_chat (
  id bigint generated always as identity primary key,
  user_id bigint, role text, content text,
  created_at timestamptz default now());
create index if not exists web_chat_user_idx on web_chat (user_id, id);

-- Realtime: đẩy thay đổi DB xuống web qua SSE. Bọc DO/EXCEPTION để re-run không lỗi
-- (nếu bảng đã trong publication hoặc publication chưa tồn tại thì bỏ qua êm).
DO $$
BEGIN
    ALTER PUBLICATION supabase_realtime ADD TABLE
      web_tracked, web_jobs, web_optimizations, web_alerts, web_settings,
      web_campaigns, web_calendar_posts, web_content_items, web_reports,
      web_accounts, web_users;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Realtime publication skip: %', SQLERRM;
END $$;

alter table web_tracked        replica identity full;
alter table web_jobs           replica identity full;
alter table web_optimizations  replica identity full;
alter table web_alerts         replica identity full;
alter table web_settings       replica identity full;
alter table web_campaigns      replica identity full;
alter table web_calendar_posts replica identity full;
alter table web_content_items  replica identity full;
alter table web_reports        replica identity full;
alter table web_accounts       replica identity full;
alter table web_users          replica identity full;

-- ============================================================================
-- HẾT. Dùng service_role key (server-side) → bỏ qua RLS.
-- Nếu về sau bật RLS (M4 auth) → thêm policy phù hợp cho từng bảng.
-- ============================================================================
