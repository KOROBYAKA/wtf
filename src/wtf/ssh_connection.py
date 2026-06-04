from wtf.tooling import debug_printer
import paramiko
from getpass import getpass

@debug_printer
def get_client(target_ip):
    username = input ("Enter login: ")
    passwd = getpass("Enter password: ")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #if you have a specific port which is not 22, add a "port=*port_value*" into the function parameters
    client.connect(target_ip, username=username, password=passwd)

    print("#DEBUG")
    print("SSH Client is up")

    return client

@debug_printer
def remote_execution(client, cmds):
    results = []
    result_codes = []
    for cmd in cmds:
        _, stdout, _ = client.exec_command(cmd)
        results.append(stdout.read().decode().strip())
        result_codes.append(stdout.channel.recv_exit_status())

    return results, result_codes
