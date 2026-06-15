import argparse


def get_parser():
    parser = argparse.ArgumentParser(
                        prog='WTF - Wi-Fi Test Framework',
                        description='Wi-Fi Test Framework. Full documentation: github.com/KOROBYAKA/WTF')
    subparsers = parser.add_subparsers(dest="command", help='subcommand help', required=True,)
    #Adding parser for preflight check
    parser_preflight = subparsers.add_parser('preflight',help='WTF check if the setup is ok')
    parser_preflight.add_argument('-c', '--config',help="Path to config file", default="conf.toml")
    parser_preflight.add_argument('--debug', default=False, action='store_true')


    #Adding subparser for check-config
    parser_conf_check = subparsers.add_parser('check-config', help='WTF check config if it is valid')
    parser_conf_check.add_argument('-c', '--config',help="Path to config file", default="conf.toml")
    parser_conf_check.add_argument('--debug', default=False, action='store_true')

    #Adding subparser for running
    parser_run = subparsers.add_parser('run', help='WTF check config if it is valid')
    parser_run.add_argument('-c', '--config',help="Path to config file", default="conf.toml")
    parser_run.add_argument('--debug', default=False, action='store_true')

    #Adding subparser for plotting
    parser_plot = subparsers.add_parser('plot', help='Plot WTF results')
    parser_plot.add_argument('path', nargs='?', help="Path to results.json or a result directory")
    parser_plot.add_argument('--path', dest='path_option', help="Path to results.json or a result directory")
    parser_plot.add_argument('--debug', default=False, action='store_true')

    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.2.0')



    return parser

def parse(parser):

    args = parser.parse_args()
    return args
