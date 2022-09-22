#!/usr/bin/python
import logging
import os

import requests
import json
import time

from loguru import logger
import os, subprocess


def startServer():
    # start = input('请输入sqlmap的路径：')
    try:
        # os.chdir(start)
        os.system('python3 lib/sqlmap/sqlmapapi.py -s -H 0.0.0.0 -p 8775')


    except:
        print('异常退出')
    return 1

class Client():
    def __init__(self,server_ip,server_port,admin_token="",taskid="",filepath=None):
        self.server = "http://" + server_ip + ":" + server_port
        self.admin_token = admin_token
        self.taskid = taskid
        self.filepath = ""
        self.status = ""
        self.scan_start_time = ""
        self.scan_end_time = ""
        self.engineid=""
        self.headers = {'Content-Type': 'application/json'}


    def create_new_task(self):
        '''创建一个新的任务，创建成功返回taskid'''
        r = requests.get("%s/task/new"%(self.server))
        self.taskid = r.json()['taskid']
        if self.taskid != "":
            return self.taskid
        else:
            print("创建任务失败!")
            return None

    def set_task_options(self,url):
        '''设置任务扫描的url等'''
        self.filepath = url



    def start_target_scan(self,url,url_target):
        '''开始扫描的方法,成功开启扫描返回True，开始扫描失败返回False'''


        if url_target[3] == "get":
            get_options ={
                'url':url,
                'getCurrentUser':True,
                'getBanner':True,
                'batch': True
            }
        else:
            get_options = {
                'url': url,
                'data': json.loads(url_target[5]),
                'getCurrentUser': True,
                'getBanner': True,
                'batch': True
            }
        headers = {
            'Content-Type': 'application/json'
        }

        r = requests.post(self.server + '/scan/' + self.taskid + '/start',
                      data=json.dumps(get_options),
                      headers=self.headers)
        if r.json()['success']:
            self.scan_start_time = time.time()
            print(r.json())
            #print(r.json()['engineid'])
            return r.json()['engineid']
        else:
            logger.debug(r.json())
            return None

    def get_scan_status(self):
        '''获取扫描状态的方法,扫描完成返回True，正在扫描返回False'''
        self.status = json.loads(requests.get(self.server + '/scan/' + self.taskid + '/status').text)['status']
        if self.status == 'terminated':
            self.scan_end_time = time.time()
            #print("扫描完成!")
            return True
        elif self.status == 'running':
            #print("Running")
            return False
        else:
            #print("未知错误！")
            self.status = False



    def get_result(self):
        '''获取扫描结果的方法，存在SQL注入返回payload和注入类型等，不存在SQL注入返回空'''
        if(self.status):
            r = requests.get(self.server + '/scan/' + self.taskid + '/data')
            if (r.json()['data']):
                return r.json()['data']
            else:
                return None

    def get_all_task_list(self):
        '''获取所有任务列表'''
        r = requests.get(self.server + '/admin/' + self.admin_token + "/list")
        if r.json()['success']:
            #print(r.json()['tasks'])
            return r.json()['tasks']
        else:
            return None

    def del_a_task(self,taskid):
        '''删除一个任务'''
        r = requests.get(self.server + '/task/' + taskid + '/delete')
        if r.json()['success']:
            return True
        else:
            return False

    def stop_a_scan(self,taskid):
        '''停止一个扫描任务'''
        r = requests.get(self.server + '/scan/' + taskid + '/stop')
        if r.json()['success']:
            return True
        else:
            return False

    def flush_all_tasks(self):
        '''清空所有任务'''
        r =requests.get(self.server + '/admin/' + self.admin_token + "/flush")
        if r.json()['success']:
            return True
        else:
            return False

    def get_scan_log(self):
        '''获取log'''
        r = requests.get(self.server + '/scan/' + self.taskid + '/log')
        return r.json()

