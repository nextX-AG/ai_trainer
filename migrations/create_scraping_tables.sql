-- Scraping Jobs Tabelle
CREATE TABLE scraping_jobs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    status VARCHAR NOT NULL,
    config JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    results JSONB,
    error TEXT,
    progress FLOAT
);

-- Scraping Results Tabelle
CREATE TABLE scraping_results (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    job_id UUID REFERENCES scraping_jobs(id),
    source VARCHAR NOT NULL,
    url TEXT NOT NULL,
    local_path TEXT NOT NULL,
    metadata JSONB,
    downloaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trigger für updated_at
CREATE TRIGGER set_timestamp
    BEFORE UPDATE ON scraping_jobs
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_set_timestamp(); 