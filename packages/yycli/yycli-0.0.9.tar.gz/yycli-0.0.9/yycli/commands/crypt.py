"""crypt command
"""
# import argparse
import base64
import logging
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from .. import config


def split(src: bytes | str, chunk_size: int) -> list[bytes | str]:
    """split
    """
    return [src[i:i + chunk_size] for i in range(0, len(src), chunk_size)]


def decode_aes_key(aes_key: str) -> bytes:
    """decode_aes_key
    """
    return b''.join(
        [chr(int(f'0x{i}', 16)).encode() for i in split(aes_key, 2)])


def args_parser(parser):
    """parse arguments
    """
    parser.add_argument(
        '-e',
        '--encrypt',
        action='store_true',
        # action=argparse.BooleanOptionalAction,
        help='encrypt')
    parser.add_argument(
        '-d',
        '--decrypt',
        action='store_true',
        # action=argparse.BooleanOptionalAction,
        help='decrypt')
    parser.add_argument('-p', '--profile', help='profile to use')
    parser.add_argument('-a', '--algorithm', help='algorithm')
    parser.add_argument('-k', '--aes_key', help='encrypt key')
    parser.add_argument('-i', '--aes_iv', help='initialization vector')
    parser.add_argument('-l', '--aes_length', help='vector length')

    parser.add_argument('-f',
                        '--file',
                        help='file to encrypt or decrypt',
                        required=False)
    parser.add_argument('text', nargs='?', help='text to encrypt or decrypt')


def encrypt_aes_256_cbc(text: str, **params) -> str:
    """encrypt_aes_256_cbc
    """
    aes_key = decode_aes_key(params.get('aes_key', '00' * 32))
    aes_iv = decode_aes_key(params.get('aes_iv', '00' * 16))
    aes_length = params.get('length', 16)
    aes = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    cipher = aes.encrypt(pad(text.encode(), aes_length))
    return base64.b64encode(aes_iv + cipher).decode()


def encrypt(text: str, **params) -> str:
    """encrypt
    """
    algorithm = params.get('algorithm', 'aes-256-cbc')
    if algorithm == 'aes-256-cbc':
        return encrypt_aes_256_cbc(text, **params)
    return text


def decrypt_aes_256_cbc(cipher: str, **params) -> str:
    """decrypt_aes_256_cbc
    """
    aes_key = decode_aes_key(params.get('aes_key', '00' * 32))
    aes_iv = decode_aes_key(params.get('aes_iv', '00' * 16))
    aes_length = params.get('length', 16)
    aes = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    text = aes.decrypt(base64.b64decode(cipher).removeprefix(aes_iv))
    return unpad(text, aes_length).decode()


def decrypt(cipher: str, **params) -> str:
    """decrypt
    """
    algorithm = params.get('algorithm', 'aes-256-cbc')
    if algorithm == 'aes-256-cbc':
        return decrypt_aes_256_cbc(cipher, **params)
    return cipher


def get_text_from_args(args):
    """get_text_from_args
    """
    if args.file is not None:
        with open(args.file, 'r', encoding='utf-8') as fin:
            text = fin.read()
    else:
        text = args.text
    return text


def get_crypt_params_from_args(args):
    """get_crypt_params_from_args
    """
    params = {
        'aes_key': '00' * 32,
        'aes_iv': '00' * 16,
        'aes_length': 16,
        'algorithm': 'aes-256-cbc'
    }
    profile = config.get('yycli.commands.crypt.default-profile', None)
    if args.profile is not None:
        profile = args.profile
    if profile is not None:
        profiles = config.get('yycli.commands.crypt.profiles')
        if profiles and profile in profiles:
            params.update(profiles.get(profile).items())
        else:
            logging.warning('profile not found')

    if args.aes_key is not None:
        params['aes_key'] = args.aes_key
    if args.aes_iv is not None:
        params['aes_iv'] = args.aes_iv
    if args.aes_length is not None:
        params['aes_length'] = args.aes_length
    if args.algorithm is not None:
        params['algorithm'] = args.algorithm
    return params


def crypt(args):
    """crypt command
    """
    params = get_crypt_params_from_args(args)
    text = get_text_from_args(args)

    if text is None:
        logging.error('no text to encrypt or decrypt')
        return

    if args.encrypt:
        print(encrypt(text, **params))
    elif args.decrypt:
        print(decrypt(text, **params))
