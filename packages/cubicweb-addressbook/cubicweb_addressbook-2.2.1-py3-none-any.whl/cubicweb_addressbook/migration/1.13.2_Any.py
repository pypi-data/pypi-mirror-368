sql(
    """
CREATE OR REPLACE FUNCTION phonetype_sort_value(phonetype text)
RETURNS int AS $$
BEGIN
    CASE phonetype
        WHEN 'fax' THEN RETURN 0;
        WHEN 'home' THEN RETURN 1;
        WHEN 'mobile' THEN RETURN 2;
        WHEN 'secretariat' THEN RETURN 3;
        WHEN 'office' THEN RETURN 4;
    END CASE;
END; $$ LANGUAGE plpgsql;
"""
)
