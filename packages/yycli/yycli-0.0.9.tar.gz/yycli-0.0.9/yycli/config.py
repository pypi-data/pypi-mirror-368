"""config
"""

import tomllib
import importlib.resources
import pathlib


def merge_dict(dst: dict, src: dict, path=None) -> dict:
    """merge
    """
    if path is None:
        path = []
    for key in src:
        if key in dst:
            if isinstance(dst[key], dict) and isinstance(src[key], dict):
                merge_dict(dst[key], src[key], path + [str(key)])
            elif isinstance(dst[key], (tuple, list)) and isinstance(
                    src[key], (tuple, list)):
                dst[key].extend(src[key])
            elif dst[key] != src[key]:
                dst[key] = src[key]
        else:
            dst[key] = src[key]
    return dst


_config = tomllib.loads(
    importlib.resources.files('yycli.conf').joinpath(
        'config.toml').read_text())

if pathlib.Path('~/.config/yycli/conf/config.toml').expanduser().exists():
    user_config = tomllib.loads(
        pathlib.Path(
            '~/.config/yycli/conf/config.toml').expanduser().read_text('utf8'))
    merge_dict(_config, user_config)

if pathlib.Path('.yycli.toml').exists():
    local_config = tomllib.loads(pathlib.Path('.yycli.toml').read_text('utf8'))
    merge_dict(_config, local_config)


def get(key: str, store=None):
    """get user defined config
    """
    if store is None:
        store = _config

    keypath = key.split('.', 1)
    if keypath[0] in store:
        if len(keypath) == 1:
            return store[keypath[0]]
        return get(keypath[1], store[keypath[0]])
    return None
