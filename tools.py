import os
import uuid
import subprocess
import configparser
import socket
import shutil
config = configparser.ConfigParser()

def rmmod():
    os.system("sync")
    os.system("rmmod g_mass_storage")
    os.system("sync")

def insmod(fdisk):
    os.system("sync")
    out_bytes = subprocess.check_output(['uname','-r']).decode('utf-8').replace("\n","")
    os.system("insmod /lib/modules/{}/kernel/drivers/usb/gadget/legacy/g_mass_storage.ko file={} stall=0 removable=1".format(out_bytes,fdisk))
    os.system("sync")
def get_mac():
    mac_address = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()
    mac_address = '-'.join([mac_address[i:i+2] for i in range(0, 11, 2)])
    return mac_address

def umount(disk):
    os.system("sync")
    os.system("umount {}".format(disk))
    os.system("sync")


def mount(disk,path):
    os.system("sync")
    os.system("mount {} {}".format(disk,path))
    os.system("sync")

def get_config(file):
    config.read(file)
    list = dict()
    for i in config.sections():
        s = dict()
        for j in config.items(i):
            s[j[0]] = j[1]
        list[i] = s
    return list

def set_ip(d):
    print(d)
    if(d["ip"])=="0.0.0.0":
        text = "auto eth0\niface eth0 inet dhcp\n"
        with open("/etc/network/interfaces.d/usereth0","w",encoding="utf-8") as f:
            f.writelines(text)
    else:
        text = "auto eth0\niface eth0 inet static\naddress {}\nnetmask {}\ngateway {}\nbroadcast {}\n".format(d["ip"],d["subnetmask"],d["interway"],d["broadcast"])
        with open("/etc/network/interfaces.d/usereth0","w",encoding="utf-8") as f:
            f.writelines(text)



def get_ip():
    ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def log_move(src,dst):
    os.sync()
    for i in os.listdir(src):
        path = os.path.join(src,i)
        shutil.copy(path,dst)
    os.sync()