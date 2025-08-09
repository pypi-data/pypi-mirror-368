-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
drop table if exists ev_charge_by_location;
create table ev_charge_by_location as
SELECT 
       Station_ID, 
       Location_Type, 
       "is_tnc_vehicle",
       x, 
       y, 
       xx_pop_scaling_factor_xx * sum("Energy_Out_Wh"- "Energy_In_Wh")/1000.0 as energy_charged_kWh, 
       xx_pop_scaling_factor_xx * sum(Time_Start - Time_In)/3600.0 as wait_hours, 
       xx_pop_scaling_factor_xx * sum(Time_Out - Time_Start)/3600.0 as charge_hours, 
       xx_pop_scaling_factor_xx * sum(Charged_Money) as charged_money, 
       xx_pop_scaling_factor_xx * sum(case when "Energy_Out_Wh"- "Energy_In_Wh">0 then 1 else 0 end) as positive_charge_count, 
       xx_pop_scaling_factor_xx * count(*) as charge_count
FROM "EV_Charging"
group by "Station_ID", "Location_Type", "is_tnc_vehicle";

drop table if exists ev_charge_by_location_hour;
create table ev_charge_by_location_hour as
SELECT 
      Station_ID, 
      "Location_Type",
      "is_tnc_vehicle",
      Time_In/3600 as hour, 
      x, 
      y, 
      xx_pop_scaling_factor_xx * sum("Energy_Out_Wh"- "Energy_In_Wh")/1000.0 as energy_charged_kWh, 
        xx_pop_scaling_factor_xx * sum(Time_Start - Time_In)/3600.0 as wait_hours, 
      xx_pop_scaling_factor_xx * sum(Time_Out - Time_Start)/3600.0 as charge_hours, 
        xx_pop_scaling_factor_xx * sum(Charged_Money) as charged_money, 
        xx_pop_scaling_factor_xx * count(*) as charge_count
FROM "EV_Charging"
group by "Station_ID", "Location_Type", "is_tnc_vehicle", "hour";

drop table if exists ev_charging_final_home;
CREATE TABLE ev_charging_final_home(
  Station_ID INT,
  Latitude REAL,
  Longitude REAL,
  vehicle INT PRIMARY KEY,
  charge_level INT,
  Time_In INT,
  Time_Out,
  Energy_In_Wh REAL,
  Energy_Out_Wh REAL,
  Location_Type TEXT,
  Has_Residential_Charging INT,
  Is_TNC_Vehicle INT,
  Miles_In REAL,
  Miles_Out REAL,
  Is_Artificial_Move INT,
  Time_Start INT,
  x REAL,
  y REAL
);

INSERT INTO ev_charging_final_home
select "Station_ID", "Latitude", "Longitude", "vehicle", "charge_level", "Time_In", max("Time_Out") as Time_Out, 
       "Energy_In_Wh", "Energy_Out_Wh", "Location_Type", "Has_Residential_Charging", "Is_TNC_Vehicle", 
       "Miles_In", "Miles_Out", "Is_Artificial_Move", "Time_Start", "x", "y"
FROM "EV_Charging"
where Location_Type = 'Home' and is_tnc_vehicle = 0
group by vehicle;

drop table if exists ev_charge_summary_1;
create table ev_charge_summary_1 as
SELECT 
       "Location_Type",
       "is_tnc_vehicle",
       sum(energy_charged_kWh)/1000.0 as total_energy_charged_MWh, 
       sum(wait_hours) as total_wait_hours, 
       sum(charge_hours) as total_charge_hours, 
       sum(charged_money) as total_charged_dollars, 
       sum(positive_charge_count) as positive_charge_count, 
       sum(charge_count) as charge_count, 
       sum(energy_charged_kWh)/sum(positive_charge_count) as average_energy_charged_kWh, 
       sum(wait_hours)*60.0/sum(charge_count) as average_wait_minutes, 
       sum(charge_hours)*60.0/sum(positive_charge_count) as average_charge_minutes, 
       sum(charged_money)/sum(positive_charge_count) as average_paid_dollars_per_event,
       sum(charged_money)/sum(energy_charged_kWh) as averaged_paid_dollars_per_kWh
FROM "ev_charge_by_location"
group by location_type, "is_tnc_vehicle";

drop table if exists ev_charge_summary_2;
create table ev_charge_summary_2 as
SELECT 
       "Location_Type",
       "is_tnc_vehicle",
       xx_pop_scaling_factor_xx * sum("Energy_Out_Wh"- "Energy_In_Wh")/1000000.0 as total_energy_charged_MWh, 
       xx_pop_scaling_factor_xx * sum(Time_Start - Time_In)/3600.0 as total_wait_hours, 
       xx_pop_scaling_factor_xx * sum(Time_Out - Time_Start)/3600.0 as total_charge_hours, 
       xx_pop_scaling_factor_xx * sum(charged_money) as total_charged_dollars, 
       xx_pop_scaling_factor_xx * sum(case when "Energy_Out_Wh"- "Energy_In_Wh">0 then 1 else 0 end) as positive_charge_count, 
       xx_pop_scaling_factor_xx * count(*) as charge_count,
       sum("Energy_Out_Wh"- "Energy_In_Wh")/1000.0/sum(case when "Energy_Out_Wh"- "Energy_In_Wh">0 then 1 else 0 end) as average_energy_charged_kWh, 
       sum(Time_Start - Time_In)/60.0/count(*) as average_wait_minutes, 
       sum(Time_Out - Time_Start)/60.0/sum(case when "Energy_Out_Wh"- "Energy_In_Wh">0 then 1 else 0 end) as average_charge_minutes, 
       sum(charged_money)/sum(case when "Energy_Out_Wh"- "Energy_In_Wh">0 then 1 else 0 end) as average_paid_dollars_per_event,
       sum(charged_money)*1000.0/sum("Energy_Out_Wh"- "Energy_In_Wh") as averaged_paid_dollars_per_kWh
FROM "EV_Charging"
group BY 1,2;

-- Has residential charging: -1 for non-household vehicles, 0 for household no chargers, 1 for household with chargers
drop table if exists ev_charge_vehicles;
create table ev_charge_vehicles as
SELECT c.class_type as "Vehicle_Class", f.type as "Fuel_Type", p.type as "Powertrain_Type", a.type as "Automation_Type", 
       h.has_residential_charging as Has_Residential_Charging, 
       xx_pop_scaling_factor_xx * count(*) as "Count"
FROM "Vehicle_Type" v, fuel_type f, powertrain_type p, automation_type a, vehicle_class c, vehicle x, household h
where v.powertrain_type = p.type_id and v.vehicle_class = c.class_id and v.fuel_type = f.type_id 
  and v.automation_type = a.type_id and x.type = v.type_id and x.hhold = h.household
group by v.type_id, h.has_residential_charging
union
SELECT c.class_type as "Vehicle_Class", f.type as "Fuel_Type", p.type as "Powertrain_Type", a.type as "Automation_Type",   
       -1 as Has_Residential_Charging,       
       xx_pop_scaling_factor_xx * count(*) as "Count"
FROM "Vehicle_Type" v, fuel_type f, powertrain_type p, automation_type a, vehicle_class c, vehicle x
where v.powertrain_type = p.type_id and v.vehicle_class = c.class_id and v.fuel_type = f.type_id 
  and v.automation_type = a.type_id and x.type = v.type_id and x.hhold < 0 
group by v.type_id
order by c.class_type, f.type, p.type, a.type;

drop table if exists ev_trips_by_vehicle_types;
create table ev_trips_by_vehicle_types as
SELECT c.class_type as "Vehicle_Class", f.type as "Fuel_Type", p.type as "Powertrain_Type", a.type as "Automation_Type", 
       h.has_residential_charging, xx_pop_scaling_factor_xx * count(*) as "Count"
FROM "Vehicle_Type" v, fuel_type f, powertrain_type p, automation_type a, vehicle_class c, vehicle x, household h, trip t
where t.vehicle = x.vehicle_id and v.powertrain_type = p.type_id and v.vehicle_class = c.class_id 
  and v.fuel_type = f.type_id and v.automation_type = a.type_id and x.type = v.type_id and x.hhold = h.household
group by v.type_id, h.has_residential_charging
order by c.class_type, f.type, p.type, a.type;

drop table if exists ev_charge_has_residential_charging;
create table ev_charge_has_residential_charging as
SELECT location_type, ev.has_residential_charging as ev_has_residential_charging, h.has_residential_charging as h_has_residential_charging, xx_pop_scaling_factor_xx * count(*)
FROM "EV_Charging" ev, vehicle v, household h
where ev.vehicle = v.vehicle_id and v.hhold = h.household and is_tnc_vehicle = 0
group by location_type, ev_has_residential_charging, h_has_residential_charging;

drop table if exists ev_charge_trajectory;
create table ev_charge_trajectory as
SELECT
    x.vehicle_id as vehicle,
    a.person as person,
    a.seq_num as seq_num,
    t.trip_id as trip_id,
    ev.veh_ess_energy as battery_size,
    t.start/60 as dept_time,
    t.end/60 as arr_time,
    l1.zone as orig_zone,
    l2.zone as dest_zone,
    t.travel_distance/1609.3 as distance_mile,
    t.initial_energy_level as initial_charge,
    t.final_energy_level as final_charge,
    a.type as activity_type,
    h.has_residential_charging as has_charger_at_home
FROM 
    activity a,
    trip t,
    vehicle x,  
    household h,
    Vehicle_Type v,   
    fuel_type f,  
    ev_features ev,
    a.location l1,
    a.location l2
where 
    a.trip = t.trip_id and
    t.mode = 0 and
    x.vehicle_id = t.vehicle AND
    x.type = v.type_id and  
    v.fuel_type = f.type_id and   
    f.type = 'Elec' and
    v.ev_features_id = ev.ev_features_id and  
    t.origin = l1.location AND
    t.destination = l2.location and
    x.hhold = h.household
group by a.person, a.trip
order by x.vehicle_id, t.start;

drop table if exists ev_charge_trajectory_freight;
create table ev_charge_trajectory_freight as
SELECT
    x.vehicle_id as vehicle,
    t.trip_id as trip_id,
    ev.veh_ess_energy as battery_size,
    t.start/60 as dept_time,
    t.end/60 as arr_time,
    l1.zone as orig_zone,
    l2.zone as dest_zone,
    t.travel_distance/1609.3 as distance_mile,
    t.initial_energy_level as initial_charge,
    t.final_energy_level as final_charge,
    t.mode
FROM 
    trip t,
    vehicle x,  
    Vehicle_Type v,   
    fuel_type f,  
    ev_features ev,
    a.location l1,
    a.location l2
where     
    t.mode in (17, 18, 19, 20) and
    x.vehicle_id = t.vehicle AND
    x.type = v.type_id and  
    v.fuel_type = f.type_id and   
    f.type = 'Elec' and
    v.ev_features_id = ev.ev_features_id and  
    t.origin = l1.location AND
    t.destination = l2.location
group by t.trip_id
order by x.vehicle_id, t.start;

drop table if exists ev_charge_trajectory_init;
CREATE TABLE ev_charge_trajectory_init(
  has_charger_at_home INT,
  vehicle INT PRIMARY KEY,
  day_begin,
  initial_charge REAL,
  battery_size REAL,
  SoC
);

drop table if exists ev_charge_trajectory_final;
CREATE TABLE ev_charge_trajectory_final(
  has_charger_at_home INT,
  vehicle INT PRIMARY KEY,
  day_end,
  final_charge REAL,
  final_charge2,
  battery_size REAL,
  SoC
);


INSERT INTO ev_charge_trajectory_init
SELECT "has_charger_at_home", "vehicle", min("dept_time") as day_begin, "initial_charge", "battery_size", "initial_charge"/"battery_size" as SoC
FROM "ev_charge_trajectory"
group by vehicle;


INSERT INTO ev_charge_trajectory_final
SELECT "has_charger_at_home", "vehicle", max("arr_time") as day_end, "final_charge", 0.0 as final_charge2, "battery_size", "final_charge"/"battery_size" as SoC
FROM "ev_charge_trajectory"
group by vehicle;

update ev_charge_trajectory_final
set final_charge2 = (select Energy_Out_Wh from EV_Charging_final_home e where e.vehicle = ev_charge_trajectory_final.vehicle)
where exists (select * from EV_Charging_final_home e where e.vehicle = ev_charge_trajectory_final.vehicle);

update ev_charge_trajectory_final
set final_charge = final_charge2
where final_charge2 > final_charge;

update ev_charge_trajectory_final
set SoC = "final_charge"/"battery_size";

drop table if exists ev_charging_events;
create table ev_charging_events as
SELECT 
    t.vehicle as vehicle,
    t.battery_size as battery_size,
    t.dept_time as dept_time,
    t.arr_time as arr_time,
    t.orig_zone as orig_zone,
    t.dest_zone as dest_zone, 
    t.distance_mile as distance_mile,
    t.initial_charge as initial_charge,
    c.Energy_Out_Wh as station_charge,
    t.activity_type as activity_type,
    t.has_charger_at_home as has_charger_at_home
FROM 
    ev_charge_trajectory t,
    EV_Charging c
where 
    t.vehicle = c.vehicle and
    t.final_charge = c.Energy_In_Wh and
    c.Energy_In_Wh<c.Energy_Out_Wh and
    c.Location_type = 'Station' AND
    t.activity_type = 'EV_CHARGING' and
    is_tnc_vehicle = 0
order by t.vehicle, t.dept_time;

drop table if exists ev_charge_consumption;
create table ev_charge_consumption as
SELECT xx_traj_scaling_factor_xx * sum("initial_charge"- "final_charge")/1000000 as Consumption_MWh
FROM "ev_charge_trajectory";

drop table if exists ev_charge_consumption_by_res_charging;
create table ev_charge_consumption_by_res_charging as
SELECT has_charger_at_home, xx_traj_scaling_factor_xx*sum("initial_charge"- "final_charge")/1000000 as Consumption_MWh
FROM "ev_charge_trajectory"
group by has_charger_at_home;

drop table if exists ev_charge_summary_by_location_and_res_charging;
create table ev_charge_summary_by_location_and_res_charging as
SELECT "Location_Type", 
       "Has_Residential_Charging", 
       xx_pop_scaling_factor_xx*sum("Energy_Out_Wh"- "Energy_In_Wh")/1000000.0 as energy_charged_MWh, 
       xx_pop_scaling_factor_xx*sum(Time_Start - Time_In)/3600.0 as wait_hours, 
       xx_pop_scaling_factor_xx*sum(Time_Out - Time_Start)/3600.0 as charge_hours, 
       xx_pop_scaling_factor_xx*sum(charged_money) as charged_money, 
       xx_pop_scaling_factor_xx*sum(case when "Energy_Out_Wh"- "Energy_In_Wh">0 then 1 else 0 end) as positive_charge_count, 
       xx_pop_scaling_factor_xx*count(*) as charge_count
FROM "EV_Charging"
where is_tnc_vehicle = 0
group BY Location_Type, "Has_Residential_Charging";

drop table if exists ev_charge_summary_by_location_and_res_charging_and_hour;
create table ev_charge_summary_by_location_and_res_charging_and_hour as
SELECT "Location_Type", "Has_Residential_Charging", Time_In/3600 as "hour", 
       xx_pop_scaling_factor_xx*sum("Energy_Out_Wh"- "Energy_In_Wh")/1000000.0 as energy_charged_MWh, 
       xx_pop_scaling_factor_xx*sum(Time_Start - Time_In)/3600.0 as wait_hours, 
       xx_pop_scaling_factor_xx*sum(Time_Out - Time_Start)/3600.0 as charge_hours, 
       xx_pop_scaling_factor_xx*sum(case when "Energy_Out_Wh"- "Energy_In_Wh">0 then 1 else 0 end) as positive_charge_count, 
       xx_pop_scaling_factor_xx*sum(charged_money) as charged_money, 
     xx_pop_scaling_factor_xx*count(*) as charge_count
FROM "EV_Charging"
where is_tnc_vehicle = 0
group BY Location_Type, "Has_Residential_Charging", "hour";

drop table if exists ev_charge_vehicle_summary;
create table ev_charge_vehicle_summary as
SELECT f.type as "Fuel_Type", p.type as "Powertrain_Type", xx_pop_scaling_factor_xx*count(*) as "Count"
FROM "Vehicle_Type" v, fuel_type f, powertrain_type p, vehicle x
where v.powertrain_type = p.type_id and v.fuel_type = f.type_id and x.type = v.type_id and x.hhold > 0
group by f.type, p.type
order by f.type, p.type;

-- drop table if exists ev_charge_summary_init_charge;
-- create table ev_charge_summary_init_charge as
-- SELECT "has_charger_at_home", sum("initial_charge")/sum("battery_size") as init_SoC, xx_traj_scaling_factor_xx*count(*) as "Count"
-- FROM "ev_charge_trajectory_init"
-- group by "has_charger_at_home";

-- drop table if exists ev_charge_summary_final_charge;
-- create table ev_charge_summary_final_charge as
-- SELECT "has_charger_at_home", sum("final_charge")/sum("battery_size") as final_SoC, xx_traj_scaling_factor_xx*count(*) as "Count"
-- FROM "ev_charge_trajectory_final"
-- group by "has_charger_at_home";

drop table if exists ev_charge_summary_stations;
create table ev_charge_summary_stations as
SELECT
    s.station_type,
    sum(case when p.plug_type = 1 then p.plug_count else 0 end) as type_1_plugs, 
    sum(case when p.plug_type = 2 then p.plug_count else 0 end) as type_2_plugs, 
    sum(case when p.plug_type = 3 then p.plug_count else 0 end) as type_3_plugs, 
    count(distinct p.station_id) as stations
FROM 
    "a"."EV_Charging_Station_Plugs" as p,
    "a"."EV_Charging_Stations" as s
WHERE
    p.station_id = s.id
GROUP BY
    s.station_type;