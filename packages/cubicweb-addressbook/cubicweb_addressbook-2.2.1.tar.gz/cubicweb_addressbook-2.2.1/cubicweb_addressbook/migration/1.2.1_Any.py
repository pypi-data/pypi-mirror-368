if "PhoneNumber" in schema:
    sql(
        """
CREATE FUNCTION phonetype_sort_value(text) RETURNS int
    AS 'return {"mobile":2, "home":1, "office":4,"fax":0, "secretariat":3}[args[0]]'
    LANGUAGE plpythonu;
"""
    )
