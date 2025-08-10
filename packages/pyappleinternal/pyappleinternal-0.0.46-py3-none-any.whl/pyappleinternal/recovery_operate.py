import usb
import os
from pyappleinternal.irecv import IRecv
import pkg_resources
import platform
from pyappleinternal.bootargs import BootArgs 
from pyappleinternal.utils import get_libusb_path
if 'arm' in platform.machine().lower():
    import zeroconf._utils.ipaddress
    import zeroconf._handlers.answers

def list_recovery_devices():
    ecid_sn_dict = []
    try:
        libusb_path = get_libusb_path()
        try:
            backend = usb.backend.libusb1.get_backend(find_library=lambda x: libusb_path)
            devices = usb.core.find(find_all=True, backend=backend)
        except Exception as e:
            devices=[]
            print(e)
            

        def _populate_device_info(device):
            result=dict()
            for component in device.serial_number.split(' '):
                k, v = component.split(':')
                if k in ('SRNM', 'SRTG') and '[' in v:
                    v = v[1:-1]
                result[k] = v
            return result
        for device in devices:
            if device.iProduct == 3:
                info=_populate_device_info(device)
                if info.get("ECID","")!="" and info.get("ECID","") not in ecid_sn_dict:
                    ecid_sn_dict.append(info.get("ECID",""))
    except Exception as e:pass
    return ecid_sn_dict

class recdevice():
    def __init__(self,ecid):
        super().__init__()
        self.ecid=ecid
        self.mode="Rec"
        self.bootargs_menu=BootArgs()
        self.init()

    def init(self):
        try:
            rec_client=IRecv(ecid=self.ecid)
            self.sn=rec_client.serial_number if rec_client.serial_number!="" else self.ecid
        except:pass
    
    def unlock_ssh(self):
        bootargs=self.get_bootargs()
        if "Unable" not in bootargs:
            ssh_unlock_bootargs=self.bootargs_menu.generate_ssh_bootargs(bootargs)
            self.set_bootargs(ssh_unlock_bootargs)

    def appswitch(self,mode):
        bootargs=self.get_bootargs()
        bootargs_list=self.bootargs_menu.load_bootargs()
        if "Unable" not in bootargs:
            temp=bootargs.split(" ")
            arr=list()
            for i in temp:
                k=i.split("=")[0]
                if k not in [j.split("=")[0] for j in [*bootargs_list.values()]]:
                    arr.append(i)
            arr.append(bootargs_list[mode])
            return self.set_bootargs(' '.join(map(str, arr)))


    
    def enter_os(self):
        try:
            rec_client=IRecv(ecid=self.ecid)
            rec_client.set_autoboot(True)
            try:
                rec_client.send_command("setenv boot-command fsboot")
            except Exception as e:pass
            rec_client.reboot()
        except Exception as e:pass
    
    def reboot(self):
        try:
            rec_client=IRecv(ecid=self.ecid)
            rec_client.reboot()
        except Exception as e:pass

    def poweroff(self):
        try:
            rec_client=IRecv(ecid=self.ecid)
            rec_client.send_command("poweroff")
        except Exception as e:pass

    def enter_diags(self):
        try:
            rec_client=IRecv(ecid=self.ecid)
            rec_client.set_autoboot(True)
            try:
                rec_client.send_command("setenv boot-command diags")
            except Exception as e:pass
            rec_client.reboot()
        except Exception as e:pass
    
    def set_bootargs(self,text):
        try:
            rec_client=IRecv(ecid=self.ecid)
            rec_client.send_command(f"setenv boot-args {text}")
            rec_client.send_command(f"saveenv")
            return self.get_bootargs()
        except Exception as e:return "Unable to connect Device"

    def get_bootargs(self):
        try:
            rec_client=IRecv(ecid=self.ecid)
            bootargs=rec_client.getenv("boot-args")
            bootargs = "" if bootargs is None else bootargs.decode('utf-8').replace('\x00', '')
            return bootargs
        except Exception as e:return "Unable to connect Device"
