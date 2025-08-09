#!/usr/bin/env python
"""weather
"""
import pathlib
from ... import config
from .backends.baidu import Baidu as WeatherBaidu
from .backends.amap import Amap as WeatherAmap


def args_parser(parser):
    """args parser
    """
    parser.add_argument('-f',
                        '--from-file',
                        type=str,
                        dest='from_file',
                        help='read district id list from file',
                        default=None)
    parser.add_argument('-b',
                        '--backend',
                        type=str,
                        dest='backend',
                        help='use specific backend, amap or baidu',
                        default=None)
    parser.add_argument('area_id', nargs='*', help='area id')


def weather(args):
    """weather
    """
    backend_type = config.get('yycli.commands.weather.api_backend')
    if args.backend:
        backend_type = args.backend
    backend = None
    if backend_type == 'amap':
        opts = config.get('yycli.commands.weather.api_backends.amap')
        backend = WeatherAmap(**opts)
    elif backend_type == 'baidu':
        opts = config.get('yycli.commands.weather.api_backends.baidu')
        backend = WeatherBaidu(**opts)
    if not backend:
        raise ValueError('No valid weather backend configured.')

    # use Beijing(Haidian) 110108 as default
    default_area_id = '110108'
    area_id_list = []
    if args.from_file and pathlib.Path(args.from_file).expanduser().exists():
        with open(pathlib.Path(args.from_file).expanduser(),
                  'r',
                  encoding='utf-8') as fin:
            for line in fin.readlines():
                area_id = backend.resolve_query(line.strip())
                area_id_list.append(area_id)
    else:
        for area_id in args.area_id:
            area_id = backend.resolve_query(area_id)
            if area_id:
                area_id_list.append(area_id)

    if not area_id_list:
        area_id_list.append(default_area_id)

    for area_id in area_id_list:
        ret = backend.query_weather(area_id)

        format_string = config.get('yycli.commands.weather.format_string')
        if not format_string:
            format_string = ('%(area)s %(phenomenon)s %(temperature)sºC'
                             ' %(wind_direction)s/%(wind_class)s')

        print(format_string % ret)
