SET search_path TO group120807;

DROP TABLE IF EXISTS snotel;
DROP TABLE IF EXISTS streamflow;
DROP TABLE IF EXISTS stations;
DROP TABLE IF EXISTS pdo;
DROP TABLE IF EXISTS oni;

CREATE TABLE oni(
    year SMALLINT,
    month SMALLINT,
    oni NUMERIC(5,2),
    PRIMARY KEY (year, month)
);

CREATE TABLE pdo(
    Year SMALLINT CHECK (Year BETWEEN 1850 AND 2030),
    Jan NUMERIC(5,2),
    Feb NUMERIC(5,2),
    Mar NUMERIC(5,2),
    Apr NUMERIC(5,2),
    May NUMERIC(5,2),
    Jun NUMERIC(5,2),
    Jul NUMERIC(5,2),
    Aug NUMERIC(5,2),
    Sep NUMERIC(5,2),
    Oct NUMERIC(5,2),
    Nov NUMERIC(5,2),
    Dec NUMERIC(5,2),
    PRIMARY KEY (Year)
);

CREATE TABLE stations(
    station_id SMALLINT,
    station_name TEXT,
    PRIMARY KEY (station_id)
);

CREATE TABLE snotel(
    station_id SMALLINT,
    date DATE,
    swe_in NUMERIC(5,2) CHECK (swe_in >= 0),
    precip_in NUMERIC(5,2) CHECK (precip_in >= 0),
    snow_depth_in NUMERIC(5,2) CHECK (snow_depth_in >= 0) ,
    temp_avg_f NUMERIC(5,2) CHECK (temp_avg_f BETWEEN -60 AND 120),
    PRIMARY KEY (station_id, date),
    FOREIGN KEY (station_id) REFERENCES stations(station_id)
);

CREATE TABLE streamflow(
    site_no TEXT,
    site_name TEXT,
    date DATE,
    discharge_cfs NUMERIC CHECK (discharge_cfs >= 0),
    PRIMARY KEY (site_no, date)
);


