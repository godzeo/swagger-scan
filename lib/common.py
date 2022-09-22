# -*- encoding: utf-8 -*-
import re
import sys
import requests
import json
import time
import codecs
import subprocess
import threading
import copy
import os
import platform

import urllib
from socketserver import ThreadingMixIn
from http.server import SimpleHTTPRequestHandler, HTTPServer

from loguru import logger

logger.remove()
handler_id = logger.add(sys.stderr, level="DEBUG")  # 设置输出级别

requests.packages.urllib3.disable_warnings()
api_set_list = []  # ALL API SET
scheme = 'http'  # default value
headers = {'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
auth_bypass_detected = False

current_path = os.getcwd()
log_path = current_path + "/out/req"

proxies = {
    "http": "http://127.0.0.1:9999",
    "https": "https://127.0.0.1:9999",
}


def get_chrome_path_win():
    pass


def get_chrome_path_linux():
    return "lib/chromedriver_linux64"


def get_chrome_path_mac():
    return "lib/chromedriver_mac64"


def get_chrome_path():
    if platform.system() == 'Darwin':
        return get_chrome_path_mac()
    elif platform.system() == 'Windows':
        return get_chrome_path_win()
    else:
        return get_chrome_path_linux()


def print_msg(msg):
    if msg.startswith('[GET] ') or msg.startswith('[POST] '):
        # print('\n') 写文件
        1
    logger.success(msg)
    # _msg = '[%s] %s' % (time.strftime('%H:%M:%S', time.localtime()), msg)
    # # print(_msg)
    # print(_msg )


def find_all_api_set(start_url):
    try:
        text = requests.get(start_url, headers=headers, verify=False).text
        if text.strip().startswith('{"swagger":"'):  # from swagger.json
            api_set_list.append(start_url)
            print_msg('[OK] [API set] %s' % start_url)
            with codecs.open('api-docs.json', 'w', encoding='utf-8') as f:
                f.write(text)
        elif text.find('"swaggerVersion"') > 0:  # from /swagger-resources/
            base_url = start_url[:start_url.find('/swagger-resources')]
            json_doc = json.loads(text)
            for item in json_doc:
                url = base_url + item['location']
                find_all_api_set(url)
        else:
            print_msg('[FAIL] Invalid API Doc: %s' % start_url)
    except Exception as e:
        print_msg('[find_all_api_set] process error %s' % e)


def process_doc(url, global_ress):
    base_url = urllib.parse.urlparse(url)
    base_url = base_url.scheme + "://" + base_url.netloc

    try:
        json_doc = requests.get(url, headers=headers, verify=False).json()

        if "basePath" in json_doc.keys():
            if 'http' not in json_doc['basePath']:
                base_url += json_doc['basePath']
            else:
                base_url = json_doc['basePath']  # eg:/santaba/rest
        elif "servers" in json_doc.keys():
            base_url = json_doc["servers"][0]['url']
        else:
            base_url = base_url.rstrip('/')

        paths = json_doc['paths']
        path_num = len(paths)
        logger.info("[+] {} has {} paths".format(url, len(paths)))

        #     遍历路径
        for path in json_doc['paths']:

            if "description" in json_doc['info'].keys():
                # v2
                summary = json_doc['info']['description']
            elif "title" in json_doc['info'].keys():
                # v1
                summary = json_doc['info']['title']
            else:
                summary = 'None'

            for method in json_doc['paths'][path]:
                if method.upper() not in ['GET', 'POST', 'PUT']:
                    continue

                params_str = ''
                sensitive_words = ['url', 'path', 'uri']
                sensitive_params = []

                if 'parameters' in json_doc['paths'][path][method]:
                    parameters = json_doc['paths'][path][method]['parameters']

                    for parameter in parameters:
                        para_name = parameter['name']
                        # mark sensitive parma
                        for word in sensitive_words:
                            if para_name.lower().find(word) >= 0:
                                sensitive_params.append(para_name)
                                break

                        if 'format' in parameter:
                            para_format = parameter['format']
                        elif 'schema' in parameter and 'format' in parameter['schema']:
                            if 'default' in parameter['schema'].keys():
                                para_format = parameter['schema']['default']
                            else:
                                para_format = parameter['schema']['format']
                        elif 'schema' in parameter and 'type' in parameter['schema']:
                            if 'default' in parameter['schema'].keys():
                                para_format = parameter['schema']['default']
                            else:
                                para_format = parameter['schema']['type']
                        elif 'schema' in parameter and '$ref' in parameter['schema']:
                            para_format = parameter['schema']['$ref']
                            para_format = para_format.replace('#/definitions/', '')
                            para_format = 'OBJECT_%s' % para_format
                        else:
                            para_format = parameter['type'] if 'type' in parameter else 'unkonwn'
                            if 'default' in parameter:
                                para_format = parameter['default']

                        if 'is_required' in parameter.keys():
                            is_required = '' if parameter['required'] else '*'
                        else:
                            is_required = ''

                        if 'default' in parameter:
                            params_str += '&%s=%s' % (para_name, para_format,)
                        else:
                            if para_format == 'string':
                                params_str += '&%s=%s%s%s' % (para_name, is_required, para_format, is_required)
                            else:
                                params_str += '&%s=%s' % (para_name, para_format)
                    params_str = params_str.strip('&')
                    if sensitive_params:
                        logger.success('[*] Possible vulnerable param found: %s, path is %s' % (
                            sensitive_params, base_url + path))

                scan_api(method, summary, base_url, path, params_str, global_ress)

    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.debug()
        print_msg('[process_doc error][%s] %s' % (url, e))


def scan_api(method, summary, base_url, path, params_str, global_ress, error_code=None):
    # place holder
    _params_str = params_str.replace('*string*', 'a')
    _params_str = _params_str.replace('*int64*', '1')
    _params_str = _params_str.replace('*int32*', '1')
    _params_str = _params_str.replace('int64', '1')
    _params_str = _params_str.replace('int32', '1')
    _params_str = _params_str.replace('=string', '=test')
    _params_str = _params_str.replace('=integer', '=1')

    url_formats = re.findall('{(.*?)}', path, flags=0)
    for ss in url_formats:
        path = path.replace('{' + ss + '}', 'test')

    api_url = base_url + path

    if not error_code:
        print_msg('[%s] %s %s' % (method.upper(), api_url, _params_str))
    if method.upper() == 'GET':
        # try:
        # r = requests.get(api_url + '?' + _params_str, proxies=proxies, headers=headers, verify=False)
        r = requests.get(api_url + '?' + _params_str, headers=headers, verify=False)
        # except:
        #     startxray_cmd = current_path + "/lib/xray/xray_darwin_amd64 webscan -u {} --html-output {}/xray_err_log{}.html".format(
        #         api_url + '?' + _params_str, log_path, str(time.time()))
        #     subprocess.run(args=startxray_cmd, shell=True, )
        if not error_code:
            print_msg('[Request] %s %s' % (method.upper(), api_url + '?' + _params_str))

    elif method.upper() == 'POST':

        try:
            # r = requests.post(api_url, data=_params_str, proxies=proxies, headers=headers, verify=False)
            r = requests.post(api_url, data=_params_str, headers=headers, verify=False)
        #     if not error_code:
        #         print_msg('[Request] %s %s %s' % (method.upper(), api_url, _params_str))
        except Exception as e:
            #     startxray_cmd = current_path + "/lib/xray/xray_darwin_amd64 webscan -u " + (
            #                 api_url + '?' + _params_str) + " -d \"" + _params_str + "\" --html-output "+ log_path + "/xray_err_log"+str(time.time())+".html"
            #     print(startxray_cmd)
            #     subprocess.run(args=startxray_cmd, shell=True)
            print(e)
    elif method.upper() == 'PUT':
        try:
            # r = requests.put(api_url, data=_params_str, proxies=proxies, headers=headers, verify=False)
            r = requests.put(api_url, data=_params_str, headers=headers, verify=False)
            if not error_code:
                print_msg('[Request] %s %s %s' % (method.upper(), api_url, _params_str))
        except Exception as e:
            print(e)
    else:
        logger.error("No method")

    content_type = r.headers['content-type'] if 'content-type' in r.headers else ''
    content_length = r.headers['content-length'] if 'content-length' in r.headers else ''
    if not content_length:
        content_length = len(r.content)
    if not error_code:
        print_msg('[Response] Code: %s Content-Type: %s Content-Length: %s' % (
            r.status_code, content_type, content_length))
    else:
        if r.status_code not in [401, 403, 404] or r.status_code != error_code:
            global auth_bypass_detected
            auth_bypass_detected = True
            print_msg('[VUL] *** URL Auth Bypass ***')
            if method.upper() == 'GET':
                print_msg('[Request] [%s] %s' % (method.upper(), api_url + '?' + _params_str))
            else:
                print_msg('[Request] [%s] %s \n%s' % (method.upper(), api_url, _params_str))

    # Auth Bypass Test
    # if not error_code and r.status_code in [401, 403]:
    #     path = '/' + path
    #     scan_api(method, summary, base_url, path, params_str, global_ress, error_code=r.status_code)

    # save req data
    results = [base_url, summary, path, method, api_url, _params_str, r.status_code, r.text]
    global_ress.append(results)


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass


class RequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/proxy?url='):
            url = self.path[11:]
            if url.lower().startswith('http') and url.find('@') < 0:
                text = requests.get(url, headers=headers, verify=False).content
                if text.find('"schemes":[') < 0:
                    text = text[0] + '"schemes":["https","http"],' + text[1:]  # HTTP(s) Switch
                global auth_bypass_detected
                if auth_bypass_detected:
                    json_doc = json.loads(text)
                    paths = copy.deepcopy(json_doc['paths'].keys())
                    for path in paths:
                        json_doc['paths']['/' + path] = json_doc['paths'][path]
                        del json_doc['paths'][path]

                    text = json.dumps(json_doc)
            else:
                text = 'Request Error'
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-length", len(text))
            self.end_headers()
            self.wfile.write(text)

        return SimpleHTTPRequestHandler.do_GET(self)




