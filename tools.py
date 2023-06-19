import os
import sys
import uuid
import subprocess
import psutil
import configparser
config = configparser.ConfigParser()

def insmod_ko(file):
    out_bytes = subprocess.check_output(['uname','-r']).decode('utf-8').replace("\n","")
    os.system("insmod /lib/modules/{}/kernel/drivers/usb/gadget/legacy/g_mass_storage.ko file={} stall=0 removable=1".format(out_bytes,file))
def rmmod():
    os.system("rmmod g_mass_storage")
def mount_fdisk(fdisk,path):
    os.system("mount {} {}".format(fdisk,path))
def umount_fdisk(fdisk):
    os.system("umount {}".format(fdisk))

def get_config(file):
    config.read(file)
    list = dict()
    for i in config.sections():
        s = dict()
        for j in config.items(i):
            s[j[0]] = j[1]
        list[i] = s
    return list

def get_mac():
    mac =  hex(uuid.getnode())[2:].zfill(12)
    return mac

def get_dirlist(path):
    if(not os.path.exists(path)):
        return {"code":-1,"Re":"本地文件夹不存在","data":'[]'}
    else:
        list = os.listdir(path)
        return {"code":0,"Re":"ok","data":str(list)}
    
def getinfo():
    disk = psutil.disk_usage("/dev/mmcblk0p4")
    cpu = psutil.cpu_count()
    ram = psutil.virtual_memory()
    l = {"CPU":cpu,"disk":disk,"ram":ram}
    r = {"code":0,"Re":"ok","data":str(l)}
    return r
