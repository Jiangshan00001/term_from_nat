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
g_is_exit=0

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
    if g_old_settings is not None:
        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSADRAIN, g_old_settings)


class ServerTerm:
    def __init__(self):
        self.token = ''
        self.bridge_server = ''
        self.bridge_port = 1883
        self.bridge_topic_prefix = ''
        self.pty_master_fd = None
        self.pty_name = None
        self.topic_from_server = ''
        self.topic_from_client = ''

    def set_token(self, token):
        self.token = token

    def set_bridge(self, bridge_server, bridge_port, bridge_topic_prefix):
        self.bridge_server = bridge_server
        self.bridge_port = bridge_port
        self.bridge_topic_prefix = bridge_topic_prefix

    def local_data_to_remote(self):
        global g_is_exit
        try:
            fd = sys.stdin.fileno()
            while 1:
                command = os.read(fd, 32)
                self.client.publish(self.topic_from_server, gen_pkt2(command, self.token))

        except Exception as e:
            print('[-] Caught exception: ' + str(e))
            try:
                self.client.disconnect()
            except:
                pass
            print('exit:read_local_and_send_to_remote-1')
            sys.exit(1)

    def remote_data_to_local(self, payload):
        output = payload
        output = get_payload2(output, self.token)
        if len(output) > 0:
            os.write(sys.stdout.fileno(), output)
            sys.stdout.flush()

        if output==b'exited':
            global g_is_exit
            self.client.disconnect()
            g_is_exit=1

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe(self.topic_from_client)
        tty_setting_read()
        tty_to_raw()
        print('connected')

    def on_message(self, client, userdata, msg):
        self.remote_data_to_local(msg.payload)

    def on_disconnect(self, client, userdata, rc):
        print('client disconnect:', client)

    def start_server(self):
        self.topic_from_client = self.bridge_topic_prefix + '/' + self.token + '/from_client'
        self.topic_from_server = self.bridge_topic_prefix + '/' + self.token + '/from_server'

        try:
            self.client = start_mqtt_connection(self.bridge_server, self.bridge_port, self)
        except Exception as e:
            print('[-] Listen/Bind/Accept failed: ' + str(e))
            sys.exit(1)

        self.local_data_to_remote()
