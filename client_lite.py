import select
import threading
import subprocess
# from PIL import ImageGrab
import sys
import socket
import time
import pty
import os

g_is_exit = 0


def remote_data_to_local(client, master_fd):
    global g_is_exit
    while True:
        if g_is_exit == 1:
            print('exit:remote_data_to_local-1')
            sys.exit(0)

        reta = select.select([client.fileno()], [], [client.fileno()], 0.5)
        if reta[0]:
            output = os.read(client.fileno(), 1024)
            command = output
            if len(command) == 0:
                continue

            os.write(master_fd, command)
            if command.strip() == b'exit':
                os.write(master_fd, b'\n')
                client.close()
                print('exit:remote_data_to_local-2')
                sys.exit(0)
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
                sys.stdout.write(output.decode('utf-8'))
                sys.stdout.flush()

                if len(output) > 0:
                    client.send(output)  # .decode('utf-8')
    except Exception as e:
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
    client.send(('Hi Im connected :)' + tty_name + '\n').encode('utf-8'))

    t = threading.Thread(target=remote_data_to_local, args=(client, master_fd))
    t.start()
    # pid = os.fork()
    # if pid:
    # child process. do read load, sendto remove
    # os.close(slave_fd)
    local_data_to_remote(proc, master_fd, client)
    # else:
    #    # main process. do write to local.
    #    remote_data_to_local(client,master_fd)

    print('exit:client_one')
    client.close()
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('usage: prog remote_host remote_port')
        sys.exit(0)
    remote_host = sys.argv[1]
    remote_port = int(sys.argv[2])

    client_one(remote_host, remote_port)
