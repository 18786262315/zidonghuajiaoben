#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
"""数据库备份"""
 

import os,time,sched,re,smtplib,subprocess
# import time
# import sched
# import re
# import smtplib
# import subprocess
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
 
# 第一个参数确定任务的时间，返回从某个特定的时间到现在经历的秒数
# 第二个参数以某种人为的方式衡量时间
schedule = sched.scheduler(time.time, time.sleep)
new_filename = ''


def rmove_file(i_time):
    work_dir = '.\\' # 遍历备份文件夹
    for parent, dirnames, filenames in os.walk(work_dir,  followlinks=True):
        for filename in filenames:
            file_path = os.path.join(parent, filename)
            t = os.path.getctime(file_path) #获取文件创建时间戳
            # print('文件名：%s' % filename)
            # print('文件完整路径：%s' % file_path)
            # print(get_FileCreateTime(file_path))
            if re.match("(.*?)\\w.sql",filename) and i_time-t >432000:
                '''当文件时间大于指定时间后(432000=5天)，删除文件'''
                # print(i_time-t)
                # print('文件名', filename)
                os.remove(file_path)

def backupsDB():
    """备份数据"""
    global new_filename

    new_filename = time.strftime("%y-%m-%d-%H-%M-%S", time.localtime())+".sql"
    i_time =time.time()
    # 如果是linux改下路径就可以了
    cmdString = 'mysqldump -u root --password=ycc962464 ---all-databases > %s'%new_filename #备份语句
    #执行备份语句并获取返回值；
    ret2 = subprocess.check_output(cmdString, shell=True)
    # out_error_list = ret2.communicate(cmdString)
    print (ret2)
    sendMail(0)



def sendMail(nber,e=""):
    """邮件发送"""
    _user = "843092012@qq.com"#发送者的邮箱
    _pwd = "xumeagqowzcgbfji"#发送者的密码
    _to = "843092012@qq.com"#接收者的邮箱
 
    # 如名字所示Multipart就是分多个部分
    msg = MIMEMultipart()
    msg["Subject"] = "数据库数据备份"
    msg["From"] = _user
    msg["To"] = _to
    if nber == 0 :
        # ---这是文字部分---
        part = MIMEText("名家景选数据库备份")
        msg.attach(part)
        print(new_filename)
        # ---这是附件部分---
        # 类型附件
        part = MIMEApplication(open(new_filename, 'rb').read())
        part.add_header('Content-Disposition','attachment',filename=new_filename)
        msg.attach(part)
    else:
        #---错误信息---
        # print(e)
        part = MIMEText("数据库备份失败！！错误："+str(e))
        msg.attach(part)



    s = smtplib.SMTP("smtp.qq.com", timeout=25)  # 连接smtp邮件服务器,端口默认是25,qq邮箱
    s.login(_user, _pwd)  # 登陆服务器
    s.sendmail(_user, _to, msg.as_string())  # 发送邮件
    s.close()
 
 
def perform_command(cmd, inc):
    # 安排inc秒后再次运行自己，即周期运行
    #防止报错后停止运行

    schedule.enter(inc, 0, perform_command, (cmd, inc))
    os.system(cmd)
    backupsDB()

def timming_exe(cmd, inc=60):
    # enter用来安排某事件的发生时间，从现在起第n秒开始启动
    schedule.enter(inc, 0, perform_command, (cmd, inc))
    # 持续运行，直到计划时间队列变成空为止
    schedule.run()
 
if __name__ == '__main__':
    # print("show time after 10 seconds:")
    timming_exe("echo %time%", 10);#每间隔43200秒备份发送邮件，43200 是12个小时
    