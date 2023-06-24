import tools
import os
import sys
import random
import shutil
import json
import queue
from paho.mqtt import client as mqttclient
import TeskThread
import MyFtp
config = ""
tesk_queue = queue.Queue()



def on_message(client, userdata, msg):
    tesk = msg.payload.decode('gb2312')
    try:
        tesk = json.loads(tesk)
    except json.decoder.JSONDecodeError:
        mqtt_client.publish(config["theme"]["r_topic_err"], "mqtt订阅主题传入参数异常")
        print("mqtt订阅主题传入参数异常")
        return
    tesk_queue.put(tesk)
    if(not p_data["tesk_thread_status"]):
        ftp_config = config["ftp-server"]
        
        ftp = MyFtp.MyFtp(ftp_config["host"],int(ftp_config["port"]),ftp_config["user"],ftp_config["pwd"])
        thread = TeskThread.TeskThread(mqtt_client,tesk_queue,p_data,ftp)
        thread.start()
    p_data["tesk_thread_status"] = 1



def subscribe(theme):
    theme = theme.split(",")
    for i in theme:
        mqtt_client.subscribe(i,0)    
def  config_v(list):
    t1 = tools.get_config("config.ini")
    for i in t1.keys():
        if(i not in list):
            return False
        for j in t1[i].keys():
            if(j not in list[i]):
                return False
    return True
p_data = {"data_path":"/root/run/data","tesk_thread_status":0}
if(__name__ == "__main__"):
    # 读取配置文件
    config = tools.get_config(os.path.join(p_data["data_path"],"config.ini"))
    # 判断配置文件是否正常
    if(not config_v(config)):
        print("配置文件不正常将实例配置文件复制到U盘进行展示")
        shutil.copy("config.ini",p_data["data_path"])
        sys.exit(-1)
    p_data["config"] = config
    # 配置mqtt
    mqtt_client = mqttclient.Client(tools.get_mac())
    mqtt_client.on_message = on_message
    mqtt_client.username_pw_set(config["mqtt-server"]["user"],config["mqtt-server"]["pwd"])
    mqtt_client.connect(config["mqtt-server"]["host"],int(config["mqtt-server"]["port"]),5)
    mqtt_client.loop_start()
    subscribe(config["theme"]["w_topic"])
    while True:
        pass

    