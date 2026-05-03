SET search_path TO group120807;


-- Query 1: Year-over-year April 1 SWE trend by station
-- Rolling 10-year average and YoY change per station

WITH april1 AS (
    SELECT
        station_id,
        EXTRACT(YEAR FROM date)::INT AS yr,
        swe_in
    FROM snotel
    WHERE EXTRACT(MONTH FROM date) = 4
      AND EXTRACT(DAY   FROM date) = 1
      AND swe_in IS NOT NULL
),
yearly AS (
    SELECT
        station_id,
        yr,
        ROUND(AVG(swe_in), 2) AS mean_swe
    FROM april1
    GROUP BY station_id, yr
)
SELECT
    s.station_name,
    y.yr,
    y.mean_swe,
    ROUND(AVG(y.mean_swe) OVER (
        PARTITION BY y.station_id
        ORDER BY y.yr
        ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_10yr_avg,
    ROUND(y.mean_swe - LAG(y.mean_swe, 1) OVER (
        PARTITION BY y.station_id
        ORDER BY y.yr
    ), 2) AS yoy_change
FROM yearly y
JOIN stations s ON s.station_id = y.station_id
ORDER BY s.station_name, y.yr;


-- Query 2: ENSO phase vs. statewide April 1 SWE
-- Winter ONI = average of DJF (month 1), JFM (month 2) seasons
-- Thresholds: >= 0.5 El Nino, <= -0.5 La Nina, else Neutral

WITH winter_oni AS (
    SELECT
        year AS water_year,
        ROUND(AVG(oni), 2) AS avg_oni
    FROM oni
    WHERE month IN (1, 2)
    GROUP BY year
),
enso AS (
    SELECT
        water_year,
        avg_oni,
        CASE
            WHEN avg_oni >=  0.5 THEN 'El Nino'
            WHEN avg_oni <= -0.5 THEN 'La Nina'
            ELSE 'Neutral'
        END AS phase
    FROM winter_oni
),
april1_statewide AS (
    SELECT
        EXTRACT(YEAR FROM date)::INT AS water_year,
        ROUND(AVG(swe_in), 2) AS mean_swe
    FROM snotel
    WHERE EXTRACT(MONTH FROM date) = 4
      AND EXTRACT(DAY   FROM date) = 1
      AND swe_in IS NOT NULL
    GROUP BY water_year
)
SELECT
    e.phase,
    COUNT(*)                        AS num_years,
    ROUND(AVG(a.mean_swe), 2)       AS avg_swe,
    ROUND(MIN(a.mean_swe), 2)       AS min_swe,
    ROUND(MAX(a.mean_swe), 2)       AS max_swe,
    ROUND(STDDEV(a.mean_swe), 2)    AS stddev_swe
FROM enso e
JOIN april1_statewide a ON a.water_year = e.water_year
GROUP BY e.phase
ORDER BY avg_swe DESC;


-- Query 3: Peak SWE to peak streamflow lag by gauge and year
-- Positive lag = runoff peaked after snowpack (expected melt pattern)

WITH daily_swe AS (
    SELECT
        date,
        EXTRACT(YEAR FROM date)::INT AS yr,
        SUM(swe_in) AS total_swe
    FROM snotel
    WHERE swe_in IS NOT NULL
    GROUP BY date
),
peak_swe AS (
    SELECT DISTINCT ON (yr)
        yr,
        date AS peak_swe_date,
        total_swe AS peak_swe
    FROM daily_swe
    ORDER BY yr, total_swe DESC, date
),
peak_flow AS (
    SELECT DISTINCT ON (site_no, yr)
        site_no,
        site_name,
        yr,
        date AS peak_flow_date,
        discharge_cfs AS peak_discharge
    FROM (
        SELECT
            site_no,
            site_name,
            date,
            EXTRACT(YEAR FROM date)::INT AS yr,
            discharge_cfs
        FROM streamflow
        WHERE discharge_cfs IS NOT NULL
    ) sub
    ORDER BY site_no, yr, discharge_cfs DESC, date
)
SELECT
    f.site_name,
    f.yr,
    p.peak_swe_date,
    f.peak_flow_date,
    (f.peak_flow_date - p.peak_swe_date)  AS lag_days,
    ROUND(p.peak_swe, 1)                  AS peak_total_swe,
    ROUND(f.peak_discharge, 1)            AS peak_discharge_cfs
FROM peak_flow f
JOIN peak_swe p ON p.yr = f.yr
ORDER BY f.site_no, f.yr;