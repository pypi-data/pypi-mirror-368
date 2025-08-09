"""ipinfo
"""
import datetime
import pathlib
import re
import tarfile
import geoip2.database
import ipdb
import requests
import requests.auth
from .. import config

DBTYPE_IPIP = 'ipip'
DBTYPE_GEOIP = 'geoip'


def args_parser(parser):
    """parse arguments
    """
    parser.add_argument(
        '-f',
        '--from-file',
        type=str,
        dest='from_file',
        help='read ip list from file',
        default=None,
    )
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        dest='output',
        help='output file',
        default=None,
    )
    dbtype_group = parser.add_mutually_exclusive_group()
    dbtype_group.add_argument(
        '--geoip',
        action='store_true',
        help='use geoip database',
    )
    dbtype_group.add_argument(
        '--ipip',
        action='store_true',
        help='use ipip database',
    )
    parser.add_argument(
        'ipaddress',
        nargs='*',
        help='ip address',
    )


def get_params_from_args(args):
    """get_params_from_args
    """
    vars(args)
    params = {}
    return params


def get_filename_from_headers(headers):
    """get_filename_from_headers
    """
    disposition = headers.get('Content-Disposition', None)
    if disposition:
        match = re.search(r'''filename[^;=\n]*=((['"]).*?\2|[^;\n]*)''',
                          disposition)
        if match:
            return match.group(1)
    return None


def get_geoip_database_remote_filename_and_timestamp():
    """get_geoip_database_remote_filename
    """
    url = config.get('yycli.commands.ipinfo.geoip_database_download_url')
    if not url:
        url = ('https://download.maxmind.com'
               '/geoip/databases/GeoLite2-City/download'
               '?suffix=tar.gz')

    auth = None
    account_id = config.get(
        'yycli.commands.ipinfo.geoip_database_download_account_id')
    license_key = config.get(
        'yycli.commands.ipinfo.geoip_database_download_license_key')
    if account_id and license_key:
        auth = requests.auth.HTTPBasicAuth(account_id, license_key)

    head_resp = requests.head(url, allow_redirects=True, timeout=30, auth=auth)
    last_modified = datetime.datetime.now()
    if head_resp.headers.get('Last-Modified'):
        last_modified = datetime.datetime.strptime(
            head_resp.headers.get('Last-Modified', ''),
            '%a, %d %b %Y %H:%M:%S %Z')
    filename = get_filename_from_headers(head_resp.headers)
    if not filename:
        filename = 'GeoLite2-City.tar.gz'

    return filename, last_modified


def download_geoip_database(filepath):
    """download_geoip_database
    """
    filepath = pathlib.Path(filepath).expanduser()
    url = config.get('yycli.commands.ipinfo.geoip_database_download_url')
    if not url:
        url = ('https://download.maxmind.com'
               '/geoip/databases/GeoLite2-City/download'
               '?suffix=tar.gz')

    auth = None
    account_id = config.get(
        'yycli.commands.ipinfo.geoip_database_download_account_id')
    license_key = config.get(
        'yycli.commands.ipinfo.geoip_database_download_license_key')
    if account_id and license_key:
        auth = requests.auth.HTTPBasicAuth(account_id, license_key)

    with requests.get(url,
                      allow_redirects=True,
                      timeout=30,
                      auth=auth,
                      stream=True) as resp:
        resp.raise_for_status()
        with open(filepath, 'wb') as fout:
            for chunk in resp.iter_content(chunk_size=8192):
                fout.write(chunk)


def update_geoip_database(filepath):
    """update_geoip_database
    """
    filepath = pathlib.Path(filepath).expanduser()

    filename, last_modified = get_geoip_database_remote_filename_and_timestamp(
    )

    skip_download = False
    if filepath.parent.joinpath(filename).exists():
        if filepath.parent.joinpath(filename + '.last_modified').exists():
            with open(filepath.parent.joinpath(filename + '.last_modified'),
                      'r',
                      encoding='utf-8') as fin:
                if datetime.datetime.fromtimestamp(float(
                        fin.read())) >= last_modified:
                    skip_download = True

    if not filepath.parent.is_dir():
        if filepath.parent.is_file():
            raise ValueError(f'{filepath.parent} is not a directory')
        filepath.parent.mkdir(parents=True, exist_ok=True)

    if not skip_download:
        download_geoip_database(filepath.parent.joinpath(filename))
        # save last modified timestamp
        with open(filepath.parent.joinpath(filename + '.last_modified'),
                  'w',
                  encoding='utf-8') as f_last_modified_out:
            f_last_modified_out.write(str(last_modified.timestamp()))

    # extract file
    with tarfile.open(filepath.parent.joinpath(filename), 'r:gz') as tar:
        for member in tar.getmembers():
            if 'GeoLite2-City.mmdb' in member.name:
                member.path = filepath.name
                tar.extract(member, path=filepath.parent.as_posix())


def get_geoip_info(ip):
    """get_geoip_info
    """
    db_path = config.get('yycli.commands.ipinfo.geoip_database_path')
    if not db_path:
        db_path = pathlib.Path('~/.config/yycli/data/GeoLite2-City.mmdb')
    else:
        db_path = pathlib.Path(db_path)

    if not pathlib.Path(db_path).expanduser().is_file():
        update_geoip_database(db_path.as_posix())
    reader = geoip2.database.Reader(db_path.expanduser().as_posix())
    response = reader.city(ip)
    locale = 'zh-CN'
    return (
        response.country.names.get(locale, ''),
        response.subdivisions.most_specific.names.get(locale, ''),
        response.city.names.get(locale, ''),
    )


def update_ipip_database(filepath):
    """update_ipip_database
    """
    filepath = pathlib.Path(filepath).expanduser()

    url = config.get('yycli.commands.ipinfo.ipip_database_download_url')
    if not url:
        url = 'https://www.ipip.net/free_download/'

    with requests.get(url, allow_redirects=True, timeout=30,
                      stream=True) as resp:
        resp.raise_for_status()
        with open(filepath, 'wb') as fout:
            for chunk in resp.iter_content(chunk_size=8192):
                fout.write(chunk)


def get_ipip_info(ip):
    """get_ipdb_info
    """
    db_path = config.get('yycli.commands.ipinfo.ipip_database_path')
    if not db_path:
        db_path = pathlib.Path('~/.config/yycli/data/ipipfree.ipdb')
    else:
        db_path = pathlib.Path(db_path)

    if not db_path.expanduser().is_file():
        update_ipip_database(db_path.as_posix())

    db = ipdb.City(db_path.expanduser().as_posix())
    resp = db.find(ip, 'CN')
    if not resp:
        return '', '', ''
    return resp[0], resp[1], resp[2]


def ipinfo(args):
    """ipinfo command
    """
    params = get_params_from_args(args)
    dbtype = config.get('yycli.commands.ipinfo.dbtype')
    if not dbtype:
        dbtype = DBTYPE_GEOIP

    if args.geoip:
        dbtype = DBTYPE_GEOIP
    elif args.ipip:
        dbtype = DBTYPE_IPIP

    if args.from_file and pathlib.Path(args.from_file).exists():
        with open(pathlib.Path(args.from_file).expanduser(),
                  'r',
                  encoding='utf-8') as fin:
            for line in fin:
                params['ip'] = line.strip()
                country, province, city = '', '', ''
                if dbtype == DBTYPE_GEOIP:
                    country, province, city = get_geoip_info(params['ip'])
                elif dbtype == DBTYPE_IPIP:
                    country, province, city = get_ipip_info(params['ip'])
                print(f'{params["ip"]}\t{country}\t{province}\t{city}')
    elif args.ipaddress:
        for ip in args.ipaddress:
            params['ip'] = ip
            country, province, city = '', '', ''
            if dbtype == DBTYPE_GEOIP:
                country, province, city = get_geoip_info(params['ip'])
            elif dbtype == DBTYPE_IPIP:
                country, province, city = get_ipip_info(params['ip'])
            print(f'{params["ip"]}\t{country}\t{province}\t{city}')
