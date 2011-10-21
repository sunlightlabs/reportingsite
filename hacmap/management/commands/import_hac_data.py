'''
{"nationalrateper1000discharges": "0.09", "name": "", "geoscore": "1.0", "color": 0, "discharges": "692", "color_bits": 0, "nationaldischarges": "5362384", "lon": "37.756834", "hacs": "0", "county": "SAN FRANCISCO", "owner": "Government - Local", "state": "CA", "rateper1000discharges": "0.0", "address": "1001 POTRERO AVENUE", "lat": "-122.406699", "geoprecision": "range", "hospitalname": "SAN FRANCISCO GENERAL HOSPITAL", "type": "Acute Care"}
'''
import json
import os
import sys

from hacmap.models import *

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **options):
        fields = ['nationalrateper1000discharges',
            'name',
            'geoscore',
            'color',
            'discharges',
            'color_bits',
            'nationaldischarges',
            'lon',
            'hacs',
            'county',
            'owner',
            'state',
            'rateper1000discharges',
            'address',
            'lat',
            'geoprecision',
            'hospitalname',
            'type',]

        path = sys.argv[-1]
        layer_name = path.strip('/').split('/')[-1]
        print layer_name

        for f in os.listdir(path):
            marker_id = f.split('.')[0]

            data = json.loads(open(os.path.join(path, f)).read())
            data.update({'layer_name': layer_name,
                         'marker_id': marker_id, })
            str_data = {}
            for k, v in data.iteritems():
                str_data[str(k)] = v

            for field in fields:
                if field not in str_data:
                    str_data[field] = 0

            Marker.objects.create(**str_data)
