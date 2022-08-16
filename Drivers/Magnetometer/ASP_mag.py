import sys
import time
import RPi.GPIO as GPIO
from AD777x import AD777x
import datetime

sys.path.append("../../ASP/Helpers")

from constants import MAG_DATA_HEADER_STRUCT

class ASP_mag():

    adc=None
    SRp=26
    data_counter=-1
    polarity=0
    capture = False
    warm_up_delay = 10
    data_save_samples = 5000
    data_save_counter = data_save_samples
    filename = None
    mag_p_bias = 14
    start_time = None

    #Functions for reading data
    B_gain=0.0364/1000 #uT per lsb
    T_gain=74.5/1E6 #Degrees kelvin per lsb
    
    myData=bytearray() #List of timestamps and data dictionaries
    
    #Todo, the functions have no control over these gPIO, why?
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SRp, GPIO.OUT)
    GPIO.setup(mag_p_bias, GPIO.OUT)
    GPIO.output(SRp,0)
    GPIO.output(mag_p_bias, 0)
    

    
    def configure_adc(self):
        #Set gain levels
        self.adc.set_gain(0,4)
        self.adc.set_gain(1,4)
        self.adc.set_gain(2,4)
        self.adc.set_gain(3,2)
        
        self.adc.set_gain(4,4)
        self.adc.set_gain(5,4)
        self.adc.set_gain(6,4)
        self.adc.set_gain(7,2)
        
        self.adc.set_decimation_rate(4000.00)
        
        self.adc.write_register("GENERAL_USER_CONFIG_1",0b01110100) 
        self.adc.write_register("GENERAL_USER_CONFIG_2",0b00000001) #No SPI Sync
        self.adc.write_register("DOUT_FORMAT",0x00)
        self.adc.write_register("ADC_MUX_CONFIG",0b01001100) #Power supply reference
        time.sleep(0.01)
        #Defualt for other values
        time.sleep(0.1) #Needs 0.1 seconds to get status cleared
        self.adc.get_status() #Clear out status info
        
    def __init__(self, sample_count=22):
        self.adc = AD777x(1,0,2,3,22) #bus,device,start,reset,drdy
        self.configure_adc()
        self.switch_samples = sample_count # data points between switch events
        self.switch_counter = self.switch_samples

        

    #Close instance of ADC
    def close(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.output(self.mag_p_bias, 1)
        self.adc.close()
            
    def __del__(self):
        self.close() #calls object's own close method
    
    # Human readable version of data collection
    # def get_data(self,save=True):
    #     data=self.adc.read_data()
    #     if len(data) != 8:
    #         raise ValueError
    #     B0={}
    #     B1={}
        
    #     B0["x"]=data[0][1]*self.B_gain*self.polarity
    #     B0["y"]=data[1][1]*self.B_gain*self.polarity
    #     B0["z"]=data[2][1]*self.B_gain*self.polarity
    #     B0["T"]=data[3][1]*self.T_gain
        
    #     B1["x"]=data[4][1]*self.B_gain*self.polarity
    #     B1["y"]=data[5][1]*self.B_gain*self.polarity
    #     B1["z"]=data[6][1]*self.B_gain*self.polarity
    #     B1["T"]=data[7][1]*self.T_gain
        
    #     if save:
    #         self.myData.append([time.time(), self.polarity, B0,B1])

    def get_data(self,save=True):
        data=self.adc.read_data()
        if save:
            # combined_data = []
            # for i in range(0, 8):
            #     combined_data[i] = (data[i][0] << 24) + data[i][1]
            # data_struct = MAG_DATA_STRUCT.pack(time.time(), self.polarity, *combined_data)
            data_arr = bytearray(MAG_DATA_HEADER_STRUCT.pack(time.time(), self.polarity))
            data_arr += data
            self.myData += data_arr
    
    def interrupt_handler(self, drdy):
        # Save data
        self.get_data(save=True)
        
        # track samples
        if self.switch_counter>0:
            self.switch_counter-=1
        else: # polarity switch
            pinVal = 1
            if self.polarity > 0:
                pinVal = 0
            GPIO.output(self.SRp,pinVal)
            self.polarity *= -1
            self.switch_counter=self.switch_samples
        
        self.data_save_counter -= 1
        if self.data_save_counter <= 0:
            self.save_data_to_file()

    
    def save_data_to_file(self):
        data = self.myData
        self.myData = bytearray()
        if len(data) == 0:
            #print("No data!")
            raise RuntimeError('NoMagData')

        #Write the results to disk
        myfile=open(self.filename,'wb')
        myfile.write(data)
        myfile.close()
        self.data_save_counter = self.data_save_samples
        self.filename = "%s/%s" % (self.dir, datetime.datetime.now().strftime(self.time_pattern))

        
    def begin_sampling(self, dir='/home/pi/magnetometer', time_pattern="%H%M%S", timeout=10, callback=None,args=None):
        self.capture = True
        GPIO.output(self.SRp,0)
        time.sleep(0.001)
        GPIO.output(self.SRp,1)
        self.polarity=1
        
        self.time_pattern = time_pattern
        self.dir = dir
        self.filename = "%s/%s" % (dir, datetime.datetime.now().strftime(time_pattern))
        
        #Setup counters
        self.data_counter=self.data_samples
        
        self.adc.initiate_data_capture()
        time.sleep(self.warm_up_delay)

        #Timer for the length of the data capture
        self.start_time=time.time()

        #Setup interrupt
        GPIO.add_event_detect(self.adc.drdyp, GPIO.FALLING, callback=self.interrupt_handler)
        
        while(time.time()<(self.start_time+timeout) and self.capture): #Wait the data-take time
            time.sleep(0.01)

        if self.data_save_counter < self.data_save_samples:
            self.save_data_to_file()
        
        if callback != None and self.capture: # execute callback on completion (but not commanded stop)
            callback(*args)
        #Shut-off the interrupt
        self.end_sampling()
        return
        

    def end_sampling(self):
        if self.capture:
            GPIO.remove_event_detect(self.adc.drdyp)
            self.capture = False
        capture_time = 0
        if self.start_time:
            capture_time = int(time.time() - self.start_time)
        return capture_time

if __name__=="__main__":
    import threading
    mymag=ASP_mag()
    dir="./"
    time_pattern="%Y%m%d%H%M%S.%f"
    timeout=20
    callback=None
    args=()
    capture_thread = threading.Thread(target=mymag.begin_sampling, args=(dir, time_pattern, timeout, callback,args))
    capture_thread.start()
    print("mag started")
    time.sleep(15)
    print("mag about to end")
    mymag.end_sampling()
    print("mag ended")
