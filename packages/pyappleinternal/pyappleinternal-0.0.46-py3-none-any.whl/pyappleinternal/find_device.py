import os
from pyappleinternal.usbmux import list_devices
from pyappleinternal.recovery_operate import list_recovery_devices
import platform
import time


if 'arm' in platform.machine().lower():
    import zeroconf._utils.ipaddress
    import zeroconf._handlers.answers

class find_device():
    def __init__(self):
        super().__init__()
        self.find_status=True

    def run(self,callback=None):
        while self.find_status:
            try:
                self.recovery_device=list_recovery_devices()
                self.os_device=list(set([device.serial for device in list_devices()]))
                if callback==None:
                    self.find_status=False
                    return self.os_device,self.recovery_device
                callback(self.os_device,self.recovery_device)
                time.sleep(1)
            except Exception as e:
                print(e)
                return {},{}

   
        


