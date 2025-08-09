-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Lists all electric vehicle charging stations available in the model.
--@
--@ The number of chargers and charger types are on EV_Charging_Station_Plugs
--@ and EV_Charging_Station_Plug_Types, respectively. The cost of charging at
--@ the specific station is defined in the EV_Charging_Station_Pricing table.
--@ The number of bays available at the charging station defined in the EV_Charging_Station_Service_Bays table.
--@
--@ Not required by all models.

CREATE TABLE IF NOT EXISTS EV_Charging_Stations(
    ID           INTEGER NOT NULL PRIMARY KEY, --@ Unique identifier for the charging station
    Latitude     REAL,           --@ Latitude of the charging station, soon to be replaced with metric values such as 'x' in other spatial columns.
    Longitude    REAL,           --@ Longitude of the charging station, soon to be replaced with metric values such as 'y' in other spatial columns.
    location     INTEGER,        --@ Foreign key reference to the nearest record in the Location table, where this charging station is location in the model. Auto-generated with geo-consistency.
    zone         INTEGER,        --@ Foreign key reference to the Zone where this charging station is situated. Auto-generated with geo-consistency.
    Station_Type INTEGER DEFAULT 1 --@ Type of station (either public, private, or freight) denoted by the enum !Charging_Station_Type_Keys!
);

select AddGeometryColumn( 'EV_Charging_Stations', 'geo', SRID_PARAMETER, 'POINT', 'XY');

create INDEX IF NOT EXISTS "EV_Charging_Stations_ID_I" ON "EV_Charging_Stations" ("ID");

select CreateSpatialIndex( 'EV_Charging_Stations' , 'geo' );
