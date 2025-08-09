# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.network.create.triggers import recreate_network_triggers


def migrate(conn):
    recreate_network_triggers(conn)
    conn.execute("update EV_Charging_Stations set Latitude = round(ST_Y(geo), 8),  Longitude = round(ST_X(geo), 8)")
