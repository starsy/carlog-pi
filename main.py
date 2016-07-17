#!/usr/bin/python

import obd
from influxdb import InfluxDBClient

obd.debug.console = True

c = obd.OBD()
r = c.query(obd.commands.RPM)

print r.value


def get_run_time(c):
    r = c.query(obd.commands.RUN_TIME)
    return r.value


def get_engine_load(c):
    r = c.query(obd.commands.ENGINE_LOAD)
    return r.value


def get_throttle_pos(c):
    r = c.query(obd.commands.THROTTLE_POS)
    return r.value


def get_rpm(c):
    r = c.query(obd.commands.RPM)
    return r.value


def get_maf(c):
    r = c.query(obd.commands.MAF)
    return r.value


def get_speed(c):
    r = c.query(obd.commands.SPEED)
    return r.value


def get_fuel_lph(c):
    maf = get_maf(c)
    return _get_fuel_lph(maf)


def get_fuel_lp100km(c):
    lph = get_fuel_lph(c)
    speed = get_speed(c)
    return _get_fuel_lp100km(lph, speed)


def _get_fuel_lph(maf):
    # LPH = (MAF / 14.7) / 454 * 3600 = MAF * 0.539423
    return maf * 0.539423


def _get_fuel_lp100km(lph, speed):
    # LP100KM = ABS(LPH / SPEED * 100) [VSS != 0]
    if speed != 0:
        return abs(lph / speed * 100)
    else:
        return None


def main(host='localhost', port=8086):
    user = 'root'
    password = 'root'
    dbname = 'example'
    dbuser = 'smly'
    dbuser_password = 'my_secret_password'
    query = 'select value from cpu_load_short;'
    json_body = [
        {
            "measurement": "cpu_load_short",
            "tags": {
                "host": "server01",
                "region": "us-west"
            },
            "time": "2009-11-10T23:00:00Z",
            "fields": {
                "value": 0.64
            }
        }
    ]

    client = InfluxDBClient(host, port, user, password, dbname)

    print("Create database: " + dbname)
    client.create_database(dbname)

    print("Create a retention policy")
    client.create_retention_policy('awesome_policy', '3d', 3, default=True)

    print("Switch user: " + dbuser)
    client.switch_user(dbuser, dbuser_password)

    print("Write points: {0}".format(json_body))
    client.write_points(json_body)

    print("Queying data: " + query)
    result = client.query(query)

    print("Result: {0}".format(result))

    print("Switch user: " + user)
    client.switch_user(user, password)

    print("Drop database: " + dbname)
    client.drop_database(dbname)
