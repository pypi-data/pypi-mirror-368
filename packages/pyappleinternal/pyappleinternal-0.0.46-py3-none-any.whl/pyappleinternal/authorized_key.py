import os
import subprocess
from pathlib import Path
import sys
from  pyappleinternal.copyUnrestricted import copyUnrestricted


authorized_path=Path(os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), ".ssh")))
def make_authorized_key():
    try:
        if os.path.exists(f'{os.path.expanduser("~")}/.ssh')!=True:
            os.makedirs(f'{os.path.expanduser("~")}/.ssh')
        authorized_path.mkdir(exist_ok=True,parents=True)
        subprocess.run("test -f ~/.ssh/id_ed25519.pub || ssh-keygen -t ed25519 -N '' -f ~/.ssh/id_ed25519 &>/dev/null",stderr=subprocess.DEVNULL, shell=True)
        authorized_keys=subprocess.check_output(["cat ~/.ssh/id_ed25519.pub"], shell=True,stderr=subprocess.DEVNULL)
        subprocess.run(f"echo {authorized_keys.decode().strip()}> '{os.path.join(authorized_path,'authorized_keys')}'", shell=True)
    except Exception as e:print(e)

def authorized(udid):
    try:
        make_authorized_key()
        copyfile=copyUnrestricted(udid)
        copyfile.authorized_keys(authorized_path)
    except Exception as e:print(e)