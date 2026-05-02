-- data_cleaning.sql
-- Cleans loaded data in place after \COPY

-- 1. Null out sentinel values
-- 2. Remove out-of-range values
-- 3. Convert Wide Range format to Short

SET search_path TO group120807;

ALTER TABLE oni ADD COLUMN month SMALLINT;
UPDATE oni
SET month = CASE seas
    WHEN 'DJF' THEN 1
    WHEN 'JFM' THEN 2
    WHEN 'FMA' THEN 3
    WHEN 'MAM' THEN 4
    WHEN 'AMJ' THEN 5
    WHEN 'MJJ' THEN 6
    WHEN 'JJA' THEN 7
    WHEN 'JAS' THEN 8
    WHEN 'ASO' THEN 9
    WHEN 'SON' THEN 10
    WHEN 'OND' THEN 11
    WHEN 'NDJ' THEN 12
END
WHERE seas IS NOT NULL;
ALTER TABLE oni ADD CONSTRAINT valid_month CHECK (month BETWEEN 1 AND 12);
DELETE FROM oni 
WHERE year < 1980;

UPDATE pdo set Jan = NULL WHERE Jan = 99.99;
UPDATE pdo set Feb = NULL WHERE Feb = 99.99;
UPDATE pdo set Mar = NULL WHERE Mar = 99.99;
UPDATE pdo set Apr = NULL WHERE Apr = 99.99;
UPDATE pdo set May = NULL WHERE May = 99.99;
UPDATE pdo set Jun = NULL WHERE Jun = 99.99;
UPDATE pdo set Jul = NULL WHERE Jul = 99.99;
UPDATE pdo set Aug = NULL WHERE Aug = 99.99;
UPDATE pdo set Sep = NULL WHERE Sep = 99.99;
UPDATE pdo set Oct = NULL WHERE Oct = 99.99;
UPDATE pdo set Nov = NULL WHERE Nov = 99.99;
UPDATE pdo set Dec = NULL WHERE Dec = 99.99;

UPDATE snotel SET temp_avg_f = NULL WHERE temp_avg_f > 120;
UPDATE snotel SET temp_avg_f = NULL WHERE temp_avg_f < -60;