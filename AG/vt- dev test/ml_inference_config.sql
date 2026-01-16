-- ML Inference Database Configuration
-- SQL functions and views for cloud_resource_tags integration

-- =====================================================================
-- FUNCTION: Get valid tags for resource type
-- =====================================================================
CREATE OR REPLACE FUNCTION get_valid_tags_for_resource(
    p_provider VARCHAR,
    p_resource_scope VARCHAR
)
RETURNS TABLE (
    id INTEGER,
    cloud_provider VARCHAR,
    resource_scope VARCHAR,
    tag_category VARCHAR,
    tag_key VARCHAR,
    value_type VARCHAR,
    allowed_values TEXT,
    is_case_sensitive BOOLEAN,
    description TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        crt.id,
        crt.cloud_provider,
        crt.resource_scope,
        crt.tag_category,
        crt.tag_key,
        crt.value_type,
        crt.allowed_values,
        crt.is_case_sensitive,
        crt.description
    FROM cloud_resource_tags crt
    WHERE crt.cloud_provider IN (p_provider, 'All')
      AND crt.resource_scope IN (p_resource_scope, 'Global')
    ORDER BY 
        CASE crt.tag_category 
            WHEN 'Critical' THEN 1
            WHEN 'Non-Critical' THEN 2
            WHEN 'Optional' THEN 3
        END,
        crt.tag_key;
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- FUNCTION: Validate tag value against schema
-- =====================================================================
CREATE OR REPLACE FUNCTION validate_tag_value(
    p_provider VARCHAR,
    p_tag_key VARCHAR,
    p_predicted_value VARCHAR
)
RETURNS TABLE (
    is_valid BOOLEAN,
    normalized_value VARCHAR,
    tag_category VARCHAR,
    confidence DECIMAL
) AS $$
DECLARE
    v_tag_record RECORD;
    v_allowed_values TEXT[];
    v_normalized VARCHAR;
    v_is_valid BOOLEAN := FALSE;
    v_confidence DECIMAL := 0.0;
BEGIN
    -- Get tag schema
    SELECT * INTO v_tag_record
    FROM cloud_resource_tags
    WHERE cloud_provider IN (p_provider, 'All')
      AND tag_key = p_tag_key
    LIMIT 1;
    
    IF NOT FOUND THEN
        -- Tag not in schema
        RETURN QUERY SELECT FALSE, NULL::VARCHAR, NULL::VARCHAR, 0.0::DECIMAL;
        RETURN;
    END IF;
    
    v_normalized := p_predicted_value;
    
    -- Validate Enum types
    IF v_tag_record.value_type = 'Enum' AND v_tag_record.allowed_values IS NOT NULL THEN
        v_allowed_values := string_to_array(v_tag_record.allowed_values, ',');
        
        IF v_tag_record.is_case_sensitive THEN
            -- Case-sensitive validation
            IF p_predicted_value = ANY(v_allowed_values) THEN
                v_is_valid := TRUE;
                v_confidence := 0.95;
            ELSE
                -- Try case-insensitive match for normalization
                SELECT av INTO v_normalized
                FROM unnest(v_allowed_values) av
                WHERE LOWER(av) = LOWER(p_predicted_value)
                LIMIT 1;
                
                IF v_normalized IS NOT NULL THEN
                    v_is_valid := TRUE;
                    v_confidence := 0.90;
                END IF;
            END IF;
        ELSE
            -- Case-insensitive validation
            SELECT av INTO v_normalized
            FROM unnest(v_allowed_values) av
            WHERE LOWER(TRIM(av)) = LOWER(p_predicted_value)
            LIMIT 1;
            
            IF v_normalized IS NOT NULL THEN
                v_is_valid := TRUE;
                v_confidence := 0.95;
            END IF;
        END IF;
    ELSE
        -- Non-Enum types are always valid if they exist in schema
        v_is_valid := TRUE;
        v_confidence := 0.90;
    END IF;
    
    -- Boost confidence for Critical tags
    IF v_tag_record.tag_category = 'Critical' AND v_is_valid THEN
        v_confidence := LEAST(v_confidence + 0.05, 0.99);
    END IF;
    
    RETURN QUERY SELECT 
        v_is_valid,
        v_normalized,
        v_tag_record.tag_category,
        v_confidence;
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- FUNCTION: Get allowed values for a tag key
-- =====================================================================
CREATE OR REPLACE FUNCTION get_tag_allowed_values(
    p_provider VARCHAR,
    p_tag_key VARCHAR
)
RETURNS TEXT[] AS $$
DECLARE
    v_allowed_values TEXT;
BEGIN
    SELECT allowed_values INTO v_allowed_values
    FROM cloud_resource_tags
    WHERE cloud_provider IN (p_provider, 'All')
      AND tag_key = p_tag_key
      AND value_type = 'Enum'
    LIMIT 1;
    
    IF v_allowed_values IS NULL THEN
        RETURN ARRAY[]::TEXT[];
    END IF;
    
    RETURN string_to_array(v_allowed_values, ',');
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- MATERIALIZED VIEW: ML Feature Extraction View
-- Optimized for ML model queries
-- =====================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS ml_tag_features AS
SELECT 
    cloud_provider,
    resource_scope,
    tag_category,
    tag_key,
    value_type,
    CASE 
        WHEN value_type = 'Enum' THEN string_to_array(allowed_values, ',')
        ELSE NULL
    END as allowed_values_array,
    is_case_sensitive,
    description,
    -- ML-specific computed fields
    CASE tag_category 
        WHEN 'Critical' THEN 1
        WHEN 'Non-Critical' THEN 2
        WHEN 'Optional' THEN 3
    END as category_priority,
    CASE 
        WHEN tag_category = 'Critical' THEN TRUE
        ELSE FALSE
    END as is_required,
    CASE 
        WHEN value_type = 'Enum' THEN array_length(string_to_array(allowed_values, ','), 1)
        ELSE 0
    END as enum_value_count
FROM cloud_resource_tags
ORDER BY category_priority, tag_key;

-- Create index on materialized view
CREATE INDEX IF NOT EXISTS idx_ml_tag_features_lookup 
ON ml_tag_features(cloud_provider, resource_scope, tag_category);

-- =====================================================================
-- FUNCTION: Refresh ML features (call periodically)
-- =====================================================================
CREATE OR REPLACE FUNCTION refresh_ml_tag_features()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW ml_tag_features;
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- VIEW: Critical Tags by Provider and Scope
-- Quick lookup for required tags
-- =====================================================================
CREATE OR REPLACE VIEW critical_tags_by_scope AS
SELECT 
    cloud_provider,
    resource_scope,
    COUNT(*) as critical_tag_count,
    array_agg(tag_key ORDER BY tag_key) as required_tag_keys
FROM cloud_resource_tags
WHERE tag_category = 'Critical'
GROUP BY cloud_provider, resource_scope;

-- =====================================================================
-- FUNCTION: Calculate confidence score
-- Based on detection method, category, and enum match
-- =====================================================================
CREATE OR REPLACE FUNCTION calculate_ml_confidence(
    p_detection_method VARCHAR,
    p_tag_category VARCHAR,
    p_enum_match BOOLEAN
)
RETURNS DECIMAL AS $$
DECLARE
    v_base_confidence DECIMAL;
BEGIN
    -- Base confidence by detection method
    v_base_confidence := CASE p_detection_method
        WHEN 'NORMALIZED' THEN 0.98
        WHEN 'PATTERN_MATCH' THEN 0.85
        WHEN 'SMART_DEFAULT' THEN 0.65
        ELSE 0.50
    END;
    
    -- Category boost
    IF p_tag_category = 'Critical' THEN
        v_base_confidence := v_base_confidence + 0.10;
    ELSIF p_tag_category = 'Optional' THEN
        v_base_confidence := v_base_confidence - 0.10;
    END IF;
    
    -- Enum match boost for pattern matching
    IF p_enum_match AND p_detection_method = 'PATTERN_MATCH' THEN
        v_base_confidence := v_base_confidence + 0.10;
    END IF;
    
    -- Cap at 0.99
    RETURN LEAST(v_base_confidence, 0.99);
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- Test the functions
-- =====================================================================

-- Test 1: Get valid tags for AWS Compute
-- SELECT * FROM get_valid_tags_for_resource('AWS', 'Compute');

-- Test 2: Validate environment tag value
-- SELECT * FROM validate_tag_value('AWS', 'Environment', 'production');

-- Test 3: Get allowed values for Environment tag
-- SELECT get_tag_allowed_values('All', 'Environment');

-- Test 4: Calculate confidence
-- SELECT calculate_ml_confidence('PATTERN_MATCH', 'Critical', TRUE);

-- Test 5: View critical tags
-- SELECT * FROM critical_tags_by_scope WHERE cloud_provider = 'AWS';

-- =====================================================================
-- Performance indexes for ML queries
-- =====================================================================

-- Additional composite indexes for common ML queries
CREATE INDEX IF NOT EXISTS idx_tags_provider_scope_category 
ON cloud_resource_tags(cloud_provider, resource_scope, tag_category);

CREATE INDEX IF NOT EXISTS idx_tags_key_lookup 
ON cloud_resource_tags(tag_key, cloud_provider) 
WHERE value_type = 'Enum';

-- Index for enum value searches
CREATE INDEX IF NOT EXISTS idx_tags_enum_values 
ON cloud_resource_tags(allowed_values) 
WHERE value_type = 'Enum' AND allowed_values IS NOT NULL;

-- =====================================================================
-- Helper function: Get tag description for reasoning
-- =====================================================================
CREATE OR REPLACE FUNCTION get_tag_reasoning(
    p_provider VARCHAR,
    p_tag_key VARCHAR,
    p_detection_method VARCHAR
)
RETURNS TEXT AS $$
DECLARE
    v_description TEXT;
    v_prefix TEXT;
BEGIN
    SELECT description INTO v_description
    FROM cloud_resource_tags
    WHERE cloud_provider IN (p_provider, 'All')
      AND tag_key = p_tag_key
    LIMIT 1;
    
    v_prefix := CASE p_detection_method
        WHEN 'NORMALIZED' THEN 'Normalized from native tag. '
        WHEN 'PATTERN_MATCH' THEN 'Pattern matched from resource name. '
        WHEN 'SMART_DEFAULT' THEN 'Smart default applied. '
        ELSE ''
    END;
    
    RETURN v_prefix || COALESCE(v_description, 'No description available');
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- Comments for documentation
-- =====================================================================
COMMENT ON FUNCTION get_valid_tags_for_resource IS 'Returns all applicable tags for a given cloud provider and resource scope, ordered by category priority';
COMMENT ON FUNCTION validate_tag_value IS 'Validates a predicted tag value against the schema and returns normalized value with confidence score';
COMMENT ON FUNCTION calculate_ml_confidence IS 'Calculates ML confidence score based on detection method, tag category, and enum matching';
COMMENT ON MATERIALIZED VIEW ml_tag_features IS 'Optimized view for ML feature extraction with precomputed category priorities and enum counts';
