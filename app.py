# Piotr Biernacki 2019

import hardware
import serwer
import time
from machine import Pin, I2C


class App:

    sliderFSR = '2'
    sliderSPS = '3'
    buttonCh0 = '4'
    buttonCh1 = '5'

    def __init__(self,server,module):
        self.server = server
        self.module = module
        self.button0 = None
        self.button1 = None
        self.FSRval = "4.096"
        self.SPSval = "128"
        self.i2c = None
        self.pin = None

    def init(self):

        i2cDevices = self.scanI2C()
        if i2cDevices is not None:
            self.module.init(i2cDevices, self.i2c, self.pin)

        self.server.connectToWIFI()
        self.server.initServices()
        self.server.startMqttService(self.sub_cb)
        self.server.mqtt.connect()

        #ustawienie domyslnych wartosci na sliderach
        self.server.mqttPublishData(2,int(self.sliderFSR))
        self.server.mqttPublishData(5,int(self.sliderSPS))

    def scanI2C(self):
        self.i2c = i2c = I2C(0, I2C.MASTER, baudrate=400000)
        self.pin = p_in = Pin('P23', mode=Pin.IN, pull=Pin.PULL_UP)
        deviceList = self.i2c.scan()
        if len(deviceList) == 0:
            print("No I2C device connected!")
            return False
        else:
            return deviceList

    def parseReceivedMsg(self, topic, msg):
        stringMsg = msg.decode("utf-8")
        stringTopic = topic.decode("utf-8")
        splittedMsg = stringMsg.split(',')
        splittedTopic = stringTopic.split('/')
        sequence = splittedMsg[0]
        data = splittedMsg[-1]
        channel = splittedTopic[-1]
        return (channel,data), sequence

    def sub_cb(self, topic, msg):
        receivedData, sequence = self.parseReceivedMsg(topic,msg)
        self.classifyData(receivedData)
        self.server.mqttPublishResponse(sequence)

    def classifyData(self, receivedData):
        if (receivedData[0] ==  self.sliderFSR):
            if receivedData[1] == '1':
                self.module.setFSR("6.144")
            elif receivedData[1] == '2':
                self.module.setFSR("4.096")
            elif receivedData[1] == '3':
                self.module.setFSR("2.048")
            elif receivedData[1] == '4':
                self.module.setFSR("1.024")
            elif receivedData[1] == '5':
                self.module.setFSR("0.512")
            elif receivedData[1] == '6':
                self.module.setFSR("0.256")
        elif (receivedData[0] ==  self.sliderSPS):
            if receivedData[1] == '1':
                self.module.setSPS("8")
            elif receivedData[1] == '2':
                self.module.setSPS("16")
            elif receivedData[1] == '3':
                self.module.setSPS("32")
            elif receivedData[1] == '4':
                self.module.setSPS("64")
            elif receivedData[1] == '5':
                self.module.setSPS("128")
            elif receivedData[1] == '6':
                self.module.setSPS("250")
            elif receivedData[1] == '7':
                self.module.setSPS("475")
            elif receivedData[1] == '8':
                self.module.setSPS("860")
        elif (receivedData[0] ==  self.buttonCh0):
            self.button0 = int(receivedData[1])
        elif (receivedData[0] ==  self.buttonCh1):
            self.button1 = int(receivedData[1])

    def read_cb(self, channel, result):
        read = 'ADC - ' + str(channel) + ': ' + str(result)
        self.server.mqttPublishData(result,channel)
        print(read)

    def loop(self):
        while 1:
            if self.button0 == 1:
                self.module.continuousRead(0, self.read_cb)
            if self.button1 == 1:
                self.module.continuousRead(1, self.read_cb)
            
            self.server.mqttSubscribe(2)
            self.server.mqttSubscribe(3)
            self.server.mqttSubscribe(4)
            self.server.mqttSubscribe(5)

        self.server.mqtt.disconnect()