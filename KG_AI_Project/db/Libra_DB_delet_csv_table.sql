--BEGIN -- 연도별 테이블 드랍
--  FOR yr IN 2014..2024 LOOP
--    BEGIN
--      EXECUTE IMMEDIATE 'DROP TABLE TD_' || yr || ' CASCADE CONSTRAINTS';
--    EXCEPTION
--      WHEN OTHERS THEN
--        IF SQLCODE != -942 THEN  -- 테이블이 존재하지 않을 때는 무시
--          RAISE;
--        END IF;
--    END;
--  END LOOP;
--END;
--/


BEGIN -- 단일명 테이블 드랍
  BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE NUM08_FILTERED_COMMON CASCADE CONSTRAINTS';
  EXCEPTION
    WHEN OTHERS THEN
      IF SQLCODE != -942 THEN
        RAISE;
      END IF;
  END;
END;
/
