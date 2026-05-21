import sys
from argparse import ArgumentParser


def get_parser():
    parser = ArgumentParser(
                        prog='WTF - Wi-Fi Test Framework',
                        description='Wi-Fi Test Framework. Full documentation: github.com/KOROBYAKA/WTF')

    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    parser.add_argument("--config",help="Path to config file", default="conf.toml")
    return parser

def parse(parser):
    args = parser.parse_args()
    return args