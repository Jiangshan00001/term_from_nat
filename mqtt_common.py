from paho.mqtt import client as mqtt


def on_connect_default(client, userdata, flags, rc):
    userdata.on_connect(client, userdata, flags, rc)


def on_message_default(client, userdata, msg):
    userdata.on_message(client, userdata, msg)


def on_disconnect_default(client, userdata, rc):
    userdata.on_disconnect(client, userdata, rc)


def start_mqtt_connection(server, port, user_data, on_connect=None, on_message=None, on_disconnect=None):
    client = mqtt.Client(transport='tcp')
    client.user_data_set(user_data)
    client.on_connect = on_connect if on_connect is not None else on_connect_default
    client.on_message = on_message if on_connect is not None else on_message_default
    client.on_disconnect = on_disconnect if on_connect is not None else on_disconnect_default
    print('connecting:', server, port)
    client.connect(server, port, 60)
    client.loop_start()
    return client
