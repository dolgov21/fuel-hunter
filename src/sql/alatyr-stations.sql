-- Seed stations in Alatyr, Chuvash Republic.

BEGIN;

CREATE TEMPORARY TABLE alatyr_station_seed (
    osm_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255) NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    address TEXT NOT NULL
) ON COMMIT DROP;

INSERT INTO alatyr_station_seed (osm_id, name, brand, lat, lon, address)
VALUES
    ('usr_CEZDN9BD7Ts', 'Башнефть', 'Башнефть', 54.84540623209541, 46.56757146120072, 'ул. Гагарина, 1В'),
    ('usr_Mb2SDHnH57A', 'Татнефть', 'Татнефть', 54.82520729703631, 46.55188858509064, 'ул. 40 лет Победы, 98'),
    ('usr_RRkc89Kz1vE', 'Татнефть', 'Татнефть', 54.83302489186547, 46.6099101305008, 'ул. Юбилейная, 22');

DO $$
DECLARE
    station_row alatyr_station_seed%ROWTYPE;
    station_location_id INTEGER;
BEGIN
    FOR station_row IN SELECT * FROM alatyr_station_seed LOOP
        SELECT location_id
        INTO station_location_id
        FROM stations
        WHERE osm_id = station_row.osm_id;

        IF NOT FOUND THEN
            INSERT INTO locations (city, address, lat, lon)
            VALUES (
                'Алатырь',
                station_row.address,
                station_row.lat,
                station_row.lon
            )
            RETURNING id INTO station_location_id;

            INSERT INTO stations (
                osm_id,
                location_id,
                name,
                brand,
                confidence_base
            )
            VALUES (
                station_row.osm_id,
                station_location_id,
                station_row.name,
                station_row.brand,
                0
            );
        END IF;
    END LOOP;
END $$;

COMMIT;
