-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The EV_Charging table holds information of the charging activities that occur
--@ during simulation. Each individual vehicle that charges, either at home or at a charging station,
--@ logs information regarding its charging event here.

CREATE TABLE "EV_Charging" (
  "Station_ID" INTEGER NULL DEFAULT 0,                   --@ Identifier for where the vehicle charged. Can refer to a EV_Charging_Station ID or Location ID - former for charging event at an EVCS, and latter for charging event at home 
  "Latitude" REAL NULL DEFAULT 0,                        --@ Latitude of charging event
  "Longitude" REAL NULL DEFAULT 0,                       --@ Longitude of charging event
  "vehicle" INTEGER NULL,                                --@ Vehicle that was being charged (foreign key to the Vehicle table)
  "charge_level" INTEGER NOT NULL DEFAULT 0,             --@ Rate at which the charging occured. Corresponds to the EV_Charging_Station_Plug_Type.
  "Time_In" INTEGER NOT NULL DEFAULT 0,                  --@ Time when the vehicle arrives at a charging station or home to begin charging. (units: seconds)
  "Time_Start" INTEGER NOT NULL DEFAULT 0,               --@ Time when the vehicle actually begins to charge (when electrons start flowing) (units: seconds)
  "Time_Out" INTEGER NOT NULL DEFAULT 0,                 --@ Time when the vehicle leaves the charging station after completing charging, or stops charging at home. (units: seconds)
  "Energy_In_Wh" REAL NULL DEFAULT 0,                    --@ Vehicle's battery level when it arrives to charge (units: Wh)
  "Energy_Out_Wh" REAL NULL DEFAULT 0,                   --@ Vehicle's battery level when charging is completed (units: Wh)
  "Location_Type" TEXT NOT NULL DEFAULT '',              --@ Text description of whether charging occured at an EV charging station or at home
  "Has_Residential_Charging" INTEGER NOT NULL DEFAULT 0, --@ boolean flag - does the vehicle have access to charging at home
  "Is_TNC_Vehicle" INTEGER NOT NULL DEFAULT 0,           --@ boolean flag - is the vehicle a TNC vehicle
  "Miles_In" REAL NULL DEFAULT 0,                        --@ For TNC vehicles, value denoting what the available range is when vehicle enters charging station (units: miles)
  "Miles_Out" REAL NULL DEFAULT 0,                       --@ For TNC vehicles, value denoting what the available range is when vehicle exits charging station (units: miles)
  "Is_Artificial_Move" INTEGER NOT NULL DEFAULT 0,       --@ boolean flag - did the vehicle arrive at charging station with a negative battery level (meaning it did not have enough battery to even get to the charging station)
  CONSTRAINT "vehicle_fk"
    FOREIGN KEY ("vehicle")
    REFERENCES "Vehicle" ("vehicle_id")
    DEFERRABLE INITIALLY DEFERRED)