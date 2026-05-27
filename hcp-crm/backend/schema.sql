-- ============================================================
-- HCP CRM Database Schema
-- PostgreSQL
-- ============================================================

-- Create database (run separately if needed)
-- CREATE DATABASE hcp_crm;

-- ============================================================
-- Table: interactions
-- Stores all HCP interaction records
-- ============================================================

CREATE TABLE IF NOT EXISTS interactions (
    -- Primary Key
    id                  SERIAL PRIMARY KEY,

    -- HCP Details
    hcp_name            VARCHAR(255) NOT NULL,
    specialty           VARCHAR(255),
    hospital            VARCHAR(255),

    -- Interaction Details
    interaction_type    VARCHAR(50),        -- Visit / Call / Meeting
    datetime            TIMESTAMPTZ,        -- Date and time of interaction
    products            TEXT,               -- Comma-separated product names
    notes               TEXT,               -- Free-form notes

    -- AI-Generated Fields
    summary             TEXT,               -- LLM-generated summary
    sentiment           VARCHAR(50)         -- positive / neutral / negative
                        DEFAULT 'neutral',

    -- Follow-up
    follow_up_date      TIMESTAMPTZ,

    -- Metadata
    created_at          TIMESTAMPTZ         DEFAULT NOW(),
    updated_at          TIMESTAMPTZ         DEFAULT NOW()
);

-- ============================================================
-- Indexes for performance
-- ============================================================

-- Index on hcp_name for fast lookups
CREATE INDEX IF NOT EXISTS idx_interactions_hcp_name
    ON interactions (hcp_name);

-- Index on datetime for sorting
CREATE INDEX IF NOT EXISTS idx_interactions_datetime
    ON interactions (datetime DESC NULLS LAST);

-- Index on sentiment for filtering
CREATE INDEX IF NOT EXISTS idx_interactions_sentiment
    ON interactions (sentiment);

-- Index on follow_up_date for upcoming follow-ups
CREATE INDEX IF NOT EXISTS idx_interactions_follow_up_date
    ON interactions (follow_up_date);

-- ============================================================
-- Auto-update updated_at trigger
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_interactions_updated_at
    BEFORE UPDATE ON interactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- Sample Data (optional, for testing)
-- ============================================================

INSERT INTO interactions (
    hcp_name, specialty, hospital, interaction_type,
    datetime, products, notes, summary, sentiment, follow_up_date
) VALUES
(
    'Dr. Priya Rao',
    'Endocrinology',
    'Apollo Hospital',
    'Visit',
    NOW() - INTERVAL '7 days',
    'Metformin XR, Januvia',
    'Doctor showed strong interest in the new diabetes drug. Asked for clinical trial data.',
    'Productive visit with Dr. Priya Rao at Apollo Hospital. Discussed Metformin XR and Januvia for diabetes management. HCP expressed positive interest and requested clinical data.',
    'positive',
    NOW() + INTERVAL '7 days'
),
(
    'Dr. Arjun Mehta',
    'Cardiology',
    'Fortis Hospital',
    'Call',
    NOW() - INTERVAL '3 days',
    'Rosuvastatin, Clopidogrel',
    'Brief call. Doctor was busy but agreed to a meeting next week.',
    'Short phone call with Dr. Arjun Mehta. Discussed cardiovascular products briefly. Follow-up meeting scheduled.',
    'neutral',
    NOW() + INTERVAL '5 days'
),
(
    'Dr. Sunita Sharma',
    'Oncology',
    'AIIMS Delhi',
    'Meeting',
    NOW() - INTERVAL '1 day',
    'Bevacizumab, Pembrolizumab',
    'Detailed discussion on immunotherapy options. Doctor expressed concerns about side effects.',
    'In-depth meeting with Dr. Sunita Sharma at AIIMS Delhi regarding immunotherapy products. HCP raised concerns about adverse effects requiring follow-up with medical affairs.',
    'neutral',
    NOW() + INTERVAL '14 days'
);
