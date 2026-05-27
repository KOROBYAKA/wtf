import argparse


def get_parser():
    parser = argparse.ArgumentParser(
                        prog='WTF - Wi-Fi Test Framework',
                        description='Wi-Fi Test Framework. Full documentation: github.com/KOROBYAKA/WTF')
    subparsers = parser.add_subparsers(dest="command", help='subcommand help', required=True,)

    #Adding subparser for check-config
    parser_conf_check = subparsers.add_parser('check-config', help='WTF check config if it is valid')
    parser_conf_check.add_argument('-c', '--config',help="Path to config file", default="conf.toml")
    parser_conf_check.add_argument('--debug', default=False, action='store_true')

    #Adding subparser for running
    parser_run = subparsers.add_parser('run', help='WTF check config if it is valid')
    parser_run.add_argument('-c', '--config',help="Path to config file", default="conf.toml")
    parser_run.add_argument('--debug', default=False, action='store_true')

    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')


    return parser

def parse(parser):

    args = parser.parse_args()
    return args