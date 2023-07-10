import os
import queue
import sys
import logging
import tools
import shutil
import time
import logging.handlers
import socket
import json
import threading
import ftplib
from paho.mqtt import client as mqttclient

lock = threading.Lock()
# 创建一个任务队列
tesk_queue = queue.Queue()


#####################class#######################
class Log():
    def __init__(self,path):
        self.logger = logging.getLogger()
        self.fh = logging.handlers.TimedRotatingFileHandler(os.path.join(path,"log/run.log"),"D",1,7,'utf-8')
        self.formatter = logging.Formatter("%(asctime)s   %(levelname)s   %(message)s")
        self.fh.setFormatter(self.formatter)
        self.logger.addHandler(self.fh)
        self.logger.setLevel(logging.DEBUG)
    def log(self,level,n) -> None:
        if(level=="info"):
            self.logger.info(n)
        elif(level=="error"):
            self.logger.error(n)
        elif(level=="warning"):
            self.logger.warning(n)
        else:
            self.logger.critical(n)

class Myftp():
    def __init__(self,ip,port,user,pwd) -> None:
        self.ip = ip
        self.ftp = ftplib.FTP()
        self.ftp.encoding='utf-8'
        self.port = port
        self.user = user
        self.pwd = pwd
        self.status = -1
    def connect(self):
        try:
            self.ftp.connect(self.ip,self.port)
            self.ftp.login(self.user,self.pwd)
        except ConnectionRefusedError as e:
            return {"code":-1,"re":e.strerror}
        self.status = 0
        return {"code":0,"re":"服务器链接成功"}
    def if_c(self):
        if(self.status==-1):
            return {"code":-1,"re":"ftp服务器为链接"}
        try:
            self.ftp.nlst()
        except (ConnectionAbortedError,AttributeError) as e:
            self.status = -1
            return {"code":0,"re":e.strerror}

    def dow(self,list,save):
        ok = []
        err = []
        for i in list:
            if(os.path.splitext(i)[-1]!=""):
                t = self._dowfile(i,save)
                if(t["code"]==0):
                    ok.append(t)
                else:
                    err.append(t)
            else:
                t = self._dowfree(i,save)
                if(t["code"]==0):
                    ok.append(t)
                else:
                    err.append(t)
        return {"code":0,"ok":ok,"err":err}
    def _dowfile(self,file,save):
        ftp_p = os.path.split(file)[0]
        try:
            list = self.ftp.nlst(ftp_p)
        except ftplib.error_perm as e:
            print("服务器不存在这个路径")
            return {"code":-1,"re":"服务器不存在这个路径"}
        if file not in list:
            print("服务器不存在这个文件")
            return {"code":-1,"re":"服务器不存在这个文件"}
        path = Pgm_env.data_path
        for i in save.split("/"):
            path = os.path.join(path,i) 
        file_n = os.path.split(file)[-1]
        if(not os.path.exists(path)):
            os.makedirs(path)
        path = os.path.join(path,file_n)
        buffer_size = 102400
        with open(path,"wb+") as f:
            self.ftp.retrbinary("RETR {}".format(file),f.write,buffer_size)
            f.flush()
        print("文件:{}下载完毕".format(file_n))
        return {"code":0,"re":"文件:{}下载完毕".format(file_n),"filename":file_n}
    def _dowfree(self,free,save):
        try:
            list = self.ftp.nlst(free)
        except:
            print("服务器不存在这个目录{}".format(free))
            return {"code":-1,"re":"服务器不存在这个目录"}
        s = free.split("/")
        s.reverse()
        p = ""
        for i in s:
            p = i
            if(p!=""):
                break
        save_p = ""
        for i in save.split("/"):
            save_p = os.path.join(save_p,i)
        save_p = os.path.join(save_p,p)
        path = os.path.join(Pgm_env.data_path,save_p)
        if(not os.path.exists(path)):
            os.makedirs(path)
        for i in list:
            if(os.path.splitext(i)[-1]!=""):
                self._dowfile(i,save_p)
            else:
                self._dowfree(i,save_p)
        return {"code":0,"re":"目录下载完毕"}
    

    def up(self,list):
        ok = []
        err = []
        for i in list:
            if(os.path.splitext(i)[-1]!=""):
                t = self._upfile(i)
                if(t["code"]!=0):
                    err.append(t)
                else:
                    ok.append(t)
            else:
                t = self._upfree(i)
                if(t["code"]!=0):
                    err.append(t)
                else:
                    ok.append(t)
        return {"code":0,"re":"完成","ok":ok,"err":err}
    def _upfile(self,file):
        p = file.split("/")
        path = Pgm_env.data_path
        for i in p:
            path = os.path.join(path,i)
        if(not os.path.exists(path)):
            print("文件{}不存在".format(file))
            return {"code":-1,"re":"文件不存在","filename":"{}".format(os.path.split(file)[-1])}
        s = os.path.split(file)[0]
        s = s.split("/")
        f_p = "/"
        for i in s:
            f_p = os.path.join(f_p,i)
            try:
                self.ftp.cwd(f_p)
            except:
                self.ftp.mkd(f_p) 
        bufsiz=10240
        with open(path,"rb") as f:
            self.ftp.storbinary("STOR {}".format(os.path.join(f_p,os.path.split(file)[-1])),f,bufsiz)
        return {"code":0,"re":"文件上传成功"}
        
    def _upfree(self,free):
        p = free.split("/")
        path = Pgm_env.data_path
        for i in p:
            path = os.path.join(path,i)
        print(path)
        if(not os.path.exists(path)):
            print("U盘不存在这个目录")
            return {"code":-1,"re":"U盘不存在这个目录"}
        f_p = "/"
        for i in p:
            f_p = os.path.join(f_p,i)
            try:
                self.ftp.cwd(f_p)
            except:
                self.ftp.mkd(f_p)
            
        list = os.listdir(path)
        for i in list:
            if(os.path.splitext(i)[-1]!=""):
                self._upfile(os.path.join(free,i))
            else:
                self._upfree(os.path.join(free,i))
        return {"code":0,"re":"文件夹上传成功"}

    
class Pgm_env():
    data_path = "/root/code/data"
    data_disk = "/dev/mmcblk0p4"
    pgm_path = "/root/code"
    thread_status = 0
    log = None
    config = ""
class TeskThread(threading.Thread):
    def __init__(self,client,tesk_queue,ftp):
        threading.Thread.__init__(self)
        self.client = client
        self.tesk_queue = tesk_queue
        self.ftp = ftp
    def run(self):
        tools.umount(Pgm_env.data_disk)
        time.sleep(1)
        tools.mount(Pgm_env.data_disk,Pgm_env.data_path)
        try:
            while (not self.tesk_queue.empty()):
                data = self.tesk_queue.get()
                print("开始处理任务:{}".format(data))
                Pgm_env.log("info","开始处理{}".format(data))
                tesk = data["tesk"]
                if(tesk=="dow"):
                    save = "/"
                    if("save" in data.keys()):
                        save = data["save"]
                    t = self.ftp.dow(data["data"],save)
                    for i in t["ok"]:
                        i["id"] = data["id"]
                        mqtt_client.publish(Pgm_env.config["theme"]["r_topic_ok"],json.dumps(i),0)
                    for i in t["err"]:
                        i["id"] = data["id"]
                        mqtt_client.publish(Pgm_env.config["theme"]["r_topic_err"],json.dumps(i),0)
                    self.re_disk()
                if(tesk=="getlist"):
                    for i in data["data"]:
                        if(os.path.splitext(i)[-1]==""):
                            l = i.split("/")
                            path = Pgm_env.data_path
                            for i in l:
                                path = os.path.join(path,i)
                            if(not os.path.exists(path)):
                                print("不存在这个文件夹")
                                r = {"code":-1,"re":"不存在这个文件夹"}
                                mqtt_client.publish(Pgm_env.config["theme"]["r_topic_err"],json.dumps(r),0)
                                return
                            list = os.listdir(path)
                            r = {"code":0,"re":str(list)}
                            r["id"] = data["id"]
                            print(r)
                            mqtt_client.publish(Pgm_env.config["theme"]["r_topic_ok"],json.dumps(r),0)
                        else:
                            r = {"code":-1,"re":"不是一个文件夹"}
                            print("不是一个文件夹")
                            mqtt_client.publish(Pgm_env.config["theme"]["r_topic_err"],json.dumps(r),0)
                if(tesk=="info"):
                    pass
                if(tesk == "up"):
                    t = self.ftp.up(data["data"])
                    mqtt_client.publish(Pgm_env.config["theme"]["r_topic_ok"],json.dumps(t),0)
                if(tesk == "del"):
                    for i in data["data"]:
                        t = Pgm_env.data_path
                        for j in i.split("/"):
                            t = os.path.join(t,j)
                        if(not os.path.exists(t)):
                            print(t)
                            print("U盘不存在这个文件或者文件夹")
                            return 
                        if(os.path.splitext(i)[-1]==""):
                            if(os.path.samefile(t,Pgm_env.data_path)):
                                print(t)
                        else:
                            pass

                else:
                    print("不存在这个操作")
                Pgm_env.log("info","处理完毕{}".format(data))
                print("任务处理完毕:{}".format(data))
                
        except Exception as e:
            # pass
            print(e.args)
        finally:
            print("当前任务处理完毕")
            Pgm_env.thread_status = 0

    def re_disk(self):
        tools.log_move(os.path.join(Pgm_env.pgm_path,"log"),Pgm_env.data_path)
        tools.rmmod()
        tools.insmod(Pgm_env.data_disk)
####################class end####################
        
#####################func########################

# mqtt链接回调函数
def on_connect(client, userdata, flags, rc):
    if 0==rc:
        print("连接成功")
        Pgm_env.log("info","mqtt连接成功")
    elif 1==rc:
        print("连接失败-不正确的协议版本")
        Pgm_env.log("error","mqtt连接失败-不正确的协议版本")
    elif 2==rc:
        print("连接失败-无效的客户端标识符")
        Pgm_env.log("error","mqtt连接失败-无效的客户端标识符")
    elif 3==rc:
        print("连接失败-服务器不可用")
        Pgm_env.log("error","连接失败-服务器不可用")
    elif 4==rc:
        print("连接失败-错误的用户名或密码")
        Pgm_env.log("error","mqtt连接失败-错误的用户名或密码")
    elif 5==rc:
        print("连接失败-未授权")
        Pgm_env.log("error","mqtt连接失败-未授权")
    else:
        print("6-255: 未定义.")

def on_message(client, userdata, msg):
    tesk = msg.payload.decode('utf-8')
    try:
        Pgm_env.log("info","mqtt接受:{}".format(tesk))
        tesk = json.loads(tesk)
    except json.decoder.JSONDecodeError:
        Pgm_env.log("error","mqtt订阅主题传入参数异常")
        print("mqtt订阅主题传入参数异常")
        client.publish(Pgm_env.config["theme"]["r_topic_err"],"mqtt订阅主题传入参数异常",0)
        return
    tesk_queue.put(tesk)

    ftp_config = Pgm_env.config["ftp-server"]
    ftp = Myftp(ftp_config["host"],int(ftp_config["port"]),ftp_config["user"],ftp_config["pwd"])
    t = 0
    n = ftp.connect()
    while (n["code"]!=0 and t <10):
        t+=1
        time.sleep(1)
        n = ftp.connect()
        Pgm_env.log("error","ftp链接失败在尝试:{}次".format(str(t)))
        print("ftp链接失败在尝试:{}次".format(str(t)))
    t = 0
    if(n["code"]!=0):
        Pgm_env.log("error","ftp尝试链接失败建议重启设备并且查看配置文件")
        client.publish(Pgm_env.config["theme"]["r_topic_err"],"ftp尝试链接失败,建议重启并查看配置文件",0)
        return
    if(not Pgm_env.thread_status):
        thread = TeskThread(mqtt_client,tesk_queue,ftp)
        thread.start()
    Pgm_env.thread_status = 1


def on_disconnect(client, userdata, rc):
    if rc!=0:
        try:
            Pgm_env.log("error","mqtt已断开正在尝试重新链接")
        except socket.error:
            Pgm_env.log("error","mqtt重连失败")
    Pgm_env.log("info","mqtt重新链接成功")


def config_v(list):
    t1 = tools.get_config("./config/defconfig.ini")
    for i in t1.keys():
        if(i not in list):
            return False
        for j in t1[i].keys():
            if(j not in list[i]):
                return False
    return True

def subscribe(cli,theme):
    theme = theme.split(",")
    for i in theme:
        cli.subscribe(i,0)
        Pgm_env.log("info","订阅主题:{}".format(i))

if __name__ == "__main__":
    tools.umount(Pgm_env.data_disk)
    tools.mount(Pgm_env.data_disk,Pgm_env.data_path)

    mac = tools.get_mac()
    with open(os.path.join(Pgm_env.data_path,"mac.txt"),"w",encoding='utf-8') as f:
        f.writelines(mac)
    ip = tools.get_ip()
    with open(os.path.join(Pgm_env.data_path,"ip.txt"),"w",encoding='utf-8') as f:
        f.writelines(ip)

    tools.rmmod()
    tools.insmod(Pgm_env.data_disk)

    Pgm_env.log = Log(Pgm_env.pgm_path).log
    if(os.path.exists(os.path.join(Pgm_env.data_path,"config.ini"))):
        if(os.path.exists(os.path.join(Pgm_env.pgm_path,"config/config.ini"))):
            os.remove(os.path.join(Pgm_env.pgm_path,'config/config.ini'))
        shutil.move(os.path.join(Pgm_env.data_path,"config.ini"),os.path.join(Pgm_env.pgm_path,"config"))
        Pgm_env.log("info","设置IP--需要重启")
        s = tools.get_config(os.path.join(Pgm_env.pgm_path,"config/config.ini"))
        s = s["upan"]
        tools.set_ip(s)
        print(s)
        sys.exit(0)


    if(not os.path.exists(os.path.join(Pgm_env.pgm_path,"config/config.ini"))):
        Pgm_env.log("error","配置文件不存在,将默认配置文件写入U盘--修改完配置文件重启")
        shutil.copyfile(os.path.join(Pgm_env.pgm_path,"config/defconfig.ini"),os.path.join(Pgm_env.data_path,"config.ini"))
        tools.log_move(os.path.join(Pgm_env.pgm_path,"log"),Pgm_env.data_path)
        tools.rmmod()
        tools.insmod(Pgm_env.data_disk)
        sys.exit(-1)

    Pgm_env.config = tools.get_config(os.path.join(Pgm_env.pgm_path,"config/config.ini"))
    if(not config_v(Pgm_env.config)):
        Pgm_env.log("error","配置文件有误")
        tools.rmmod()
        tools.insmod(Pgm_env.data_disk)
        sys.exit(-1)



    mqtt_client = mqttclient.Client(tools.get_mac(),clean_session = False)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    Pgm_env.mqtt_client = mqtt_client
    mqtt_client.username_pw_set(Pgm_env.config["mqtt-server"]["user"],Pgm_env.config["mqtt-server"]["pwd"])
    mqtt_client.connect(Pgm_env.config["mqtt-server"]["host"],int(Pgm_env.config["mqtt-server"]["port"]),60)
    # mqtt_client.loop_start()
    subscribe(mqtt_client,Pgm_env.config["theme"]["w_topic"])
    mqtt_client.loop_forever()
    
