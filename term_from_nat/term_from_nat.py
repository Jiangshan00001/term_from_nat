#!/usr/bin/env python3
#coding:utf-8

import sys, getopt
import random
from .server_term import ServerTerm
from .client_term import ClientTerm


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hst:b:p:f:", ['help', 'server', 'token', 'bridge', 'port', 'prefix'])
    except getopt.GetoptError:
        print('prog -h')

    join_a_client = False
    token = str(random.randrange(100000, 999999, 1))
    server = 'broker-cn.emqx.io' # or 'test.mosquitto.org'
    port = 1883
    prefix = ''
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(
                'prog -s -t token -b bridge_server_name -p bridge_server_port -f topic_prefix\n'
                '\t-s i am a server, connect to a client(no new session),\n'
                '\t-t token, this is optional for client, must be set for server.\n'
                '\t-b bridge(default is test.mosquitto.org). \n'
                '\t-p port(default is 1883). -f topic prefix(default \'\') \n')
            sys.exit()
        elif opt in ("-s", "--server"):
            join_a_client = True
        elif opt in ("-t", "--token"):
            token = arg
        elif opt in ("-b", "--bridge"):
            server = arg
        elif opt in ("-p", "--port"):
            port = int(arg)
        elif opt in ("-f", "--prefix"):
            prefix = prefix

    if join_a_client:
        print('starting a server to control remote client...')
        servert = ServerTerm()
        servert.set_token(token)
        servert.set_bridge(server, port, prefix)
        servert.start_server()
    else:
        print('starting a client to be controlled...')
        client = ClientTerm()
        client.set_token(token)
        client.set_bridge(server, port, prefix)
        if len(prefix) > 0:
            print('client started, USE: \nterm_from_nat -s -t  ' + token + ' -b ' + server + ' -p ' + str(
                port) + ' -f ' + prefix + '\n TO START THE SERVER from another computer')
        else:
            print('client started, USE: \nterm_from_nat -s -t  ' + token + ' -b ' + server + ' -p ' + str(
                port) + '\n TO START THE SERVER from another computer')
        client.start_server()


if __name__ == '__main__':
    main()