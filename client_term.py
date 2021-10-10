# coding:utf-8
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


class ClientTerm:
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

    def start_pty(self):
        # open pseudo-terminal to interact with subprocess
        self.pty_master_fd, slave_fd = pty.openpty()

        # use os.setsid() make it run in a new process group, or bash job control will not be enabled
        self.proc = subprocess.Popen('bash',
                                     preexec_fn=os.setsid,
                                     stdin=slave_fd,
                                     stdout=slave_fd,
                                     stderr=slave_fd,
                                     universal_newlines=True
                                     )

        self.pty_name = os.ttyname(slave_fd)

    def close_pty(self):
        if self.pty_master_fd is not None:
            pass
        os.write(self.pty_master_fd, b'exit\n')
        os.close(self.pty_master_fd)
        self.pty_master_fd = None
        self.pty_name = None

    def on_connect(self, client, userdata, flags, rc):
        print('bridge connected')
        self.client.subscribe(self.topic_from_server)

    def on_message(self, client, userdata, msg):
        self.remote_data_to_local(msg.payload, self.pty_master_fd)

    def on_disconnect(self, client, userdata, rc):
        print('client disconnect:', client)

    def remote_data_to_local(self, remote_data, master_fd):
        output = remote_data
        command = get_payload2(output, self.token)
        if len(command) == 0:
            return
        os.write(master_fd, command)

    def local_data_to_remote(self):
        try:
            while self.proc.poll() == None:
                reta = select.select([self.pty_master_fd], [], [])
                if reta[0]:
                    output = os.read(self.pty_master_fd, 1024)
                    os.write(sys.stdout.fileno(), output)
                    # sys.stdout.write(output.decode('utf-8'))
                    sys.stdout.flush()

                    if len(output) > 0:
                        cmd = gen_pkt2(output, self.token)
                        if self.client.is_connected():
                            self.client.publish(self.topic_from_client, cmd)  # .decode('utf-8')
                        else:
                            print('local_data_to_remote: no connect. drop data')
        except Exception as e:
            print('local_data_to_remote error:')
            print(e)

        print('exit:local_data_to_remote')

        cmd = gen_pkt2(b'exited', self.token)
        self.client.publish(self.topic_from_client, cmd)  # .decode('utf-8')
        time.sleep(2)
        self.client.disconnect()
        self.close_pty()

    def start_server(self):
        self.start_pty()

        self.topic_from_client = self.bridge_topic_prefix + '/' + self.token + '/from_client'
        self.topic_from_server = self.bridge_topic_prefix + '/' + self.token + '/from_server'

        self.client = start_mqtt_connection(self.bridge_server, self.bridge_port, self)
        self.client.publish(self.topic_from_client,
                            gen_pkt2(('Hi Im connected :)' + self.pty_name + '\n').encode('utf-8'), self.token))

        self.local_data_to_remote()

        print('exit:client_one')
        sys.exit(0)
