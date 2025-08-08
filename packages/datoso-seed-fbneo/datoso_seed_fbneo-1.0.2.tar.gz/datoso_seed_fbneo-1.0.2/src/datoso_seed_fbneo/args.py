"""Argument parser for FinalBurn Neo seed."""
import platform
from argparse import ArgumentParser, Namespace

from datoso.configuration import config


def seed_args(parser: ArgumentParser) -> ArgumentParser:
    """Add seed arguments to the parser."""
    parser.add_argument('--fetch-full', type=bool, help='Fetch the full set of files.', default=True)
    parser.add_argument('--fetch-light', type=bool, help='Fetch the light set of files.', default=False)
    parser.add_argument('--source', type=str, help='Select source.',
                        default='finalburnneo', choices=['finalburnneo', 'libretro'])
    parser.add_argument('--system', help='Select system.',
                        default=None, choices=['win32', 'win64', 'linuxsdl1.2', 'linuxsdl2'])
    return parser

def post_parser(args: Namespace) -> None:
    """Post parser actions."""
    if getattr(args, 'fetch_full', None):
        config.set('FBNEO', 'FetchFull', str(args.fetch_full))
    if getattr(args, 'fetch_light', None):
        config.set('FBNEO', 'FetchLight', str(args.fetch_light))
    if getattr(args, 'source', None):
        config.set('FBNEO', 'DownloadFrom', args.source)
    if getattr(args, 'system', None):
        config.set('FBNEO', 'System', args.system)

def init_config() -> None:
    """Initialize the configuration."""
    default_values = {
        'FetchFull': True,
        'FetchLight': False,
        'DownloadFrom': 'finalburnneo',
    }
    if not config.has_section('FBNEO'):
        config['FBNEO'] = default_values
        # platform_system platform.system()
        # platform_system must be 'Windows' as linux executables are not supported:
        system = 'win32' if platform.architecture()[0] == '32bit' else 'win64'
        config.set('FBNEO', 'System', system)
    for key, value in default_values.items():
        if not config.has_option('FBNEO', key):
            config.set('FBNEO', key, str(value))
