import spidev
import time
import RPi.GPIO as GPIO

'''
ADS7779 class based off spidev objects

Documentation: https://www.analog.com/media/en/technical-documentation/data-sheets/AD7779.pdf

'''

class AD777x:
    #Register map (9.6.3)
    registers = {
        "CHO_CONFIG"     : 0x00,
        "CH1_CONFIG"     : 0x01,
        "CH2_CONFIG"     : 0x02,
        "CH3_CONFIG"     : 0x03,
        "CH4_CONFIG"     : 0x04,
        "CH5_CONFIG"     : 0x05,
        "CH6_CONFIG"     : 0x06,
        "CH7_CONFIG"     : 0x07,
        "CH_DISABLE"     : 0x08,
        "CH0_SYNC_OFFSET": 0x09,
        "CH1_SYNC_OFFSET": 0x0A,
        "CH2_SYNC_OFFSET": 0x0B,
        "CH3_SYNC_OFFSET": 0x0C,
        "CH4_SYNC_OFFSET": 0x0D,
        "CH5_SYNC_OFFSET": 0x0E,
        "CH6_SYNC_OFFSET": 0x0F,
        "CH7_SYNC_OFFSET": 0x10,
        "GENERAL_USER_CONFIG_1": 0x11,
        "GENERAL_USER_CONFIG_2": 0x12,
        "GENERAL_USER_CONFIG_3": 0x13,
        "DOUT_FORMAT"    : 0x14,
        "ADC_MUX_CONFIG" : 0x15,
        "GLOBAL_MUX_CONFIG": 0x16,
        "GPIO_CONFIG"    : 0x17,
        "GPIO_DATA"      : 0x18,
        "BUFFER_CONFIG_1": 0x19,
        "BUFFER_CONFIG_2": 0x1A,
        "BUFFER_CONFIG_3": 0x1B,
        "CH0_OFFSET_UPPER_BYTE": 0x1C,
        "CH0_OFFSET_MID_BYTE"  : 0x1D,
        "CH0_OFFSET_LOWER_BYTE": 0x1E,
        "CH0_GAIN_UPPER_BYTE"  : 0x1F,
        "CH0_GAIN_MID_BYTE"    : 0x20,
        "CH0_GAIN_LOWER_BYTE"  : 0x21,
        "CH1_OFFSET_UPPER_BYTE": 0x22,
        "CH1_OFFSET_MID_BYTE"  : 0x23,
        "CH1_OFFSET_LOWER_BYTE": 0x24,
        "CH1_GAIN_UPPER_BYTE"  : 0x25,
        "CH1_GAIN_MID_BYTE"    : 0x26,
        "CH1_GAIN_LOWER_BYTE"  : 0x27,
        "CH2_OFFSET_UPPER_BYTE": 0x28,
        "CH2_OFFSET_MID_BYTE"  : 0x29,
        "CH2_OFFSET_LOWER_BYTE": 0x2A,
        "CH2_GAIN_UPPER_BYTE"  : 0x2B,
        "CH2_GAIN_MID_BYTE"    : 0x2C,
        "CH2_GAIN_LOWER_BYTE"  : 0x2D,
        "CH3_OFFSET_UPPER_BYTE": 0x2E,
        "CH3_OFFSET_MID_BYTE"  : 0x2F,
        "CH3_OFFSET_LOWER_BYTE": 0x30,
        "CH3_GAIN_UPPER_BYTE"  : 0x31,
        "CH3_GAIN_MID_BYTE"    : 0x32,
        "CH3_GAIN_LOWER_BYTE"  : 0x33,
        "CH4_OFFSET_UPPER_BYTE": 0x34,
        "CH4_OFFSET_MID_BYTE"  : 0x35,
        "CH4_OFFSET_LOWER_BYTE": 0x36,
        "CH4_GAIN_UPPER_BYTE"  : 0x37,
        "CH4_GAIN_MID_BYTE"    : 0x38,
        "CH4_GAIN_LOWER_BYTE"  : 0x39,
        "CH5_OFFSET_UPPER_BYTE": 0x3A,
        "CH5_OFFSET_MID_BYTE"  : 0x3B,
        "CH5_OFFSET_LOWER_BYTE": 0x3C,
        "CH5_GAIN_UPPER_BYTE"  : 0x3D,
        "CH5_GAIN_MID_BYTE"    : 0x3E,
        "CH5_GAIN_LOWER_BYTE"  : 0x3F,
        "CH6_OFFSET_UPPER_BYTE": 0x40,
        "CH6_OFFSET_MID_BYTE"  : 0x41,
        "CH6_OFFSET_LOWER_BYTE": 0x42,
        "CH6_GAIN_UPPER_BYTE"  : 0x43,
        "CH6_GAIN_MID_BYTE"    : 0x44,
        "CH6_GAIN_LOWER_BYTE"  : 0x45,
        "CH7_OFFSET_UPPER_BYTE": 0x46,
        "CH7_OFFSET_MID_BYTE"  : 0x47,
        "CH7_OFFSET_LOWER_BYTE": 0x48,
        "CH7_GAIN_UPPER_BYTE"  : 0x49,
        "CH7_GAIN_MID_BYTE"    : 0x4A,
        "CH7_GAIN_LOWER_BYTE"    : 0x4B,
        "CH0_ERR_REG"  : 0x4C,
        "CH1_ERR_REG"  : 0x4D,
        "CH2_ERR_REG"  : 0x4E,
        "CH3_ERR_REG"  : 0x4F,
        "CH4_ERR_REG"  : 0x50,
        "CH5_ERR_REG"  : 0x51,
        "CH6_ERR_REG"  : 0x52,
        "CH7_ERR_REG"  : 0x53,
        "CH0_1_SAT_ERR": 0x54,
        "CH2_3_SAT_ERR": 0x55,
        "CH4_5_SAT_ERR": 0x56,
        "CH6_7_SAT_ERR": 0x57,
        "CHX_ERR_REG_EN": 0x58,
        "GEN_ERR_REG_1": 0x59,
        "GEN_ERR_REG_1_EN": 0x5A,
        "GEN_ERR_REG_2": 0x5B,
        "GEN_ERR_REG_2_EN": 0x5C,
        "STATUS_REG_1": 0x5D,
        "STATUS_REG_2": 0x5E,
        "STATUS_REG_3": 0x5F,
        "SRC_N_MSB"   : 0x60,
        "SRC_N_LSB"   : 0x61,
        "SRC_IF_MSB"  : 0x62,
        "SRC_IF_LSB"  : 0x63,
        "SRC_UPDATE"  : 0x64        
    }
    
     #basic initialization
    def __init__(self, bus, device, start, reset, drdy):
        #Store pins
        self.startp=start
        self.resetp=reset
        self.drdyp=drdy
        
        GPIO.setmode(GPIO.BCM)
        self.spi = spidev.SpiDev()
        self.spi.open(bus,device)
        
        GPIO.setup(start, GPIO.OUT)
        GPIO.setup(reset, GPIO.OUT)
        GPIO.setup(drdy, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        GPIO.output(reset,1) #Reset_bar
        GPIO.output(start,1) #Start_bar
        
        
        #creating SPI device
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)

        #set parameters for SpiDev object
        self.spi.max_speed_hz = 1*1000000
        self.spi.mode = 0
        self.spi.bits_per_word = 8
        
        self.reset()

    
    #Close instance of ADC
    def close(self):
        self.reset()
        self.spi.close() #disconnects from the SPI device
        GPIO.cleanup()
            
    def __del__(self):
        self.close() #calls object's own close method
        
    def reset(self):
        GPIO.output(self.resetp,0) #Reset_bar
        time.sleep(0.01)
        GPIO.output(self.resetp,1)
        time.sleep(0.01)
        self.read_register("GEN_ERR_REG_2")

    def twos_comp(self,val,bits):
        ret=val
        if(val & (1<<(bits-1))) != 0:
            ret = val - (1<<bits)
        return ret
    
    #read a configuration register
    def read_register(self,reg):       
        if type(reg) is str:
            reg=self.registers[reg]
        
        if reg<0 or reg>0x64:
            raise ValueError("Invalid register identifier")

        to_send=[(0b1<<7)|reg,0]

        result = self.spi.xfer2(to_send)

        return result[1]
        
    #Write to a configuration register
    def write_register(self,reg,val):
        if type(reg) is str:
            reg=self.registers[reg]
        
        to_send=[reg]+[val]
        self.spi.xfer2(to_send)
        
    def initiate_data_capture(self):
        temp=self.read_register("GENERAL_USER_CONFIG_3")
        self.write_register("GENERAL_USER_CONFIG_3",temp | (0b1<<4))
        GPIO.output(self.startp,0)
        time.sleep(0.001)
        GPIO.output(self.startp,1)
        
    def stop_data_capture(self):
        #temp=self.read_register("GENERAL_USER_CONFIG_3")
        #self.write_register("GENERAL_USER_CONFIG_3",~(~temp & ~(0b1<<4)))
        self.write_register("GENERAL_USER_CONFIG_3",0b10000000)

        
#     def read_data(self):
#         #Send back a dictionary of lists,
#         #each channel has a list containing two items, the header and the data
#         result={}
#         if GPIO.input(self.drdyp):
#             raise ValueError
#         for i in range(0,7):
#             temp=self.spi.xfer2([0x80,0x00,0x00,0x00])
#             header=temp[0]
#             data=temp[1]<<16+temp[2]<<8+temp[3]
#             data=self.twos_comp(data,24)
#             channel=(header>>4)&(0b111)
#             result[channel]=[header,data]
#         return result

    def read_data(self): #Hopefully faster implementation
        #Send back a dictionary of lists,
        #each channel has a list containing two items, the header and the data
        result={}
        if GPIO.input(self.drdyp):
            raise RuntimeError("Attempted to read data from ADC when not ready")
        read=self.spi.xfer2([0x80,0x00,0x00,0x00]*8)
        #print(read)
        # for i in range(0,8):
        #     temp=read[0+4*i:4+4*i]
        #     header=temp[0]
        #     data=(temp[1]<<16)+(temp[2]<<8)+temp[3]
        #     data=self.twos_comp(data,24)
        #     channel=(header>>4)&(0b111)
        #     result[channel]=[header,data]
        return bytearray(read)

    def set_gain(self,channel,gain):
        if gain not in [1,2,4,8]:
            raise ValueError("Invalid PGA gain requested")
        if channel<0 or channel>8:
            raise ValueError("Invaled PGA channel referenced")
        
        gain_bits=0
        if gain==1:
            gain_bits=0b00
        elif gain==2:
            gain_bits=0b01
        elif gain==4:
            gain_bits=0b10
        elif gain==8:
            gain_bits=0b11
        
        reg_base=0
        reg=reg_base+channel
        
        self.write_register(reg,gain_bits<<6)
        
    def set_decimation_rate(self,rate):
        self.write_register("SRC_UPDATE",0)
                       
        N=int(rate)
        IF=int((rate-N)*(2**16))
        
        if N<0 or N>2**16:
            raise ValueError("Invalid decimation N")
        if IF<0 or IF>2**16:
            raise ValueError("Invalid decimation IF")
        
        self.write_register("SRC_N_MSB",N>>8)
        self.write_register("SRC_N_LSB",N & 0xFF)
        self.write_register("SRC_IF_MSB",IF>>8)
        self.write_register("SRC_IF_LSB",IF & 0xFF)
        
        self.write_register("SRC_UPDATE",1)
        time.sleep(0.001)
        self.write_register("SRC_UPDATE",0)
    
    def get_status(self):
        reg_1=self.read_register("STATUS_REG_1")
        reg_2=self.read_register("STATUS_REG_2")
        reg_3=self.read_register("STATUS_REG_3")
        return (reg_1, reg_2, reg_3)

    def get_formatted_status(self):
        error_dict={}
        error_dict["STATUS_REG_1"]=self.read_register("STATUS_REG_1")
        error_dict["STATUS_REG_2"]=self.read_register("STATUS_REG_2")
        error_dict["STATUS_REG_3"]=self.read_register("STATUS_REG_3")
        
        temp=error_dict["STATUS_REG_1"]
        if temp&(0b1<<4):
            error_dict["CH4_ERR_REG"]=self.read_register("CH4_ERR_REG")
        if temp&(0b1<<3):
            error_dict["CH3_ERR_REG"]=self.read_register("CH3_ERR_REG")
        if temp&(0b1<<2):
            error_dict["CH2_ERR_REG"]=self.read_register("CH2_ERR_REG")
        if temp&(0b1<<1):
            error_dict["CH1_ERR_REG"]=self.read_register("CH1_ERR_REG")
        if temp&(0b0<<1):
            error_dict["CH0_ERR_REG"]=self.read_register("CH0_ERR_REG")

        temp=error_dict["STATUS_REG_2"]
        if temp&(0b1<<4):
            error_dict["GEN_ERR_REG_2"]=self.read_register("GEN_ERR_REG_2")
        if temp&(0b1<<3):
            error_dict["GEN_ERR_REG_1"]=self.read_register("GEN_ERR_REG_1")
        if temp&(0b1<<2):
            error_dict["CH7_ERR_REG"]=self.read_register("CH7_ERR_REG")
        if temp&(0b1<<1):
            error_dict["CH6_ERR_REG"]=self.read_register("CH6_ERR_REG")
        if temp&(0b0<<1):
            error_dict["CH5_ERR_REG"]=self.read_register("CH5_ERR_REG")
            
        temp=error_dict["STATUS_REG_3"]
        if temp&(0b1<<3):
            error_dict["ERR_LOC_SAT_CH6_7"]=self.read_register("CH6_7_SAT_ERR")
        if temp&(0b1<<2):
            error_dict["ERR_LOC_SAT_CH4_5"]=self.read_register("CH4_5_SAT_ERR")
        if temp&(0b1<<1):
            error_dict["ERR_LOC_SAT_CH2_3"]=self.read_register("CH2_3_SAT_ERR")
        if temp&(0b0<<1):
            error_dict["ERR_LOC_SAT_CH0_1"]=self.read_register("CH0_1_SAT_ERR")
        return error_dict


if __name__ == "__main__":
    my_adc=AD777x(1,0,2,3,22) #bus,device,start,reset,drdy
    my_adc.set_decimation_rate(4000.0)
        
    my_adc.write_register("GENERAL_USER_CONFIG_1",0b01110100) 
    my_adc.write_register("GENERAL_USER_CONFIG_2",0b00000001) #Do we need SPI sync? seems like bit 0 should be 1
    my_adc.write_register("DOUT_FORMAT",0x00)
    time.sleep(0.1)
    print(my_adc.get_status()) #Expect 0,0,16
    #my_adc.initiate_data_capture()
