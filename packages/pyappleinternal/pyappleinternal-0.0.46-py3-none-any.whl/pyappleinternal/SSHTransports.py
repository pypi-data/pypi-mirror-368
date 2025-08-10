import paramiko
import os
from scp import SCPClient
import stat
import time
from PIL import Image
import re
from tqdm import tqdm
from pyappleinternal.bootargs import BootArgs
from pyappleinternal.copyUnrestricted import copyUnrestricted
from pyappleinternal.authorized_key import authorized
from pyappleinternal.tcp_forwarder import UsbmuxTcpForwarder
from pyappleinternal.tcprelay import tcprelay
# import logging

# logging.basicConfig(level=logging.DEBUG)

import threading
import sys
import uuid
from pyappleinternal.assign_ports import PortManager
from functools import partial
from pathlib import Path
import select



class SSHTransports():
    def __init__(self, udid, taskid="debug"):
        super().__init__()
        self.udid = udid
        self.host = "localhost"
        self.username = "root"
        self.client_on = None
        self.taskid=taskid
        self.error_callback = None
        self.invoke_shell_on = None
        self.taskid_info={}
        self.port=None
        self.invoke_read_status=False
        self.usb_port_forward=None
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.copyUnrestricted = copyUnrestricted(self.udid)
        self.PortManager=PortManager()
        self.BootArgs = BootArgs()
    
    def thread_it(self,fun,args=()):
        command = threading.Thread(target=fun,args=(*args,))
        if sys.version_info >= (3, 10):
            command.daemon = True
        else:
            command.setDaemon(True)
        command.start()
        return  command

    def is_connect(self):
        return self.client.get_transport() is not None and self.client.get_transport().is_active()

    def connect(self):
        if not self.is_connect():
            authorized(self.udid)
            # sock = paramiko.ProxyCommand(f"/usr/libexec/remotectl netcat {self.udid} com.apple.internal.ssh")
            self.tcprelay_on()
            self.client.connect(hostname=self.host, username=self.username,port=self.port,
                                key_filename=f'{os.path.expanduser("~")}/.ssh/id_ed25519', timeout=2)
            if self.invoke_shell_on!=None:
                self.invoke_close()
    
    def tcprelay_on(self):
        if self.usb_port_forward == None:
            self.port=self.PortManager.allocate_port(self.taskid,self.udid)
            self.usb_port_forward = tcprelay(self.udid)
            self.thread_it(self.usb_port_forward.start,args=("0.0.0.0",self.taskid,self.udid,self.port,self.error_callback))      

    def command(self, command, timeout=5, callback=None,raise_error=False):
        try:
            self.connect()
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
            if callback is None:
                output = stdout.read().decode('utf-8').strip()
                outerr = stderr.read().decode('utf-8').strip()
                return output + outerr
            result_data = ""
            buffers = {'stdout': '', 'stderr': ''}
            def process_data(channel, stream_type):
                nonlocal result_data
                while True:
                    if stream_type == 'stdout' and channel.recv_ready():
                        data = channel.recv(1024)
                        if data:
                            buffers[stream_type] += data.decode('utf-8')
                    elif stream_type == 'stderr' and channel.recv_stderr_ready():
                        data = channel.recv_stderr(1024)
                        if data:
                            buffers[stream_type] += data.decode('utf-8')

                    lines = buffers[stream_type].split('\n')
                    if len(lines) > 1:
                        for line in lines[:-1]:
                            callback(self.udid,line)
                            result_data += line + '\n'
                        buffers[stream_type] = lines[-1]
                    else:
                        break

            while not stdout.channel.closed or stdout.channel.recv_ready() or stdout.channel.recv_stderr_ready():
                process_data(stdout.channel, 'stdout')
                process_data(stdout.channel, 'stderr')

            for stream in buffers.values():
                if stream:
                    callback(self.udid,stream)
                    result_data += stream

            return result_data.strip()
        except Exception as e:
            if callback:
                return self.udid,False
            if raise_error:
                raise "send command error " +str(e)
            return False

    def invoke_shell(self, command):
        try:
            self.connect()
            if self.invoke_shell_on is None:
                self.invoke_shell_on = self.client.invoke_shell()
            self.invoke_shell_on.send(command + "\n")
            return True

        except Exception as e:
            print(f"Error in invoke_shell: {e}")
            self.invoke_shell_on=None
            self.invoke_read_status=False
            return False
    def invoke_stop(self):
        self.connect()
        if self.invoke_shell_on is None:return False
        self.invoke_shell_on.send('\x03')
            
    
    def invoke_read(self,callback=print):
        if self.invoke_shell_on is None:return False
        self.invoke_read_status=True
        buffer=""
        try:
            while self.invoke_read_status:
                rlist, _, _ = select.select([self.invoke_shell_on], [], [])
                if not rlist:
                    break

                data = self.invoke_shell_on.recv(1024).decode('utf-8', errors='ignore')
                if not data:
                    break

                buffer += data
                lines = buffer.split('\n')
                buffer = lines.pop()

                for line in lines:
                    callback(self.udid,line.strip())
        except Exception as e:
            print("invoke read error ",e)
            self.invoke_read_status=False
            callback(self.udid,"invoke chanel disconnected")

    def invoke_close(self):
        try:
            if self.invoke_shell_on is not None:
                self.invoke_shell_on.close()
                self.invoke_shell_on = None
                self.invoke_read_status=False
        except Exception as e:
            print(f"Error in close invoke_shell: {e}")

    def cam_shell(self, command):
        try:
            self.connect()
            self.client_on = self.client.invoke_shell()
            self.client_on.send("mkdir /tmp/take_photo &>/dev/null \n")
            self.client_on.send("cd /tmp/take_photo\n")
            self.client_on.send("OSDToolbox display -s 1 &\n")
            self.client_on.send("killall h16isp\n")
            self.client_on.send("h16isp -j\n")
            self.client_on.send("forget\n")
            self.client_on.send("on\n")
            self.client_on.send("v\n")
            self.client_on.send(command)
        except Exception as e:
            print("open cam error ",e)

    def tele_on(self):
        self.cam_mode = 1
        self.cam_shell("start 1 139 0 \n")

    def swide_on(self):
        self.cam_mode = 4
        self.cam_shell("start 4 139 0 \n")

    def default_on(self):
        self.cam_mode = 0
        self.cam_shell("start 0 255 0 \n")

    def focus(self):
        if self.client_on != None:
            self.client_on.send(f"f {self.cam_mode}\n")

    def exit_cam(self):
        if self.client_on != None:
            self.client_on.close()
            self.client_on = None

    def save_image(self):
        try:
            if self.client_on != None:
                self.client_on.send(f"\n")
                self.client_on.recv(2048)
                self.client_on.send(f"p 1\n")
                time.sleep(1)
                output = self.client_on.recv(2048).decode('utf-8')
                match = re.search(r'(?i)\./\S+\.(jpg|png|jpeg|tiff|bmp|heif|heic|raw)', output)
                if match:
                    filename = os.path.basename(match.group(0))
                    timestamp = int(time.time())
                    self.download(f'/tmp/take_photo/{filename}', os.path.expanduser(f"~/Desktop/photo_{timestamp}.jpg"))
                else:
                    self.screenshot(True)
        except Exception as e:
            print("save image error ",e)

    def upload(self, local_path, remote_path, callback=None,taskid=None):
        try:
            taskid = taskid if taskid else str(uuid.uuid4())
            self.connect()
            scp = SCPClient(self.client.get_transport(),
                            progress=lambda filename, size, sent: self.progress(filename, size, sent, local_path,
                                                                                callback,taskid,"Upload"))  # 添加进度回调
            scp.put(local_path, remote_path, recursive=True)
            scp.close()
            return  True,taskid
        except Exception as e:
            print("upload error ",e)
            return  False,taskid

    def download(self, remote_path, local_path, callback=None,taskid=None):
        try:
            taskid = taskid if taskid else str(uuid.uuid4())
            self.connect()
            scp = SCPClient(self.client.get_transport(),
                            progress=lambda filename, size, sent: self.progress(filename, size, sent, remote_path,
                                                                                callback,taskid,"Download"))  # 添加进度回调
            scp.get(remote_path, local_path, recursive=True)
            scp.close()
            return  True,taskid
        except Exception as e:
            print("download error ",e)
            return  False,taskid

    def delete(self, *remote_path):
        status=True
        sftp=None
        try:
            self.connect()
            sftp = self.client.open_sftp()
            dir_list=[]
            for path in remote_path:
                if self.is_directory(sftp,path):
                    dir_list.append(path)
                else:sftp.remove(path)
            remote_list = " ".join([f"'{i}'" for i in dir_list])
            self.command(f"rm -rf {remote_list}",raise_error=True)
        except Exception as e:
            print("delete error ",e)
            status=  False
        finally:
            if sftp!=None:sftp.close()
            return status

    def rename(self, original_path, target_path):
        status = True
        sftp=None
        try:
            self.connect()
            sftp = self.client.open_sftp()
            sftp.rename(original_path, target_path)
        except Exception as e:
            print("rename error ",e)
            status = False
        finally:
            if sftp!=None:sftp.close()
            return status

    def exists(self,path):
        try:
            self.connect()
            sftp = self.client.open_sftp()
            sftp.stat(path)
            return  True
        except:
            return False

    def movefile(self, target_path, *paths):
        status = True
        sftp=None
        try:
            self.connect()
            sftp = self.client.open_sftp()
            for path in paths:
                newname=os.path.join(target_path,os.path.basename(os.path.normpath(path)))
                if self.exists(newname):
                    self.delete(newname)
                sftp.rename(path, newname)
        except Exception as e:
            print("movefile error ",e)
            status = False
        finally:
            if sftp!=None:sftp.close()
            return status
    def start_server(self,servername,command,op_type="script"):
        self.connect()
        self.stop_server(servername)
        if op_type=="script":
            self.upload(command,"/var/root")
            program_arguments=[f"/var/root/{os.path.basename(os.path.normpath(command))}"]
        elif op_type=="command":
            program_arguments = ["/bin/bash","-c",command]
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>Label</key>
            <string>com.darker.{servername}</string>
            <key>ProgramArguments</key>
            <array>
                {''.join(f'<string>{arg}</string>' for arg in program_arguments)}
            </array>
            <key>RunAtLoad</key>
            <true/>
            <key>KeepAlive</key>
            <true/>
            <key>EnablePressuredExit</key>
            <false/>
            <key>EnableTransactions</key>
            <true/>
        </dict>
        </plist>
        '''
        plist_path = f"/Library/LaunchDaemons/com.darker.{servername}.plist"
        ssh_command = f'''
        bash -c 'cat > {plist_path} <<EOF
        {plist_content}
        EOF'
        chown root:wheel {plist_path}
        chmod 644 {plist_path}
        launchctl load {plist_path}
        '''
        self.command(ssh_command)

    def stop_server(self,servername):
        self.connect()
        self.command(f"launchctl unload /Library/LaunchDaemons/com.darker.{servername}.plist")

    def mkdir(self, remote_path):
        status = True
        sftp=None
        try:
            self.connect()
            sftp = self.client.open_sftp()
            sftp.mkdir(remote_path)
        except Exception as e:
            print("mkdir error ",e)
            status = False
        finally:
            if sftp!=None:sftp.close()
            return status

    def list_files_with_stat(self, remote_path):
        file_reslut = {}
        file_reslut[remote_path] = {}
        sftp=None
        try:
            self.connect()
            sftp = self.client.open_sftp()
            files = sftp.listdir_attr(remote_path)
            for file in files:
                real_filetype=None
                filename = file.filename
                if stat.S_ISDIR(file.st_mode):
                    filetype = "Directory"
                elif stat.S_ISLNK(file.st_mode):
                    filetype = "Symlink"
                else:
                    filetype = "File"
                filepath = os.path.join(remote_path, filename)
                if filetype == "Symlink":
                    real_path = self.get_real_link(filepath)
                    filepath = "/" + "/".join(part for part in real_path.split("/") if part and not part.startswith(".."))
                    if self.is_directory(sftp,filepath):
                        real_filetype="Directory"
                    else:real_filetype="File"
                size = self.convert_size(file.st_size)
                file_extension = filename.split(".")[-1].lower() if "." in filename else ""
                file_reslut[remote_path][filename] = {
                    "file_path": filepath,
                    "file_type": filetype,
                    "file_size": size,
                    "file_extension": file_extension,
                    "file_real_type":real_filetype
                }
        except Exception as e:
            print("list dir error ",e)
            file_reslut = None
        finally:
            if sftp!=None:sftp.close()
            return file_reslut

    def is_directory(self, sftp, remote_path):
        try:
            return stat.S_ISDIR(sftp.stat(remote_path).st_mode)
        except IOError:
            return False

    def convert_size(self, size):
        if size < 1000:
            return f"{size} B"
        elif size < 1000 * 1000:
            return f"{size / 1000:.2f} KB"
        elif size < 1000 * 1000 * 1000:
            return f"{size / (1000 * 1000):.2f} MB"
        else:
            return f"{size / (1000 * 1000 * 1000):.2f} GB"

    def get_real_link(self, link_path):
        target_path = None
        sftp=None
        try:
            self.connect()
            sftp = self.client.open_sftp()
            target_path = sftp.readlink(link_path)
        except Exception as e:
            print("get path real link error ",e)
        finally:
            if sftp!=None:sftp.close()
            return target_path

    def compress_progress(self,taskid,filename,callback,udid,text):
        pattern = r'\d+/\d+'
        matches = re.findall(pattern, text)
        if matches:
            percentage_arr=matches[0].split("/")
            count=int(percentage_arr[0])
            total=int(percentage_arr[1])
            self.progress( filename, total, count, filename, callback=callback,taskid=taskid,op_type="Compress")

    def find_file(self, remote_path, filename):
        sftp = None
        file_result = []
        try:
            self.connect()
            sftp = self.client.open_sftp()
            files = sftp.listdir_attr(remote_path)
            for file_attr in files:
                filename_match = filename.lower() in file_attr.filename.lower()
                try:
                    rep= re.findall(filename, file_attr.filename, re.IGNORECASE)
                except Exception as e:
                    rep= []
                if filename_match or rep:
                    file_result.append(f"{remote_path}/{file_attr.filename}")
        except Exception as e:
            print("find file error ", e)
        finally:
            if sftp is not None:
                sftp.close()
            return file_result



    def compress(self, enter_path, save_name,callback, *remote_name):
        try:
            taskid = str(uuid.uuid4())
            if len(str(remote_name))>(120*1024*1024):return False,taskid
            compress_callback = partial(self.compress_progress, taskid,f"{save_name}.tar",callback)
            remote_list = " ".join([f"./'{i}'" for i in remote_name])
            self.command(f"""
                cd {enter_path}
                total_files=$(find {remote_list} -type f | wc -l)
                count=0
                find {remote_list} -type f | while IFS= read -r file; do
                    tar -rf '{save_name}'.tar -- "$file"
                    ((count++))
                    printf "%d/%d\n" "$count" "$total_files"
                done
            """, timeout=None,callback=compress_callback)
            return True,taskid
        except Exception as e:
            print("comress error ",e)
            return False,taskid

    def decompress(self, remote_path):
        try:
            base_name = Path(remote_path).stem
            self.command(f"cd '{os.path.dirname(remote_path)}';mkdir '{base_name}';bsdtar -xf '{remote_path}' -C ./'{base_name}'")
            return True
        except Exception as e:
            print("decompress error ",e)
            return False

    def get_bootargs(self):
        try:
            result = self.command("diagstool bootargs --print",raise_error=True).replace("boot-args=", '')
            return result
        except:
            return "Unable to connect Device"

    def set_bootargs(self, text):
        try:
            self.command(f'OSDToolbox display -s 1 &>/dev/null & nvram boot-args="{text}";OSDToolbox appswitch -b',raise_error=True)
            return self.get_bootargs()
        except:
            return "Unable to connect Device"

    def screenshot(self, cut=False):
        try:
            timestamp = int(time.time())
            png_path = f"/tmp/screenshot_{timestamp}.png"
            self.command(f"/usr/local/bin/CADebug -c '{png_path}'",raise_error=True)
            local_path = os.path.expanduser(f"~/Desktop/screenshot_{timestamp}.png")
            self.download(png_path, local_path)
            if cut == True:
                image = Image.open(local_path)
                width, height = image.size
                new_height = height * 0.642
                crop_box = (0, (height - new_height) // 2, width, (height + new_height) // 2) 
                cropped_image = image.crop(crop_box)
                cropped_image.save(local_path)
        except Exception as e:
            print("screenshot error " ,e)

    def showimage(self, path,internal=False):
        try:
            if internal:
                self.appswitch(None,"newLcdMura=MagicalStarsign")
                self.command("diagstool lcdmura --start-test StarsignTest",raise_error=True)
                self.command(f"diagstool lcdmura --imagepath '{path}'",raise_error=True)
            else:
                name = os.path.basename(path)
                self.mkdir("/tmp/player/")
                self.upload(path, "/tmp/player/")
                self.appswitch(None,"newLcdMura=MagicalStarsign")
                self.command("OSDToolbox appswitch -b",raise_error=True)
                self.command("diagstool lcdmura --start-test StarsignTest",raise_error=True)
                self.command(f"diagstool lcdmura --imagepath '/tmp/player/{name}'",raise_error=True)
            return True
        except Exception as e:
            print("showimage error ",e)
            return False
            

    def play(self, path,volume):
        try:
            name = os.path.basename(path)
            self.command("mkdir /tmp/player",raise_error=True)
            self.upload(path, "/tmp/player/")
            self.command(f"figplayAV -volume {volume} '/tmp/player/{name}' &",raise_error=True)
        except Exception as e:
            print("play sound error ", e)
    
    def unlock_ssh(self):
        try:
            self.command(f"OSDToolbox display -s 1 & diagstool bootargs --a rdar102068001=yes --a rdar102068389=yes --a rdar102001044=yes ; reboot",raise_error=True)
            return "Unable to connect(Wait device reboot)"
        except:
            return False
        
    def appswitch(self,mode,add=None):
        try:
            OS_command='diagstool bootargs'
            temp_bootargs=[]
            bootargs_config=self.BootArgs.load_bootargs()
            for i in bootargs_config:
                if i!=mode and bootargs_config[i]!=add:
                    OS_command+=f"{f' --r {bootargs_config[i]}' if bootargs_config[i]!='' else ''}"
                else:
                    temp_bootargs.append(i)
            for i in temp_bootargs:
                OS_command+=f"{f' --a {bootargs_config[i]}' if bootargs_config[i]!='' else ''}"
            if add:OS_command+=f" -a {add}"
            self.command(f"OSDToolbox display -s 1 &>/dev/null & {OS_command};OSDToolbox appswitch -b",raise_error=True)
            return self.get_bootargs() 
        except:return "Unable to connect"
        

    def progress(self, filename, size, sent, remote_path, callback=None,taskid=None,op_type=None):
        if isinstance(filename, (bytes, bytearray)):
            filename = filename.decode("utf-8")
        percent = (sent / size) * 100
        get_percent=self.taskid_info.get(taskid,0)
        if callable(callback):
            if percent-get_percent>=1 or get_percent-percent>=1:
                self.taskid_info[taskid] = int(percent)
                callback(self.udid, remote_path, filename, percent,taskid,op_type)
        # else:
        #     bar = tqdm(
        #         total=size,
        #         ncols=100,
        #         bar_format=f"{filename} " + "{bar}| {percentage:3.0f}%"
        #     )
        #     bar.update(sent - bar.n) 