WITH base AS (
    SELECT * FROM {{ ref('stg_energy') }}
),
with_metrics AS (
    SELECT
        country,
        year,
        electricity_generation,
        renewables_electricity,
        wind_electricity,
        solar_electricity,
        coal_electricity,
        gas_electricity,
        nuclear_electricity,
        hydro_electricity,
        ROUND(CAST(renewables_electricity / NULLIF(electricity_generation, 0) * 100 AS numeric), 2) AS renewable_share_pct,
        coal_electricity + gas_electricity AS fossil_electricity,
        ROUND(CAST((coal_electricity + gas_electricity) / NULLIF(electricity_generation, 0) * 100 AS numeric), 2) AS fossil_share_pct,
        ROUND(CAST(wind_electricity / NULLIF(electricity_generation, 0) * 100 AS numeric), 2) AS wind_share_pct,
        ROUND(CAST(
            (electricity_generation - LAG(electricity_generation) OVER (PARTITION BY country ORDER BY year))
            / NULLIF(LAG(electricity_generation) OVER (PARTITION BY country ORDER BY year), 0) * 100
        AS numeric), 2) AS yoy_growth_pct,
        RANK() OVER (PARTITION BY year ORDER BY renewables_electricity DESC) AS renewable_rank
    FROM base
)
SELECT * FROM with_metrics
ORDER BY country, year