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
import struct
    
class ADS1115:

    Adc_register = {'CONV_REG':0x00, 'CONF_REG':0x01, 'LO_TRESH':0x02, 'HI_TRESH':0x03}
    chanMasks = [0x04, 0x05, 0x06, 0x07]
    FSRmask = {"6.144":0x00,
            "4.096":0x02,
            "2.048":0x04,
            "1.024":0x06,
            "0.512":0x08,
            "0.256":0x0A}

    SPSmask = {"8":0x00,
            "16":0x20,
            "32":0x40,
            "64":0x60,
            "128":0x80,
            "250":0xA0,
            "475":0xC0,
            "860":0xE0}

    def __init__(self):
        self.i2c = None
        self.pin = None
        self.fsr = "4.096"
        self.sps = "128"
        self.channel = 0
        self.i2cID = None
        self.initiated = 0
        self.deviceList = None
        self.Next_value = 0
        self.Adc_fsr = 4.096

    def init(self, i2cID, i2c, pin):
        self.i2c = i2c
        self.pin = pin
        self.i2cID = i2cID
        self.configureModuleFSR(self.fsr)
        self.pin.callback (Pin.IRQ_FALLING, self.readCurrentValue)
        self.initiated = 1
        print("I2C device connected!")

    def configureModuleFSR(self, fsr):
        self.fsr= fsr
        regH = (self.chanMasks[self.channel] << 4) | self.FSRmask[self.fsr]
        regL = self.SPSmask[self.sps]
        reg = bytes([regH,regL])
        self.i2c.writeto_mem(self.i2cID[0], self.Adc_register['CONF_REG'], reg)
        self.i2c.writeto_mem(self.i2cID[0], self.Adc_register['HI_TRESH'], b'\x80\x00')
        self.i2c.writeto_mem(self.i2cID[0], self.Adc_register['LO_TRESH'], b'\x00\x00')
    
    def configureModuleSPS(self, sps):
        self.sps= sps
        regH = self.FSRmask[self.fsr]
        regL = self.SPSmask[self.sps]
        reg = bytes([regH,regL])
        self.i2c.writeto_mem(self.i2cID[0], self.Adc_register['CONF_REG'], reg)

    def configureChannel(self, channel):
        self.channel = channel
        regH = (self.chanMasks[self.channel] << 4) | self.FSRmask[self.fsr]
        regL = self.SPSmask[self.sps]
        reg = bytes([regH,regL])
        self.i2c.writeto_mem(self.i2cID[0], self.Adc_register['CONF_REG'], reg)
    
    def readCurrentValue(self, val):
        self.newVal = 1

    def getVal(self):
        samples = 16
        sum = 0
        cnt = 0
        while cnt<samples:
            if self.newVal == 1:
                value = self.i2c.readfrom_mem(self.i2cID[0], self.Adc_register['CONV_REG'], 2)
                self.newVal = 0
                decoded = int.from_bytes(value,'big')
                sum += decoded
                cnt+=1
            
        div = sum/samples
        val = ((float(self.fsr)/32768)*div)
        return val

    def continuousRead(self, channel, callback):
        if self.initiated:
            result = self.getVal()
            callback(channel, result)
        else:
            print("Module not initiated!")