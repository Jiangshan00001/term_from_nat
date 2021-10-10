import sys, getopt
import random
from server_term import ServerTerm
from client_term import ClientTerm

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hst:b:p:f:", ['help', 'server', 'token', 'bridge', 'port', 'prefix'])
    except getopt.GetoptError:
        print('prog -h')

    join_a_client = False
    token = str(random.randrange(100000, 999999, 1))
    server = 'test.mosquitto.org'
    port = 1883
    prefix = ''
    for opt, arg in opts:
        if opt == ('-h', '--help'):
            print(
                'prog -s i am a server, connect to a client(no new session), . -t token, this is optional for client, must be set for server. -b bridge(default is test.mosquitto.org). -p port(default is 1883). -f topic prefix(default \'\') ')
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
            print('client started, use: term_from_nat -s -t  ' + token + ' -b ' + server + ' -p ' + str(
                port) + ' -f ' + prefix + '\n to start the server')
        else:
            print('client started, use: term_from_nat -s -t  ' + token + ' -b ' + server + ' -p ' + str(
                port) + '\n to start the server')
        client.start_server()
