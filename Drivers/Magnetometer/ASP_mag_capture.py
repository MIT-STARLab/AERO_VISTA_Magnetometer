from ASP_mag import ASP_mag
import threading

class ASPMagCapture:

    settings = {
      "decimation_rate": 4000.00,
      "switch_samples": 50,
      "pga_gain": 4,
      "warm_up_delay": 10,
    }

    mag = None

    def __init__(self):
      self.mag = ASP_mag()
      self.apply_settings()
    
    def __del__(self):
        self.stop_magnetometer()

    # begins magnetometer capture
    def start_magnetometer(self, dir="./", time_pattern="%Y%m%d%H%M%S.%f", timeout=500,callback=None, args=()):
        capture_thread = threading.Thread(target=self.mag.begin_sampling, args=(dir, time_pattern, timeout, callback,args))
        capture_thread.start()
        return capture_thread

    # ends magnetometer capture
    def stop_magnetometer(self):
        return self.mag.end_sampling()
    
    # changes settings to match new setting values and applies them to magnetometers
    def change_settings(self, new_settings):
        for key in new_settings.keys():
            if key in self.settings.keys():
                self.settings[key] = new_settings[key]
        self.apply_settings()
    
    # applies current settings to magnetometers
    def apply_settings(self):
        self.mag.data_samples = self.settings["switch_samples"]
        self.mag.warm_up_delay = self.settings["warm_up_delay"]
        self.set_gain(self.settings["pga_gain"])
        self.set_sample_rate(self.settings["decimation_rate"])

    # sets pga gain for both magnetometers
    def set_gain(self, gain):
        self.mag.adc.set_gain(0,gain)
        self.mag.adc.set_gain(1,gain)
        self.mag.adc.set_gain(2,gain)
        
        self.mag.adc.set_gain(4,gain)
        self.mag.adc.set_gain(5,gain)
        self.mag.adc.set_gain(6,gain)
    
    def set_sample_rate(self, decimation_rate):
        self.mag.adc.set_decimation_rate(decimation_rate)
        
    
    #Command implementation
    def update_magnetometer_settings(self,myparams):
        new_settings = {
            "decimation_rate": myparams["decimation_rate"].value,
            "switch_samples": myparams["switch_samples"].value,
            "pga_gain": myparams["pga_gain"].value,
            "warm_up_delay": myparams["warm_up_delay"].value,
        }
        self.change_settings(new_settings)
    

    





