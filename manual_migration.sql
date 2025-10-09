-- Manual migration to add LinkedIn and Meta fields
-- Run this if automatic migration fails

-- Set search path to marketing_agent schema
SET search_path TO marketing_agent;

-- Add linkedin_urn field (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'marketing_agent' 
        AND table_name = 'user' 
        AND column_name = 'linkedin_urn'
    ) THEN
        ALTER TABLE marketing_agent."user" ADD COLUMN linkedin_urn VARCHAR(256);
    END IF;
END $$;

-- Add meta_access_token field (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'marketing_agent' 
        AND table_name = 'user' 
        AND column_name = 'meta_access_token'
    ) THEN
        ALTER TABLE marketing_agent."user" ADD COLUMN meta_access_token VARCHAR(512);
    END IF;
END $$;

-- Add instagram_business_id field (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'marketing_agent' 
        AND table_name = 'user' 
        AND column_name = 'instagram_business_id'
    ) THEN
        ALTER TABLE marketing_agent."user" ADD COLUMN instagram_business_id VARCHAR(128);
    END IF;
END $$;

-- Verify all columns exist
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_schema = 'marketing_agent' 
AND table_name = 'user'
AND column_name IN ('linkedin_urn', 'meta_access_token', 'facebook_page_id', 'instagram_business_id', 'linkedin_access_token')
ORDER BY column_name;
