#!/usr/bin/python

import led
from shiftpi import shiftpi
from influxdb import InfluxDBClient

from gps3 import agps3
from time import sleep


def calc_sats(dot):
    sats_used = 0
    sats = 0
    if isinstance(dot.satellites, list):
        i = 0
        j = 0
        for sat in dot.satellites:
            if sat['used']:
                i += 1
            j += 1
        sats_used = i
        sats = j
    return sats_used, sats


class GpsData:

    def __init__(self):
        self.measure_name = 'gps'
        self.tags = {}
        self.fields = {}

    def to_json(self):
        json_body = [
            {
                "measurement": self.measure_name,
                "tags": self.tags,
                "fields": self.fields
            }
        ]
        return json_body

    def fields(self):
        return self.fields

    def tags(self):
        return self.tags

    def v(self, v):
        try:
            return float(v)
        except:
            return -1

    def populate_gps_data(self, dot):
        f = self.fields

        f['mode'] = int(float(self.v(dot.mode)))
        f['lat'] = float(self.v(dot.lat))
        f['ept'] = float(self.v(dot.ept))
        f['lon'] = float(self.v(dot.lon))
        f['epx'] = float(self.v(dot.epx))
        f['alt'] = float(self.v(dot.alt))
        f['epv'] = float(self.v(dot.epv))
        f['speed'] = float(self.v(dot.speed))
        f['eps'] = float(self.v(dot.eps))
        f['track'] = float(self.v(dot.track))
        f['epd'] = float(self.v(dot.epd))
        f['climb'] = float(self.v(dot.climb))
        f['epc'] = float(self.v(dot.epc))
        f['t'] = dot.time

        sats_used = 0
        sats = 0
        if isinstance(dot.satellites, list):
            i = 0
            j = 0
            for sat in dot.satellites:
                if sat['used']:
                    i += 1
                j += 1
            sats_used = i
            sats = j

        f['sats'] = sats
        f['sats_used'] = sats_used

led = led.Led(5, 25, led.BRIGHT_HIGHEST)
led.Clear()

influxdb = InfluxDBClient('localhost', 8086, 'root', 'root', 'gps')
influxdb.create_database('gps')

shiftpi.startup_mode(shiftpi.LOW, True)

gps = agps3.GPSDSocket()
dot = agps3.Dot()
gps.connect()
gps.watch()

for n in gps:
    if n:
        dot.unpack(n)

        if dot.mode == 'n/a':
            print "Fixing location"
            sleep(.5)
            continue

        data = GpsData()
        data.populate_gps_data(dot)
        influxdb.write_points(data.to_json())

        sats_used, sats = calc_sats(dot)

        print("Mode = %s" % (dot.mode))
        print("Time = %s, ept = %s" % (dot.time, dot.ept))
        print('Lat  = %s, epy = %s' % (dot.lat, dot.epy))
        print('Lng  = %s, epx = %s' % (dot.lon, dot.epx))
        print('Alt  = %s, epv = %s' % (dot.alt, dot.epv))
        print('Speed  = %s, eps = %s' % (dot.speed, dot.climb))
        print('Track  = %s, epd = %s' % (dot.track, dot.epd))
        print('Climb  = %s, epc = %s' % (dot.climb, dot.epc))
        print('Sat#  = %s, epc = %s' % (sats_used, ''))
        print('--------------------')
        shiftpi.display(sats_used)

        led.Show([0, 0, 0, sats_used])

        sleep(.2)
