-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

--##
create trigger if not exists polaris_ev_charging_stations_populates_fields_on_new_record after insert on EV_Charging_Stations
begin
    update EV_Charging_Stations
    set
        Longitude = round(ST_X(new.geo), 8),
        Latitude = round(ST_Y(new.geo), 8),
        zone =(SELECT fid FROM knn2 WHERE f_table_name = 'Zone' AND ref_geometry = new.geo AND radius = 10 AND expand=1 AND max_items=1),
        location=(SELECT fid FROM knn2 WHERE f_table_name = 'Location' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1)
    where
        EV_Charging_Stations.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_ev_charging_stations_on_longitude_change after update of "Longitude" on EV_Charging_Stations
begin
    update 
        EV_Charging_Stations set Longitude = round(ST_X(new.geo), 8)
    where
        EV_Charging_Stations.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_ev_charging_stations_on_latitude_change after update of "Latitude" on EV_Charging_Stations
begin
    update 
        EV_Charging_Stations set Latitude = round(ST_Y(new.geo), 8)
    where
        EV_Charging_Stations.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_ev_charging_stations_on_geo_change after update of geo on EV_Charging_Stations
begin
    update EV_Charging_Stations
    set
        Longitude = round(ST_X(new.geo), 8),
        Latitude = round(ST_Y(new.geo), 8),
        zone =(SELECT fid FROM knn2 WHERE f_table_name = 'Zone' AND ref_geometry = new.geo AND radius = 10 AND expand=1 AND max_items=1),
        location=(SELECT fid FROM knn2 WHERE f_table_name = 'Location' AND ref_geometry = new.geo AND radius = 10 AND expand=1 AND max_items=1)
    where
        EV_Charging_Stations.rowid = new.rowid;
end;

--##
create trigger if not exists polaris_ev_charging_stations_delete_all_data_for_deleted_stations before delete on EV_Charging_Stations
begin
  delete from EV_Charging_Station_Plugs where station_id = old.ID;
  delete from EV_Charging_Station_Service_Bays where Station_id = old.ID;
end;

--##
create trigger if not exists polaris_ev_charging_stations_on_zone_change after update of zone on EV_Charging_Stations
begin
    update EV_Charging_Stations
        set zone =(SELECT fid FROM knn2 WHERE f_table_name = 'Zone' AND ref_geometry = new.geo AND radius = 10 AND expand=1 AND max_items=1)
    where
        EV_Charging_Stations.rowid = new.rowid;
end;


--##
create trigger if not exists polaris_ev_charging_stations_on_location_change after update of location on EV_Charging_Stations
begin
        update EV_Charging_Stations
    set
        location=(SELECT fid FROM knn2 WHERE f_table_name = 'Location' AND ref_geometry = new.geo AND radius = 100 AND expand=1 AND max_items=1)
    where
        EV_Charging_Stations.rowid = new.rowid;
end;

