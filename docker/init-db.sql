-- e-BIS Sahayak: PostgreSQL Initial Setup
-- SIH 2026

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Verification notice
SELECT 'Database initialized for e-BIS Sahayak' AS init_status;
