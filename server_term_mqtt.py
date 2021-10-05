# coding:utf-8
import socket
import os
import select
import termios
import threading
import tty
import atexit
import fcntl
import struct
import sys
import time
import termios
from pkt_common import get_payload2, gen_pkt2
from mqtt_common import start_mqtt_connection
import random

g_old_settings = None
g_is_exit = 0
g_tk = '1234567890' #str(random.randrange(100000, 999999, 1))
g_topic_from_server='/'+g_tk+'/from_server'
g_topic_from_client='/'+g_tk+'/from_client'


def tty_to_raw():
    fd = sys.stdin.fileno()
    tty.setraw(fd)

def tty_setting_read():
    global g_old_settings
    fd = sys.stdin.fileno()
    g_old_settings = termios.tcgetattr(fd)


@atexit.register
def tty_restore():
    global g_old_settings
    fd = sys.stdin.fileno()
    termios.tcsetattr(fd, termios.TCSADRAIN, g_old_settings)


def read_local_and_send_to_remote(client):
    global g_is_exit
    try:
        fd = sys.stdin.fileno()
        while 1:
            # command = input()
            command = os.read(fd, 32)
            # for icmd in command:
            client.publish(g_topic_from_server, gen_pkt2(command, g_tk))

    except Exception as e:
        print('[-] Caught exception: ' + str(e))
        try:
            client.disconnect()
        except:
            pass
        print('exit:read_local_and_send_to_remote-1')
        sys.exit(1)


def remote_data_to_local(payload, userdata):
    output = payload
    output = get_payload2(output, g_tk)
    if len(output)>0:
        os.write(sys.stdout.fileno(), output)
        sys.stdout.flush()

def on_connect(client, userdata, flags, rc):
    tty_setting_read()
    tty_to_raw()
    print('connected')
    client.subscribe(g_topic_from_client)

def on_message(client,userdata, msg):
    #msg.payload
    #msg.topic
    #msg.qos
    remote_data_to_local(msg.payload, userdata)

def on_disconnect(client, userdata, rc):
    print('client disconnect:', client)

def server_one(server_host,server_port=12345):
    try:
        client = start_mqtt_connection(server_host, server_port, None, on_connect, on_message, on_disconnect)
    except Exception as e:
        print('[-] Listen/Bind/Accept failed: ' + str(e))
        sys.exit(1)

    # recv remote and display
    #t = threading.Thread(target=recv_remote_and_display_to_local, args=(client,))
    #t.start()
    # read input and send
    read_local_and_send_to_remote(client)


if __name__ == '__main__':
    remote_port = 12345
    if len(sys.argv) < 3:
        print('usage: prog remote_host remote_port')
        remote_host = 'test.mosquitto.org'
        remote_port=1883
    else:
        remote_host = sys.argv[1]
        remote_port = int(sys.argv[2])

    if len(sys.argv)>3:
        g_tk = str(sys.argv[3])

    server_one(remote_host, remote_port)
