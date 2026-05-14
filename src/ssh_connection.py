from contextlib import contextmanager
import paramiko

@contextmanager
def get_client(target_ip):
    username = input ("Enter login: ")
    passwd = input("Enter password: ")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #if you have a specific port which is not 22, add a "port=*port_value*" into the function parameters
    client.connect(target_ip,password=passwd,username=username)
    yield client
    client.close()

def remote_execution(client, cmds):
    results = []
    for cmd in cmds:
        _, stdout, _ = client.exec_command(cmd)
        results.append(stdout.read().decode().strip())

    return results
