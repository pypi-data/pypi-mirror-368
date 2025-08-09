-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ An output table for the trip paths of freight shipments 
--@ including the number of internal trip legs, and the
--@ corresponding origin and destination locations of the leg
--@

CREATE TABLE Shipment_Legs (
    "carrier"                    INTEGER NOT NULL DEFAULT 0, --@ The unique identifier of the carrier
    "carrier_location"           INTEGER NOT NULL DEFAULT 0, --@ The location of carrier
    "shipment"                   INTEGER NOT NULL DEFAULT 0, --@ The unique identifier of this shipment 
    "leg"                        INTEGER NOT NULL DEFAULT 0, --@ The identifier of the internal trip leg for the shipment
    "leg_type"                   INTEGER NOT NULL DEFAULT 0, --@ The type of the internal trip leg
    "origin_location"            INTEGER NOT NULL DEFAULT 0, --@ The trip leg origin location (foreign key to the Location table)
    "destination_location"       INTEGER NOT NULL DEFAULT 0, --@ The trip leg destination location (foreign key to the Location table)
    "num_trucks_assigned"        INTEGER NOT NULL DEFAULT 0, --@ The number of trucks needed to carry the whole shipment, this is greater than 1 if shipment size is greater than maximum truckload
    "truckload_size"             FLOAT   NOT NULL DEFAULT 0  --@ Size of truckload for a single truck (= total shipment size of the shipment / number of trucks assigned)
);