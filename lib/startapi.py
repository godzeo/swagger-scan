import os


def startServer():
    # start = input('请输入sqlmap的路径：')
    try:
        # os.chdir(start)
        d = os.system('python3 lib/sqlmap/sqlmapapi.py -s -H 0.0.0.0 -p 8775')

        cmd = 'python3 lib/sqlmap/sqlmapapi.py -s -H 0.0.0.0 -p 8775'
        # p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # while True:
        #     output = p.stdout.readline()
        #     if output == '' and p.poll() is not None:
        #         break
        #     if output:
        #         print(output)
    except:
        print('异常退出')

if __name__ == '__main__':
    startServer()