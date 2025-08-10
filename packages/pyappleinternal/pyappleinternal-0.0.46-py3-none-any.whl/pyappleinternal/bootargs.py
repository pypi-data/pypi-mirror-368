import json
import copy
import os,sys
class BootArgs():
    def __init__(self):
        super().__init__()
        path_value = os.environ.get('pyappleinternal_bootargs',None)
        self.bootargs_name=path_value if path_value else os.path.join(os.path.expanduser("~/.pyappleinternal"),"bootargs.json")
        self.bootargs={
            "Menu": "",
            "altoMobile": "altoMobile",
            "MagicalStarsign": "newLcdMura=MagicalStarsign",
            "DVI": "newLcdMura=iSD",
            "RGBW": "newLcdMura=RGBW",
            "ALSX": "newLcdMura=ALSX",
            "Wisteria": "astro=wisteria/rel",
            "OTA": "ota",
            "MMI": "MMI",
            "QRcode4": "qrcode=POv4",
            "QRcode3": "qrcode=POv3",
            "QRcode": "qrcode",
            "Burnin": "astro=factory/burnin"
        } 
    
    def save_bootargs(self,data):
        with open(self.bootargs_name, "w") as file:
            json.dump(data, file, indent=4)

    def load_bootargs(self):
        try:
            with open(self.bootargs_name,'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            os.makedirs(os.path.dirname(self.bootargs_name),exist_ok=True)
            self.save_bootargs(self.bootargs)
            return copy.deepcopy(self.bootargs)
    
    def generate_bootargs(self,add_part,bootargs,bootargs_list,mode="os"):
        if mode=="os":
            OS_command='diagstool bootargs'
            temp_bootargs=[]
            for i in bootargs_list:
                if add_part!=i:
                    OS_command+=f"""{f" --r {i.split('=')[0]}" if i!='' else ''}"""
            OS_command+=f"{f' --a {add_part}' if add_part!='' else ''}"
            return OS_command
        elif mode=="rec":
            temp=bootargs.split(" ")
            arr=list()
            for i in temp:
                k=i.split("=")[0]
                if k not in [j.split("=")[0] for j in bootargs_list]:
                    arr.append(i)
            arr.append(add_part)
            return f"setenv {' '.join(map(str, arr))}"
    
    def generate_ssh_bootargs(self,text):
        count=0
        temp=text.split(" ")
        for i in ['rdar102001044=yes','rdar102068389=yes','rdar102068001=yes']:
            if i not in temp:
                temp.append(i)
            else:count += 1
        return ' '.join(map(str, temp))


