"""tests
"""

import argparse
from . import commands


class TestCommandsCrypt:
    """TestCommandsCrypt
    """

    def test_encrypt(self):
        """test encrypt
        """
        args = argparse.Namespace(
            command='crypt',
            encrypt=True,
            decrypt=False,
            text='helloworld',
            profile='default',
            file=None,
            aes_key=None,
            aes_iv=None,
            aes_length=None,
            algorithm=None,
        )
        params = commands.crypt.get_crypt_params_from_args(args)
        text = commands.crypt.get_text_from_args(args)

        result = 'AAAAAAAAAAAAAAAAAAAAAJqEKl6oG2eIc/U7wi9I6c0='
        assert result == commands.crypt.encrypt(text, **params)

    def test_decrypt(self):
        """test decrypt
        """
        args = argparse.Namespace(
            command='crypt',
            encrypt=False,
            decrypt=True,
            text='AAAAAAAAAAAAAAAAAAAAAJqEKl6oG2eIc/U7wi9I6c0=',
            profile='default',
            file=None,
            aes_key=None,
            aes_iv=None,
            aes_length=None,
            algorithm=None,
        )
        params = commands.crypt.get_crypt_params_from_args(args)
        text = commands.crypt.get_text_from_args(args)

        result = 'helloworld'
        assert result == commands.crypt.decrypt(text, **params)


class TestCommandsConfuse:
    """TestCommandsConfuse
    """

    def test_confuse(self):
        """test confuse
        """
        block_size = 8

        magic = 0
        number = 0x12345678
        block_order = '0,1,2,3'
        result = 0x12345678
        assert result == commands.confuse.confuse(number, magic, block_size,
                                                  block_order)
        magic = 0
        block_order = '1,2,3,0'
        result = 0x34567812
        assert result == commands.confuse.confuse(number, magic, block_size,
                                                  block_order)

        magic = 0x27
        block_order = '0,1,2,3'
        result = 0x1234565f
        assert result == commands.confuse.confuse(number, magic, block_size,
                                                  block_order)

        magic = 0x27
        block_order = '3,0,1,2'
        result = 0x78123471
        assert result == commands.confuse.confuse(number, magic, block_size,
                                                  block_order)

    def test_clarify(self):
        """test clarify
        """
        block_size = 8

        number = 0x12345678
        magic = 0
        block_order = '0,1,2,3'
        result = 0x12345678
        assert result == commands.confuse.clarify(number, magic, block_size,
                                                  block_order)
        number = 0x34567812
        magic = 0
        block_order = '1,2,3,0'
        result = 0x12345678
        assert result == commands.confuse.clarify(number, magic, block_size,
                                                  block_order)

        number = 0x1234565f
        magic = 0x27
        block_order = '0,1,2,3'
        result = 0x12345678
        assert result == commands.confuse.clarify(number, magic, block_size,
                                                  block_order)

        number = 0x78123471
        magic = 0x27
        block_order = '3,0,1,2'
        result = 0x12345678
        assert result == commands.confuse.clarify(number, magic, block_size,
                                                  block_order)
