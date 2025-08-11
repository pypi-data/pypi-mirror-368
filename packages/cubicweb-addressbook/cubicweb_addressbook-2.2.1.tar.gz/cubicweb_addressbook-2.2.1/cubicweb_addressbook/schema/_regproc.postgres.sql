/* -*- sql -*-

   postgres specific registered procedures,
   require the plpgsql language installed

*/

CREATE OR REPLACE FUNCTION NAME(login VARCHAR, firstname VARCHAR, surname VARCHAR) RETURNS VARCHAR
AS $$
BEGIN
    IF firstname IS NULL OR firstname = '' THEN
        RETURN login;
    ELSEIF surname IS NULL OR surname = '' THEN
        RETURN firstname;
    ELSE
        RETURN firstname || ' ' || surname;
    END IF;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION PHONETYPE_SORT_VALUE(phonetype varchar) RETURNS int
AS $$
BEGIN
    IF phonetype = 'fax' THEN
        RETURN 0;
    ELSIF phonetype = 'home' THEN
        RETURN 1;
    ELSIF phonetype = 'mobile' THEN
        RETURN 2;
    ELSIF phonetype = 'secretariat' THEN
        RETURN 3;
    ELSE
        RETURN 4;
    END IF;
END;
$$ LANGUAGE plpgsql;
