import hardware
import serwer
import machine
import network
import time

class main:

    def __init__(self,server,module):
        self.server = server
        self.module = module

    def init(self):
        
        server.connectToWIFI()
        server.initServices()
        
        module.init()
        # module.startContinuousRead()


server = serwer.Server()
module = hardware.ADS1115(2,5 )
main = main(server,module)
main.init()

server.mqttPublishData('1602',0)

# module.init()
# module.startContinuousRead()


# server.mqttSubscribe(1)
server.mqttSubscribe(1)





# from machine import Pin, I2C
# import time
# Adc_register = {'CONV_REG':0x00, 'CONF_REG':0x01, 'LO_TRESH':0x02, 'HI_TRESH':0x03}
# Conf_Reg = bytearray(b'\x42\x80')
# Adc_channel = (bytearray(b'\x42\x80'), bytearray(b'\x52\x80'), bytearray(b'\x62\x80'), bytearray(b'\x72\x80'))
# Sel_channel = 0
# Num_of_channels = 2 # ilosc wykorzystywanych kanalow, tez mogla by byc ustawiana przez uzytkownika
# Next_channel = False
# Next_value= b'\x00'
# Adc_fsr = 4.096

# # Domyslnie  FSR = 4,096 ORAZ  SPS= 128. FSR przyjmowac moze wartosci : 0,256V ; 0,512 ; 1,024 ; 2,048; 4,096; 6,144
# # czestotliwosc probkowania 8 SPS, 16  32 64 128 250 475 860
# # JEŻELI FSR = 6,144  to Conf_Reg[0]=b'\x40'; 4,096 Conf_Reg[0]=b'\x42'; 2,048 Conf_Reg[0]= b'/x44'; 1,024 Conf_Reg[0]= b'\x46'; 0,512 Conf_Reg[0]= b'\x48'; 0,256 Conf_Reg[0]=b'\x4A'
# # JEŻELI SPS = 8 to   Conf_Reg[1]=b'\x00'; SPS = 16 to   Conf_Reg[1]=b'\x20';SPS = 32 to   Conf_Reg[1]=b'\x40';SPS = 64 to   Conf_Reg[1]=b'\x60';SPS = 128   to   Conf_Reg[1]=b'\x80'; SPS = 250 to   Conf_Reg[1]=b'\xA0'; SPS = 475 to   Conf_Reg[1]=b'\xC0'; SPS = 860 to   Conf_Reg[1]=b'\xE0';
# # Po zmianie FSR zmienic sie musi Adc_fsr na atualną wartosci
# #  po wyliczeniu nowego Conf_Reg zmienic się musi takze Adc_channel  w taki sposób ,że na początku kolejnych zawsze będzie b'\x4...', b'\x5...', b'\x6...' , b'\x7...' (najłatwiej chyba będzie dodawac 16 do kolejnych Adc_channel(n)(1)

# def pin_handler(arg):
#     global Next_channel
#     global Next_value
#     if Next_channel == True:
#         Next_value = i2c.readfrom_mem(Device_list[0], Adc_register['CONV_REG'], 2)
#         Next_channel = False
#     else:
#         pass

# i2c = I2C(0, I2C.MASTER, baudrate=400000)
# Device_list = i2c.scan()
# if len(Device_list) == 0:
#     # jakis komunikat
#     pass
# else:
#     p_in = Pin ('P23', mode=Pin.IN, pull=Pin.PULL_UP)
#     p_in.callback (Pin.IRQ_FALLING, pin_handler)
#     i2c.writeto_mem(Device_list[0], Adc_register['CONF_REG'], bytes(Conf_Reg))
#     print(i2c.readfrom_mem(Device_list[0], Adc_register['CONF_REG'], 2))
#     i2c.writeto_mem(Device_list[0], Adc_register['HI_TRESH'], b'\x80\x00') #   ustawienie sygnalizacji zakonczenia konwersji
#     i2c.writeto_mem(Device_list[0], Adc_register['LO_TRESH'], b'\x00\x00')
#     while True:
#         if Next_channel == False:
#             Sel_channel += 1
#             if Sel_channel == Num_of_channels:
#                 Sel_channel = 0
#             i2c.writeto_mem(Device_list[0], Adc_register['CONF_REG'], bytes(Adc_channel[Sel_channel]))
#             result = ((Adc_fsr/32768)*int.from_bytes(Next_value,'big'))
#             print(result)
#             time.sleep(1)
#             Next_channel = True
#         else:
#             pass

