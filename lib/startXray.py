import os
import platform
import subprocess
import time
import loguru


def startxray():
    current_path = os.getcwd()
    log_path = current_path+"/out"

    try:
        if platform.system() =='Windows':
            startxray_cmd="start xray/xray_windows_amd64.exe webscan --listen 127.0.0.1:7666 --html-output={}/xraylog.html".format(log_path)
            os.system(startxray_cmd)
            time.sleep(5)
        elif platform.system() == 'Darwin':
            startxray_cmd=current_path+"/lib/xray/xray_darwin_amd64 webscan --listen 0.0.0.0:8686 --html-output={}/xraylog{}.html &".format(log_path,str(time.time()))
            # os.system(startxray_cmd)
            subprocess.run(args=startxray_cmd, shell=True, check=True)
            time.sleep(5)
        else:
            startxray_cmd=current_path+"/xray/xray_linux_amd64 webscan --listen 127.0.0.1:7066 --html-output={}/xraylog.html".format(log_path)
            os.system(startxray_cmd)
            time.sleep(5)
        loguru.logger.success('[+] Xray启动成功')
    except Exception as e:
        loguru.logger.error( '[-] Xray启动错误 ' +e)


if __name__ == '__main__':
    startxray()