from paho.mqtt import client as mqtt

def start_mqtt_connection(server, port, user_data, on_connect, on_message, on_disconnect):
    client = mqtt.Client(transport='tcp')
    client.user_data_set(user_data)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    print('connecting:', server, port)
    client.connect(server, port, 60)
    client.loop_start()
    return client
