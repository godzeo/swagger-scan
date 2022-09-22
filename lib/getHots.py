import socket
import urllib.parse
import os

def main(url):
    lines = os.popen('nslookup '+url)
    row = lines.readlines()
    if len(row) > 5:
        for ip in row[5:]:
            if 'Address:' in ip:
                ip=ip.split(':')[1].strip()
                print(ip)


if __name__ == '__main__':

    f = open("/Users/yi.zhai/Desktop/swagger/url.txt", 'r')
    urls = f.readlines()
    for u in urls:
        print(main(u))