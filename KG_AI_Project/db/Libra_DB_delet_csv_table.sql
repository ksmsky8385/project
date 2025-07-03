BEGIN
  FOR t IN (
    SELECT table_name
    FROM user_tables
    WHERE table_name LIKE '%.CSV'
  ) LOOP
    EXECUTE IMMEDIATE 'DROP TABLE "' || t.table_name || '" CASCADE CONSTRAINTS';
  END LOOP;
END;
/