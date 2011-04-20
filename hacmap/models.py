from django.db import models
'''
{"nationalrateper1000discharges": "0.09"
 "name": ""
 "geoscore": "1.0"
 "color": 0
 "discharges": "692"
 "color_bits": 0
 "nationaldischarges": "5362384"
 "lon": "37.756834"
 "hacs": "0"
 "county": "SAN FRANCISCO"
 "owner": "Government - Local"
 "state": "CA"
 "rateper1000discharges": "0.0"
 "address": "1001 POTRERO AVENUE"
 "lat": "-122.406699"
 "geoprecision": "range"
 "hospitalname": "SAN FRANCISCO GENERAL HOSPITAL"
 "type": "Acute Care"}
'''

class Marker(models.Model):
    layer_name = models.CharField(max_length=100)
    marker_id = models.CharField(max_length=32)
    nationalrateper1000discharges = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    geoscore = models.CharField(max_length=100)
    color = models.IntegerField()
    discharges = models.IntegerField()
    color_bits = models.IntegerField()
    nationaldischarges = models.IntegerField()
    lon = models.CharField(max_length=100)
    hacs = models.IntegerField()
    county = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    state = models.CharField(max_length=4)
    rateper1000discharges = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    lat = models.CharField(max_length=100)
    geoprecision = models.CharField(max_length=100)
    hospitalname = models.CharField(max_length=255)
    type = models.CharField(max_length=100)


class MarkerList(models.Model):
    marker_id = models.CharField(max_length=32)
    lon = models.CharField(max_length=100)
    lat = models.CharField(max_length=100)
    bitmask = models.IntegerField()
    hospital_name = models.CharField(max_length=255)
