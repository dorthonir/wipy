# Piotr Biernacki 2019

import hardware
import serwer
import time
from machine import Pin, I2C


class App:

    sliderFSR = '8'
    sliderSPS = '9'
    buttonsList = ['4','5','6','7']
    sliderFSRlist = ["6.144", "4.096", "2.048", "1.024", "0.512", "0.256"]
    sliderSPSlist = ["8", "16", "32", "64", "128", "250", "475", "860"]

    def __init__(self,server,module):
        self.server = server
        self.module = module
        self.buttons = [0,0,0,0]
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

        #ustawienie domyslnych wartosci na serwerze
        self.server.mqttPublishData(2,int(self.sliderFSR))
        self.server.mqttPublishData(5,int(self.sliderSPS))
        self.server.mqttPublishData(0,int(self.buttonsList[0]))
        self.server.mqttPublishData(0,int(self.buttonsList[1]))
        self.server.mqttPublishData(0,int(self.buttonsList[2]))
        self.server.mqttPublishData(0,int(self.buttonsList[3]))


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
        data = int(receivedData[1])
        if (receivedData[0] ==  self.sliderFSR):
            self.module.fsr = self.sliderFSRlist[data]
            self.module.configureModuleFSR(self.module.fsr)
            print("FSR set to: " + self.module.fsr)

        elif (receivedData[0] ==  self.sliderSPS):
            self.module.sps = self.sliderSPSlist[data]
            self.module.configureModuleSPS(self.module.sps)
            print("SPS set to: " + self.module.sps)

        elif any(receivedData[0] in s for s in self.buttonsList):
            position = [i for i,x in enumerate(self.buttonsList) if x == receivedData[0]]
            self.buttons[position[0]] = data
            if (data == 1):
                state = 'on'
            else:
                state = 'off'
            string = "Channel: " + str(position[0]) + ' ' + state
            print(string)

    def read_cb(self, channel, result):
        read = 'ADC - ' + str(channel) + ': ' + str(result)
        self.server.mqttPublishData(result,channel)
        print(read)

    def loop(self):
        while 1:
            for n in range(len(self.buttons)):
                if self.buttons[n] == 1:
                    self.module.configureChannel(n)
                    time.sleep(0.15)
                    self.module.continuousRead(n, self.read_cb)

            for n in range(len(self.buttonsList)):
                self.server.mqttSubscribe(self.buttonsList[n])

            self.server.mqttSubscribe(self.sliderFSR)
            self.server.mqttSubscribe(self.sliderSPS)

        self.server.mqtt.disconnect()