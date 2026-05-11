WITH source AS (
    SELECT * FROM raw.raw_energy
),
cleaned AS (
    SELECT
        country,
        year,
        COALESCE(electricity_generation, 0) AS electricity_generation,
        COALESCE(renewables_electricity, 0) AS renewables_electricity,
        COALESCE(wind_electricity, 0)       AS wind_electricity,
        COALESCE(solar_electricity, 0)      AS solar_electricity,
        COALESCE(coal_electricity, 0)       AS coal_electricity,
        COALESCE(gas_electricity, 0)        AS gas_electricity,
        COALESCE(nuclear_electricity, 0)    AS nuclear_electricity,
        COALESCE(hydro_electricity, 0)      AS hydro_electricity,
        ingested_at
    FROM source
    WHERE year >= 2000
    AND country IS NOT NULL
    AND electricity_generation > 0
)
SELECT * FROM cleaned