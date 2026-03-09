-- HEA Consulting AI — Database Schema
-- PostgreSQL with pgvector for RAG embeddings
--
-- This schema supports the full AI operating system:
-- knowledge base, projects, tasks, finance, sales, CSM, and agent tracking.

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================
-- KNOWLEDGE BASE (RAG)
-- ============================================

CREATE TABLE knowledge_base (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    domain TEXT DEFAULT 'general',
    content_era TEXT DEFAULT 'source-of-truth'
        CHECK (content_era IN ('source-of-truth', 'strategic-blueprint', 'reference-material', 'archived')),
    usage_type TEXT DEFAULT 'operational',
    embedding vector(384),  -- sentence-transformers all-MiniLM-L6-v2
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_kb_domain ON knowledge_base(domain);
CREATE INDEX idx_kb_era ON knowledge_base(content_era);
CREATE INDEX idx_kb_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);

-- ============================================
-- PROJECTS
-- ============================================

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    project_key TEXT UNIQUE NOT NULL,
    project_name TEXT NOT NULL,
    client_name TEXT,
    status TEXT DEFAULT 'active'
        CHECK (status IN ('active', 'completed', 'on-hold', 'cancelled')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    service_type TEXT,
    start_date DATE,
    end_date DATE,
    budget NUMERIC(12,2),
    currency TEXT DEFAULT 'MXN',
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE project_notes (
    id SERIAL PRIMARY KEY,
    project_key TEXT REFERENCES projects(project_key),
    content TEXT NOT NULL,
    note_type TEXT DEFAULT 'general'
        CHECK (note_type IN ('general', 'progress_update', 'blocker', 'decision', 'recommendation')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TASKS (AI Priority Scoring)
-- ============================================

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    project_key TEXT REFERENCES projects(project_key),
    status TEXT DEFAULT 'pending'
        CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    priority_score INTEGER DEFAULT 50 CHECK (priority_score >= 0 AND priority_score <= 100),
    due_date DATE,
    is_blocking BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI Priority Engine: auto-scores tasks on INSERT/UPDATE
CREATE OR REPLACE FUNCTION calculate_task_priority()
RETURNS TRIGGER AS $$
DECLARE
    score INTEGER := 50;
    days_until_due INTEGER;
BEGIN
    -- Deadline proximity (0-40 points)
    IF NEW.due_date IS NOT NULL THEN
        days_until_due := NEW.due_date - CURRENT_DATE;
        IF days_until_due < 0 THEN
            score := score + 40;  -- Overdue
        ELSIF days_until_due <= 1 THEN
            score := score + 35;
        ELSIF days_until_due <= 3 THEN
            score := score + 25;
        ELSIF days_until_due <= 7 THEN
            score := score + 15;
        ELSE
            score := score + 5;
        END IF;
    END IF;

    -- Blocking status (+10)
    IF NEW.is_blocking THEN
        score := score + 10;
    END IF;

    NEW.priority_score := LEAST(score, 100);
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_task_priority
    BEFORE INSERT OR UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION calculate_task_priority();

-- ============================================
-- FINANCE
-- ============================================

CREATE TABLE income (
    id SERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    currency TEXT DEFAULT 'MXN',
    exchange_rate NUMERIC(8,4) DEFAULT 1.0,
    status TEXT DEFAULT 'pending'
        CHECK (status IN ('pending', 'received', 'cancelled')),
    date DATE NOT NULL,
    project_key TEXT REFERENCES projects(project_key),
    description TEXT,
    stripe_payment_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    currency TEXT DEFAULT 'MXN',
    category TEXT,
    date DATE NOT NULL,
    project_key TEXT REFERENCES projects(project_key),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE pricing_models (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    service_type TEXT NOT NULL,
    base_rate NUMERIC(12,2) NOT NULL,
    currency TEXT DEFAULT 'MXN',
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- SALES & CRM
-- ============================================

CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    company_name TEXT NOT NULL,
    contact_name TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    industry TEXT,
    stage TEXT DEFAULT 'new'
        CHECK (stage IN ('new', 'contacted', 'qualified', 'proposal', 'negotiation', 'won', 'lost')),
    score INTEGER DEFAULT 0 CHECK (score >= 0 AND score <= 100),
    estimated_value NUMERIC(12,2),
    source TEXT,
    employee_count INTEGER,
    problem_description TEXT,
    timeline TEXT,
    is_decision_maker BOOLEAN DEFAULT FALSE,
    last_contact TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE lead_activities (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    activity_type TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- CUSTOMER SUCCESS
-- ============================================

CREATE TABLE client_health_scores (
    id SERIAL PRIMARY KEY,
    project_key TEXT REFERENCES projects(project_key),
    score INTEGER CHECK (score >= 0 AND score <= 100),
    factors JSONB DEFAULT '{}',
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_key)
);

CREATE TABLE client_interactions (
    id SERIAL PRIMARY KEY,
    project_key TEXT REFERENCES projects(project_key),
    interaction_type TEXT NOT NULL,
    summary TEXT,
    sentiment TEXT DEFAULT 'neutral'
        CHECK (sentiment IN ('positive', 'neutral', 'negative')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- DOCUMENTS
-- ============================================

CREATE TABLE generated_proposals (
    id SERIAL PRIMARY KEY,
    client_name TEXT NOT NULL,
    project_name TEXT NOT NULL,
    service_type TEXT,
    content_md TEXT,
    total_amount NUMERIC(12,2),
    currency TEXT DEFAULT 'MXN',
    status TEXT DEFAULT 'draft'
        CHECK (status IN ('draft', 'sent', 'accepted', 'rejected')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE generated_contracts (
    id SERIAL PRIMARY KEY,
    client_name TEXT NOT NULL,
    project_name TEXT NOT NULL,
    content_md TEXT,
    status TEXT DEFAULT 'draft'
        CHECK (status IN ('draft', 'sent', 'signed', 'rejected')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- AGENT SYSTEM
-- ============================================

CREATE TABLE agent_profiles (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    dept_code TEXT UNIQUE NOT NULL,
    role TEXT,
    description TEXT,
    tools TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE agent_activations (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER REFERENCES agent_profiles(id),
    dept_code TEXT NOT NULL,
    query_text TEXT,
    session_id TEXT,
    response_time_ms INTEGER,
    tools_used TEXT[] DEFAULT '{}',
    success BOOLEAN DEFAULT TRUE,
    routed_by TEXT DEFAULT 'manual',
    handoff_to TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- SEARCH FUNCTIONS
-- ============================================

-- Semantic search with era boosting
CREATE OR REPLACE FUNCTION search_hea_knowledge(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.3,
    match_count int DEFAULT 5,
    filter_domain text DEFAULT NULL
)
RETURNS TABLE (
    id int,
    title text,
    content text,
    domain text,
    content_era text,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        kb.id,
        kb.title,
        kb.content,
        kb.domain,
        kb.content_era,
        (1 - (kb.embedding <=> query_embedding)) *
        CASE kb.content_era
            WHEN 'source-of-truth' THEN 1.5
            WHEN 'strategic-blueprint' THEN 1.0
            WHEN 'reference-material' THEN 0.8
            WHEN 'archived' THEN 0.5
            ELSE 1.0
        END AS similarity
    FROM knowledge_base kb
    WHERE
        kb.embedding IS NOT NULL
        AND (filter_domain IS NULL OR kb.domain = filter_domain)
        AND (1 - (kb.embedding <=> query_embedding)) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;

-- Hybrid search (semantic + full-text)
CREATE OR REPLACE FUNCTION hybrid_search(
    search_query text,
    query_embedding vector(384),
    match_count int DEFAULT 5,
    filter_domain text DEFAULT NULL
)
RETURNS TABLE (
    id int,
    title text,
    content text,
    domain text,
    combined_score float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        kb.id,
        kb.title,
        kb.content,
        kb.domain,
        (
            COALESCE(1 - (kb.embedding <=> query_embedding), 0) * 0.7 +
            COALESCE(ts_rank(
                to_tsvector('english', kb.title || ' ' || kb.content),
                plainto_tsquery('english', search_query)
            ), 0) * 0.3
        ) AS combined_score
    FROM knowledge_base kb
    WHERE
        kb.embedding IS NOT NULL
        AND (filter_domain IS NULL OR kb.domain = filter_domain)
    ORDER BY combined_score DESC
    LIMIT match_count;
END;
$$;

-- Full-text search
CREATE OR REPLACE FUNCTION text_search(
    search_query text,
    match_count int DEFAULT 10,
    filter_domain text DEFAULT NULL
)
RETURNS TABLE (
    id int,
    title text,
    content text,
    domain text,
    rank float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        kb.id,
        kb.title,
        kb.content,
        kb.domain,
        ts_rank(
            to_tsvector('english', kb.title || ' ' || kb.content),
            plainto_tsquery('english', search_query)
        ) AS rank
    FROM knowledge_base kb
    WHERE
        to_tsvector('english', kb.title || ' ' || kb.content)
        @@ plainto_tsquery('english', search_query)
        AND (filter_domain IS NULL OR kb.domain = filter_domain)
    ORDER BY rank DESC
    LIMIT match_count;
END;
$$;
