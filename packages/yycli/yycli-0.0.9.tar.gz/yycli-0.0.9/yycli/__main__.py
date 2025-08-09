#!/usr/bin/env python3
"""Main module for the application.
"""
import argparse
import importlib
from . import commands
from . import config

COMMANDS = {}


def register_command(parser: argparse.ArgumentParser, name: str,
                     command: callable, args_parser: callable):
    """register command
    """
    if args_parser is not None:
        args_parser(parser)

    COMMANDS[name] = {'name': name, 'type': 'command', 'command': command}


def register_plugin(parser: argparse.ArgumentParser, name: str,
                    plugin: callable, args_parser: callable, options):
    """register plugin
    """
    if args_parser is not None:
        args_parser(parser)

    COMMANDS[name] = {
        'name': name,
        'command': plugin,
        'type': 'plugin',
        'options': options
    }


def main():
    """Main entry point of the application.
    """
    parser = argparse.ArgumentParser(description='yycli')
    subparsers = parser.add_subparsers(help='commands',
                                       title='valid commands',
                                       dest='command')
    crypt_parser = subparsers.add_parser('crypt', help='crypt help')
    register_command(crypt_parser, 'crypt', commands.crypt.crypt,
                     commands.crypt.args_parser)
    confuse_parser = subparsers.add_parser('confuse', help='confuse help')
    register_command(confuse_parser, 'confuse', commands.confuse.entrypoint,
                     commands.confuse.args_parser)
    ipinfo_parser = subparsers.add_parser('ipinfo', help='ipinfo help')
    register_command(ipinfo_parser, 'ipinfo', commands.ipinfo.ipinfo,
                     commands.ipinfo.args_parser)
    weather_parser = subparsers.add_parser('weather', help='weather help')
    register_command(weather_parser, 'weather', commands.weather.weather,
                     commands.weather.args_parser)

    plugins_config = config.get('yycli.plugins')
    if isinstance(plugins_config, dict):
        for plugin_name, options in config.get('yycli.plugins').items():
            command = options.get('command', plugin_name)
            modpath = options.get('module', plugin_name)
            entry_name = options.get('entry', 'main')
            args_parser_name = options.get('args_parser', 'args_parser')

            try:
                module = importlib.import_module(modpath)
                entry = getattr(module, entry_name)
                args_parser = getattr(module, args_parser_name, None)

                command_parser = subparsers.add_parser(command,
                                                       help=f'{command} help')

                register_plugin(command_parser, command, entry, args_parser,
                                options)
            except ModuleNotFoundError:
                print(f'Error loading plugin {plugin_name} from {modpath}')
                print(f'Could not find module {modpath}')
                continue
            except AttributeError:
                print(f'Error loading plugin {plugin_name} from {modpath}')
                print(f'Could not find entry point {entry_name}')
                continue

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return

    command = COMMANDS[args.command]
    if command['type'] == 'command':
        command['command'](args)
    elif command['type'] == 'plugin':
        command['command'](args, command['options'])


if __name__ == '__main__':
    main()
