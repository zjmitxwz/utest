import os
import time
import threading
import tools
class TeskThread(threading.Thread):
    def __init__(self,client,tesk_queue,program_status,ftp):
        threading.Thread.__init__(self)
        self.client = client
        self.tesk_queue = tesk_queue
        self.program_status = program_status
        self.ftp = ftp
    def run(self):
        try:
            while(not self.tesk_queue.empty()):
                data = self.tesk_queue.get()
                print(data["tesk_name"]+"开始处理")
                tesk_name = data["tesk_name"]

                # 获取u盘的文件列表
                if(tesk_name == "getdirlist"):
                    li = tools.get_dirlist(os.path.join(self.program_status["data_path"],data["data"][0]))
                    if(li["code"]==0):
                        r = '{"tesk_name":'+tesk_name+',"code":'+str(li["code"])+',"rdata":'+li["data"]+',"Re":'+li["Re"]+'}'
                        self.push(self.program_status["config"]["theme"]["r_topic_ok"],r)
                    else:
                        r = '{"tesk_name":'+tesk_name+',"code":'+str(li["code"])+',"rdata":'+li["data"]+"}"
                        self.push(self.program_status["config"]["theme"]["r_topic_err"],r)


                # 下载ftp文件或文件夹到U盘
                elif(tesk_name=="download"):
                    for i in data["data"]:
                        if(os.path.split(i)[1]!=""):
                            c = self.ftp.download_file(i,self.program_status["data_path"])
                            if(c["code"]==0):
                                r = '{"tesk_name":'+tesk_name+',"code":'+str(c["code"])+',"Re":"'+c["Re"]+'"}'
                                self.push(self.program_status["config"]["theme"]["r_topic_ok"],r)
                            else:
                                r = '{"tesk_name":'+tesk_name+',"code":'+str(c["code"])+',"Re":"'+c["Re"]+'"}'
                                self.push(self.program_status["config"]["theme"]["r_topic_err"],r)
                        else:
                            c = self.ftp.download_free(i,self.program_status["data_path"])
                            if(c["code"]==0):
                                r = '{"tesk_name":'+tesk_name+',"code":'+str(c["code"])+',"Re":"'+c["Re"]+'"}'
                                self.push(self.program_status["config"]["theme"]["r_topic_err"],r)
                            else:
                                r = '{"tesk_name":'+tesk_name+',"code":'+str(c["code"])+',"Re":"'+c["Re"]+'"}'
                                self.push(self.program_status["config"]["theme"]["r_topic_err"],r)
                    self.reset()

                
                # 将U盘文件夹或文件上传到ftp
                elif(tesk_name=="upload"):
                    pass


                # 删除U盘文件
                elif(tesk_name=="delete"):
                    e = ["","/","/*"]
                    for i in data["data"]:
                        if(i not in e):
                            print(i)
                        else:
                            r = '{"tesk_name":'+tesk_name+',"code":-1'+',"Re":"不允许删除这个文件夹"}'
                            self.push(self.program_status["config"]["theme"]["r_topic_err"],r)



                # 任务传入错误异常
                else:
                    r = '{"tesk_name":'+tesk_name+',"code":-1,"Re":"任务错误"}'
                    self.push(self.program_status["config"]["theme"]["r_topic_err"],r)
            print(data["tesk_name"]+"处理结束")

        # 异常处理
        except Exception as e:
            r  = r = '{"tesk_name":'+'空'+',"code":-1,"Re":"处理线程异常"}'
            self.push(self.program_status["config"]["theme"]["r_topic_err"],r)
        finally:
            self.program_status["tesk_thread_status"] = 0

    # 文件操作完成的同步操作
    def reset(self):
            os.system("sync")
            tools.rmmod()
            tools.insmod_ko("/dev/mmcblk0p4")


    def push(self,theme,data):
        self.client.publish(theme,data)