import os
import ftplib

class MyFtp():
    def __init__(self,host:str,port:int,user:str,pwd:str) -> None:
        self.HOST = host
        self.PORT = port
        self.USER = user
        self.PWD = pwd
        self.ftpc = self.get_ftpc()
    def get_ftpc(self):
        ftpc = ftplib.FTP()
        ftpc.encoding="utf-8"
        
        ftpc.connect(self.HOST,self.PORT)
        ftpc.login(self.USER,self.PWD)
        ftpc.voidcmd("TYPE I")
        return ftpc
    def close(self):
        # self.ftpc.quit()
        self.ftpc.close()

    def download_file(self,server_path,local_path):
        f = self.ftpc.nlst(os.path.split(server_path)[0])
        if(server_path not in f):
            return  {"code":-1,"Re":"服务器不存在这个文件"} 
        p = os.path.join(local_path,server_path)
        p1 = os.path.split(p)
        if(not os.path.exists(p1[0])):
            os.makedirs(p1[0])
        file = open(p,"wb")
        self.ftpc.retrbinary("RETR "+server_path,file.write)
        file.flush()
        file.close()
        os.system("sync")
        return {"code":0,"Re":"下载完毕"}
    def download_free(self,server_path,local_path):
        p0 = os.path.join(local_path,server_path)
        if(not os.path.exists(p0)):
            os.makedirs(p0)
        self.ftpc.cwd(server_path)
        for i in self.ftpc.nlst():
            path = os.path.join(i,local_path)
            if(i.find(".")!=-1):
                self.download_file(i,p0)
            else:
                self.download_free(i,p0)
        self.ftpc.cwd("..")
        return {"code":0,"Re":"下载完毕"}
    def upload_file(self,local_path,server_path):
        p0 = os.path.split(server_path)
        p1 = p0[0].split("/")
        s_p = ""
        for i in p1:
            s_p= s_p+i+"/"
            try:
                self.ftpc.cwd(s_p)
            except Exception as e:
                self.ftpc.mkd(s_p)
            finally:
                self.ftpc.cwd("/")
        if(os.path.exists(local_path)):
            file = open(local_path,"rb")
            self.ftpc.storbinary("STOR %s"%server_path,file)
        else:
            pass
            
    def upload_free(self,local_path,server_path):
        if(os.path.exists(local_path)):
            p1 = server_path.split("/")
            sp = ""
            for i in p1:
                sp=sp+i+"/"
                try:
                    self.ftpc.cwd(sp)
                except Exception as e:
                    print(e)
                    self.ftpc.mkd(sp)
                finally:
                    self.ftpc.cwd("/")
            for i in os.listdir(local_path):
                if(i.find(".")!=-1):
                    self.upload_file(os.path.join(local_path,i),os.path.join(server_path,i))
                else:
                    self.upload_free(os.path.join(local_path,i),os.path.join(server_path,i))
