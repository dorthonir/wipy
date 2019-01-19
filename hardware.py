# Dawid Gizan & Piotr Biernacki 2019

# Domyslnie  FSR = 4,096 ORAZ  SPS= 128. FSR przyjmowac moze wartosci : 0,256V ; 0,512 ; 1,024 ; 2,048; 4,096; 6,144
# czestotliwosc probkowania 8 SPS, 16  32 64 128 250 475 860
#
# JEŻELI 
# FSR = 6,144 to   Conf_Reg[0]= b'\x40'
# FSR = 4,096 to   Conf_Reg[0]= b'\x42'
# FSR = 2,048 to   Conf_Reg[0]= b'\x44'
# FSR = 1,024 to   Conf_Reg[0]= b'\x46'
# FSR = 0,512 to   Conf_Reg[0]= b'\x48'
# FSR = 0,256 to   Conf_Reg[0]= b'\x4A'
#
# JEŻELI 
# SPS = 8 to     Conf_Reg[1]=b'\x00'
# SPS = 16 to    Conf_Reg[1]=b'\x20'
# SPS = 32 to    Conf_Reg[1]=b'\x40'
# SPS = 64 to    Conf_Reg[1]=b'\x60'
# SPS = 128 to   Conf_Reg[1]=b'\x80'
# SPS = 250 to   Conf_Reg[1]=b'\xA0'
# SPS = 475 to   Conf_Reg[1]=b'\xC0'
# SPS = 860 to   Conf_Reg[1]=b'\xE0'
#
# Po zmianie FSR zmienic sie musi Adc_fsr na atualną wartosci
# po wyliczeniu nowego Conf_Reg zmienic się musi takze Adc_channel w taki sposób, że na początku kolejnych zawsze 
# będzie b'\x4...', b'\x5...', b'\x6...' , b'\x7...' (najłatwiej chyba będzie dodawac 16 do kolejnych Adc_channel(n)(1)

from machine import Pin, I2C
import time


class Channel:

    def __init__(self):
        self.fsr = "4.096"
        self.sps = "128"

    def setFSR(self, value):
        self.fsr = value

    def getFSR(self):
        return self.fsr
    
    def setSPS(self, value):
        self.sps = value

    def getSPS(self):
        return self.sps
    
    
class ADS1115:

    Adc_register = {'CONV_REG':0x00, 'CONF_REG':0x01, 'LO_TRESH':0x02, 'HI_TRESH':0x03}
    Conf_Reg = bytearray(b'\x42\x80')
    Next_channel = True
    Next_value= b'\x00'
    Adc_fsr = 4.096
    nrOfChannels = 4
    channel = []
    FSR = {"6.144":b'\x40',
            "4.096":b'\x42',
            "2.048":b'\x44',
            "1.024":b'\x46',
            "0.512":b'\x48',
            "0.256":b'\x4A'}

    SPS = {"8":b'\x00',
            "16":b'\x20',
            "32":b'\x40',
            "64":b'\x60',
            "128":b'\x80',
            "250":b'\xA0',
            "475":b'\xC0',
            "860":b'\xE0'}

    def __init__(self, channel):
        self.fsr = "4.096"
        self.sps = "128"
        self.i2c = None
        self.pin = None
        self.i2cID = None
        self.initiated = 0
        self.deviceList = None
        self.Next_value

    def init(self, i2cID, i2c, pin):
        self.i2c = i2c
        self.pin = pin
        self.i2cID = i2cID
        self.pin.callback (Pin.IRQ_FALLING, self.readCurrentValue)
        self.initiated = 1
        print("I2C device connected!")

    def configureModule(self):
        self.i2c.writeto_mem(self.i2cID[0], self.Adc_register['CONF_REG'], bytes(self.Conf_Reg))
        self.i2c.writeto_mem(self.i2cID[0], self.Adc_register['HI_TRESH'], b'\x80\x00') # ustawienie sygnalizacji zakonczenia konwersji
        self.i2c.writeto_mem(self.i2cID[0], self.Adc_register['LO_TRESH'], b'\x00\x00')

    def initChannels(self):
        for n in range(self.nrOfChannels):
            self.channel[n] = Channel()
    
    def readCurrentValue(self, val):
        self.Next_value = self.i2c.readfrom_mem(self.i2cID[0], self.Adc_register['CONV_REG'], 2)
        print(self.Next_value)

    def continuousRead(self, channel, callback):
        if self.initiated:
            sps = self.SPS[self.sps]
            fsr = self.FSR[self.fsr]
            self.i2c.writeto_mem(self.i2cID[0], self.Adc_register['CONF_REG'], (b''.join((fsr,sps))))
            result = ((float(self.fsr)/32768)*int.from_bytes(self.Next_value,'big'))
            callback(channel, result)
            time.sleep(0.15)
        else:
            print("Module not initiated!")