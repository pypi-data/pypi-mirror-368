import os
from pyappleinternal.lockdown import create_using_usbmux
from pyappleinternal.services.crash_reports import CrashReportsManager
from pyappleinternal.services.diagnostics import DiagnosticsService
from pyappleinternal.SSHTransports import SSHTransports
from pyappleinternal.copyUnrestricted import copyUnrestricted
from pyappleinternal.authorized_key import authorized
import re
import subprocess
import textwrap
import time
import tempfile

class osdevice():
    def __init__(self,udid,taskid='debug',tcprelay_output_callback=None):
        super().__init__()
        self.udid=udid
        self.taskid=taskid
        self.tcprelay_output_callback=tcprelay_output_callback
        self.init()
    
    def init(self):
        self.ecid="" if "-" not in self.udid else self.udid.split("-")[1]
        self.mode="Non-UI"
        self.update_device_info()
        self.ssh_client=SSHTransports(self.udid,self.taskid)
        self.ssh_client.error_callback=self.tcprelay_output_callback
        self.ssh_client.tcprelay_on()
        self.get_bootargs=self.ssh_client.get_bootargs
        self.set_bootargs=self.ssh_client.set_bootargs
        self.command=self.ssh_client.command
        self.invoke_shell=self.ssh_client.invoke_shell
        self.invoke_read=self.ssh_client.invoke_read
        self.invoke_close=self.ssh_client.invoke_close
        self.invoke_stop=self.ssh_client.invoke_stop
        self.unlock_ssh=self.ssh_client.unlock_ssh
        self.appswitch=self.ssh_client.appswitch
        self.play=self.ssh_client.play
    
    def update_device_info(self):
        info=self.get_device_info()
        if info=={}: return
        if info.get("device_info",{})=={}:return
        if info.get("batt",{})=={}:return
        self.info=info
        self.mlbsn=self.info.get("device_info",{}).get("MLBSerialNumber","")
        self.sn=self.info.get("device_info",{}).get("SerialNumber",'') if self.info.get("device_info",{}).get("SerialNumber",'')!='' else self.mlbsn
        self.battery_level=self.info.get("batt",{}).get("CurrentCapacity","")
        self.hwmodel=self.info.get("device_info",{}).get("HardwareModel","")
        self.build_version=self.info.get("device_info",{}).get("BuildVersion","")
        self.os_version=self.info.get("device_info",{}).get("ProductVersion","")
        self.producttype = self.info.get("device_info", {}).get("ProductType", "")
        self.devicename = self.info.get("device_info", {}).get("DeviceName", self.producttype)
        self.internal=True if self.info.get("device_info",{}).get("ReleaseType","")=="NonUI" else False
        self.copyUnrestricted=copyUnrestricted(self.udid,self.internal)
    
    def poweroff(self):
        try:
            with create_using_usbmux(self.udid) as lockdown:
                ds = DiagnosticsService(lockdown)
                ds.shutdown()
            lockdown.close()
        except Exception as e:pass

    def enter_recovery(self):
        try:
            with create_using_usbmux(self.udid) as lockdown:
                lockdown.enter_recovery()
            lockdown.close()
        except Exception as e:pass

    def enter_diags(self):
        try:
            self.command("nvram boot-command='diags' ; nvram auto-boot='true' ; reboot")
        except Exception as e:print(e)

    def reboot(self):
        try:
            with create_using_usbmux(self.udid) as lockdown:
                ds = DiagnosticsService(lockdown)
                ds.restart()
            lockdown.close()
        except Exception as e:pass

    def sysdiagnose(self):
        try:
            with create_using_usbmux(self.udid) as lockdown:
                cr = CrashReportsManager(lockdown)
                cr.pull(f"{os.path.expanduser(f'~/Desktop/sysdiagnose_{lockdown.udid}')}", erase=True)
            lockdown.close()
        except Exception as e:pass

    def get_batt(self):
        try:
            with create_using_usbmux(self.udid) as lockdown:
                ds = DiagnosticsService(lockdown)
            lockdown.close()
            return ds.get_battery()
        except Exception as e:
            return {}
    
    def open_terminal(self):
        try:
            self.set_ssh_host()
            authorized(self.udid)
            applescript = f'''
                tell application "Terminal" 
                    do script "ssh {self.udid}.rsd"
                end tell
            '''
            subprocess.call(['osascript','-e',applescript])
        except Exception as e:print(e)
    
    def find_terminal(self):
        try:
            script = f'''
            tell application "Terminal"
                set found_window to false
                repeat with w in windows
                    if name of w contains "{self.udid}" then
                        set found_window to true
                        activate
                        return found_window 
                    end if
                end repeat
                return found_window 
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result.stdout.strip() == 'true'
            
        except Exception as e:
            print(f"Error finding terminal: {e}")
            return False
        
    def set_ssh_host(self):
        if os.path.exists(f'{os.path.expanduser("~")}/.ssh')!=True:
                os.makedirs(f'{os.path.expanduser("~")}/.ssh')
        host="ProxyCommand /usr/libexec/remotectl netcat -F %h com.apple.internal.ssh"
        otherhost="Include config.d/config_iosmenu"
        host_auth=textwrap.dedent("""
        Host *.rsd
            # This host entry is generated by remotectl setup-ssh
            ProxyCommand /usr/libexec/remotectl netcat -F %h com.apple.internal.ssh
            ProxyUseFdpass yes
            ServerAliveInterval 1
            ServerAliveCountMax 3
            StrictHostKeyChecking no
            UserKnownHostsFile /dev/null
            User root
            ControlPersist no""")
        case=re.compile(host,re.DOTALL)
        try:
            with open(f'{os.path.expanduser("~")}/.ssh/config', 'r+') as f:
                content=f.read()
                if otherhost in content:
                    subprocess.run(f"rm -rf $HOME/.ssh/config & echo '{host_auth}' >> $HOME/.ssh/config", shell=True)
                if case.search(content)==None:
                    f.write(host_auth)
        except:subprocess.run(f"echo '{host_auth}' >> $HOME/.ssh/config", shell=True)

    def command_terminal(self,command):
        for i in [1,2,3]:
            if self.find_terminal():
                self.command_terminal_fun(command)
                break
            else:
                self.open_terminal()
                time.sleep(1)

    def command_terminal_fun(self, command):
        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
                temp_file.write(command)
                temp_file_path = temp_file.name
                
            script = f"""
            set cmdFile to POSIX file "{temp_file_path}"
            set cmdContent to (read cmdFile)
            
            tell application "Terminal"
                set found_window to false
                repeat with w in windows
                    if name of w contains "{self.udid}" then
                        do script cmdContent in w
                        set found_window to true
                        activate
                        exit repeat
                    end if
                end repeat
                return found_window
            end tell
            """
            
            result = subprocess.run(['osascript', '-e', script], stdout=subprocess.PIPE)
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
            return 'true' in result.stdout.decode().strip().lower()
            
        except Exception as e:
            print(f"Error in command_terminal_fun: {e}")
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    print(f"Failed to delete temp file: {e}")
            return False

    def get_device_info(self):
        try:
            result_data = dict()
            with create_using_usbmux(self.udid) as lockdown:
                result_data['batt'] = self.get_batt()
                result_data['device_info'] = lockdown.all_values
            lockdown.close()
            return result_data
        except Exception as e:
            return {}
