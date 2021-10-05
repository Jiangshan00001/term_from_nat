import select
import threading
import subprocess

import sys
import socket
import time
import pty
import os
import random
import paho.mqtt.client as mqtt

from pkt_common import get_payload2, gen_pkt2
from mqtt_common import start_mqtt_connection
g_is_exit = 0

g_tk='1234567890'#str(random.randrange(100000,999999,1))
g_topic_from_server='/'+g_tk+'/from_server'
g_topic_from_client='/'+g_tk+'/from_client'
def remote_data_to_local(remote_data, master_fd):
        output = remote_data
        command = get_payload2(output,g_tk)

        if len(command) == 0:
            return
        os.write(master_fd, command)


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
                    if client.is_connected():
                        client.publish(g_topic_from_client, cmd)  # .decode('utf-8')
                    else:
                        print('local_data_to_remote: no connect. drop data')
    except Exception as e:
        print('local_data_to_remote error:')
        print(e)

    print('exit:local_data_to_remote')
    global g_is_exit
    g_is_exit = 1

    cmd = gen_pkt2(b'exited', g_tk)
    client.publish(g_topic_from_client,cmd )  # .decode('utf-8')
    time.sleep(2)
    client.disconnect()
    os.close(master_fd)
    sys.exit(0)

def on_connect(client, userdata, flags, rc):
    print('connected')
    client.subscribe(g_topic_from_server)

def on_message(client,userdata, msg):
    #msg.payload
    #msg.topic
    #msg.qos
    remote_data_to_local(msg.payload, userdata)

def on_disconnect(client, userdata, rc):
    print('client disconnect:', client)

def client_one(remote_host, remote_port):

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

    client = start_mqtt_connection(remote_host, remote_port,master_fd, on_connect, on_message, on_disconnect)
    client.publish(g_topic_from_client, gen_pkt2( ('Hi Im connected :)' + tty_name + '\n').encode('utf-8'), g_tk))


    local_data_to_remote(proc, master_fd, client)

    print('exit:client_one')
    client.disconnect()
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('usage: prog remote_host remote_port')
        remote_host = 'test.mosquitto.org'
        remote_port=1883
    else:
        remote_host = sys.argv[1]
        remote_port = int(sys.argv[2])

    if len(sys.argv)>3:
        g_tk = str(sys.argv[3])
    client_one(remote_host, remote_port)
