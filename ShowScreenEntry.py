import time

from PyQt5.QtWidgets import QApplication,QDialog, QMainWindow
from show_screen import Ui_MainWindow
import sys
import paho.mqtt.client as mqtt
import random
from pkt_common import get_payload, gen_pkt
from client_qt import screen_data_to_img, DEFAULT_MQTT_SERVER_PORT, DEFAULT_MQTT_SERVER


g_acc = '1234567890'#str(random.randrange(1000000,9999999,1))
g_pass = str(random.randrange(1000000,9999999,1))


def on_connect(client, userdata, flags, rc):
    userdata.on_connect(client, userdata, flags, rc)
def on_message(client,userdata, msg):
    print('on_message')
    userdata.on_message(client,userdata, msg)
def on_disconnect(client, userdata, rc):
    userdata.on_disconnect(client, userdata, rc)

class ShowScreenEntry(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.setupUi(self)

        self.t1=time.time()
        self.cnt=0

        self.client = mqtt.Client(transport='tcp')
        self.client.user_data_set(self)
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.on_disconnect = on_disconnect
        self.client.connect(DEFAULT_MQTT_SERVER, DEFAULT_MQTT_SERVER_PORT,60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print('connected')
        client.subscribe('/'+str(g_acc)+'/')

    def on_message(self, client,userdata, msg):
        #msg.payload
        #msg.topic
        #msg.qos
        command = get_payload(msg.payload, '')

        if len(command) == 0:
            return

        t2=time.time()
        self.cnt+=1
        if(t2-self.t1>10):
            print('frame:'+str(self.cnt/10.0) +'fps')
            self.t1=t2
            self.cnt=0

        self.pix=screen_data_to_img(command)
        #print(self.pix)
        #print(self.labelImage)
        self.labelImage.setPixmap(self.pix.scaled(640,640))
        #self.labelImage.resize(0.5 * self.labelImage.pixmap().size())
        self.labelImage.setStyleSheet("border: 2px solid")
        self.labelImage.setScaledContents(True)


    def on_disconnect(self, client, userdata, rc):
        print('client disconnect:', client)




if __name__ == '__main__':
    myapp = QApplication(sys.argv)
    myDlg = ShowScreenEntry()
    myDlg.show()
    sys.exit(myapp.exec_())


