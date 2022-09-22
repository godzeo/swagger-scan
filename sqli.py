#!/usr/bin/python
# -*- coding:utf-8 -*-
# wirter:En_dust
import platform
import sys

import requests
from loguru import logger

from lib.sqlmapServer import Client, startServer
import time
from threading import Thread

def sqlmapApiScan(targets):
    '''实例化Client对象时需要传递sqlmap api 服务端的ip、port、admin_token和HTTP包的绝对路径'''
    print("————————————————Start SQLMAP Working！—————————————————")
    target = 'http://testphp.vulnweb.com/listproducts.php?cat=2'
    task1 = Thread(target=set_start_get_result,args=(targets,))
    task1.start()



def time_deal(mytime):
     first_deal_time = time.localtime(mytime)
     second_deal_time = time.strftime("%Y-%m-%d %H:%M:%S", first_deal_time)
     return  second_deal_time


def set_start_get_result(targets):
    my_scan = Client("127.0.0.1", "8775", "c88927c30abb1ef6ea78cb81ac7ac6b0")

    for url_target in targets:

        url = url_target[4]+'/'+url_target[5]
        #/home/cheng/Desktop/sqldump/1.txt
        current_taskid =  my_scan.create_new_task()
        logger.debug("Get taskid: " + str(current_taskid))
        my_scan.set_task_options(url=url)

        logger.debug("Send Scan task :" + str(my_scan.start_target_scan(url=url,url_target=url_target),))
        print("Scan start time：" + str(time_deal(my_scan.scan_start_time)))
        while True:
            if my_scan.get_scan_status() == True:
                return_results = my_scan.get_result()
                if return_results == None:
                    print(url+"  No Vul")
                else:
                    print("当前数据库:" + str(return_results[-1]['value']))
                    print("当前数据库用户名:" + str(return_results[-2]['value']))
                    print("数据库版本:" + str(return_results[-3]['value']))
                    print( return_results[1]['value'][0]['data'] )

                    print("扫描结束时间：" + str(time_deal(my_scan.scan_end_time)))
                    print("扫描日志：\n" + str(my_scan.get_scan_log()))
                break


def sllmapApiScanMain(targets):
    # my_scan = Client("127.0.0.1", "8775", "5f8fa11b43595cb7edd53c1fa78607b1")
    sqlmapApiScan(targets)


if __name__ == '__main__':
    # startServer()
    my_scan = Client("127.0.0.1", "8775", "5f8fa11b43595cb7edd53c1fa78607b1")
    sqlmapApiScan("targets")




