import network
import time
import machine
from umqtt.simple import MQTTClient


class Server:
    def __init__(self):
        self.wifi = None
        self.mqtt = None
        self.user = '0147ea70-e78f-11e8-809d-0f8fe4c30267'
        self.password = 'fc87ccfa48ef6e60f357b61605a43d4fc35df86a'
        self.client_id = 'cc6bda90-0378-11e9-b82d-f12a91579eed'
        self.server = 'mqtt.mydevices.com'
        self.port = 1883

    def startMqttService(self,callback):
        self.mqtt = MQTTClient(self.client_id, self.server, port=self.port, user=self.user, password=self.password)
        self.mqtt.set_callback(callback)

    def mqttPublishData(self, data, channel):
        topic = 'v1/{0}/things/{1}/data/{2}'.format(self.user,self.client_id,channel)
        self.mqtt.publish(topic,str(data))

    def mqttPublishResponse(self, sequence):
        topic = 'v1/{0}/things/{1}/response'.format(self.user,self.client_id)
        response = 'ok,' + str(sequence)
        self.mqtt.publish(topic,response)
    
    def sub_cb(self, topic, msg):
        string = msg.decode("utf-8")
        splittedMsg = string.split(',')
        sequence = splittedMsg[0]
        self.mqttPublishResponse(sequence)
        print(splittedMsg[-1])

    def mqttSubscribe(self, channel):
        topic = 'v1/{0}/things/{1}/cmd/{2}'.format(self.user,self.client_id,channel)
        self.mqtt.subscribe(topic)
        self.mqtt.check_msg()

    def connectToWIFI(self):
        self.wifi = network.WLAN(mode=network.WLAN.STA)
        nets = self.wifi.scan()
        counter = 0
        success = 0
        print('\nWybierz nr wifi:')
        for net in nets:
            security = ''
            if (net[2] == 0):
                security = 'brak hasla'
            else:
                security = 'siec zabezpieczona haslem'
            string = str(counter) + '. ' + str(net[0]) + ' - ' + security
            print(string)
            counter += 1

        while(not success):
            text = input("\nWybrany nr wifi: ")
            if (int(text)>(counter-1) | int(text)<0):
                print(int(counter))
                print("Wybrano niepoprawny numer")
            else:
                ssid = str(nets[int(text)][0])
                print(ssid)
                success = 1

        if (nets[int(text)][2] == 0):
            pwd = ''
        else:
            success = 0
            pwd = input("Wprowadz haslo: ")
            self.wifi.connect(nets[int(text)].ssid, auth=(nets[int(text)].sec, pwd), timeout=6000)
            while not self.wifi.isconnected():
                machine.idle() 

        self.wifi.ifconfig()

    def initServices(self):
        my_timezone = "CET-1CEST"
        rtc = machine.RTC()
        rtc.init((2019, 01, 01, 12, 12, 12))
        rtc.ntp_sync("pool.ntp.org")
        time.sleep(5)
        print("IP modulu: " + self.wifi.ifconfig()[0])