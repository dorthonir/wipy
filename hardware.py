from machine import Pin, I2C
import time

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

class ADS1115:
    Adc_register = {'CONV_REG':0x00, 'CONF_REG':0x01, 'LO_TRESH':0x02, 'HI_TRESH':0x03}
    Conf_Reg = bytearray(b'\x42\x80')
    Adc_channel = (bytearray(b'\x42\x80'), bytearray(b'\x52\x80'), bytearray(b'\x62\x80'), bytearray(b'\x72\x80'))
    Sel_channel = 0
    Num_of_channels = 2 # ilosc wykorzystywanych kanalow, tez mogla by byc ustawiana przez uzytkownika
    Next_channel = True
    Next_value= b'\x00'
    Adc_fsr = 4.096

    def __init__(self, fsr, sps):
        self.fsr = fsr
        self.sps = sps
        self.i2c = None
        self.pin = None
        self.initiated = 0
        self.continuous = 0
        self.deviceList = None
        self.Next_channel
        self.Next_value

    def init(self):
        self.i2c = i2c = I2C(0, I2C.MASTER, baudrate=400000)
        self.pin = p_in = Pin('P23', mode=Pin.IN, pull=Pin.PULL_UP)
        self.deviceList = self.i2c.scan()
        if len(self.deviceList) == 0:
            print("No I2C device connected!")
            return False
        else:
            print("I2C device connected!")
            i2c.writeto_mem(self.deviceList[0], self.Adc_register['CONF_REG'], bytes(self.Conf_Reg))
            # print(i2c.readfrom_mem(self.deviceList[0], Adc_register['CONF_REG'], 2))
            i2c.writeto_mem(self.deviceList[0], self.Adc_register['HI_TRESH'], b'\x80\x00') # ustawienie sygnalizacji zakonczenia konwersji
            i2c.writeto_mem(self.deviceList[0], self.Adc_register['LO_TRESH'], b'\x00\x00')
            time.sleep(1)
            self.pin.callback (Pin.IRQ_FALLING, self.readCurrentValue)
            self.initiated = 1

    def setFSR(self, value):
        self.fsr = value

    def getFSR(self):
        return self.fsr
    
    def setSPS(self, value):
        self.sps = value

    def getSPS(self):
        return self.sps
    
    def readCurrentValue(self, val):
        if self.Next_channel == True:
            self.Next_value = self.i2c.readfrom_mem(self.deviceList[0], self.Adc_register['CONV_REG'], 2)
            self.Next_channel = False
        else:
            pass

    def callbackA(self, channel, result):
        print(result)
        
    def continuousRead(self, callback):
        print('3')
        if (self.initiated == 1):
            self.continuous = 1
            while (self.continuous == 1):
                if self.Next_channel == False:
                    self.Sel_channel += 1
                    if self.Sel_channel == self.Num_of_channels:
                        self.Sel_channel = 0
                    self.i2c.writeto_mem(self.deviceList[0], self.Adc_register['CONF_REG'], bytes(self.Adc_channel[self.Sel_channel]))
                    result = ((self.Adc_fsr/32768)*int.from_bytes(self.Next_value,'big'))
                    self.callbackA(self.Sel_channel, result)
                    time.sleep(1)
                    self.Next_channel = True
                else:
                    pass
        else:
            print("Module was not initiated!")

    def startContinuousRead(self):
        self.continuousRead(self.callbackA)
