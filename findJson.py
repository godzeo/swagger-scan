from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from urllib.parse import urlparse
from lib.common import get_chrome_path

#在爆破前用于检测元素是否可以被找到
def check_jsonurl(target,errTarget,browser):
    try:

        browser.get(target)
        # 隐式等待，等待时间10秒
        browser.implicitly_wait(5)
        # wait = WebDriverWait(browser, 10)
        # wait.until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
        browser.set_page_load_timeout(5)
        browser.set_script_timeout(5)  # 这两种设置都进行才有效
        # elems = browser.find_elements(By.TAG_NAME,'a')
        # for elem in elems:
        #     href = elem.get_attribute('href')
        #     if href is not None:
        #         print(href)
        time.sleep(3)
        elems = browser.find_elements(By.XPATH,"//a[@href]")

        reUrl = elems[0].get_attribute("href")
        if reUrl.find("json") < 0:
            if reUrl.find("docs") < 0:
                for one in elems:
                    if one.accessible_name in 'json' or 'docs' :
                        reUrl = urlparse(target).scheme+"://"+urlparse(target).netloc+"/"+ one.accessible_name


    except Exception as e :
        print("err :  "+target.strip())
        errTarget.append(target.strip())

    browser.back()
    return reUrl,errTarget

def start_chrom():
    print('[+] 正在后台打开谷歌浏览器...')


    chrome_path = get_chrome_path()
    chrome_option = Options()

    chrome_option.add_argument('blink-settings=imagesEnabled=false')
    chrome_option.add_argument('--ignore-certificate-errors')
    chrome_option.add_argument('--headless')
    # chrome_option.add_argument('--proxy-server=socks5h://127.0.0.1:1082')
    # chrome_option.add_argument('proxy_options')
    chrome_option.add_experimental_option('excludeSwitches', ['enable-logging'])  # 关闭控制台日志
    browser = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_option)


    browser.set_page_load_timeout(500)
    return browser


def writeTmpOut(jsonUrl,errTarget):
    with open('out/err_target', 'w+', encoding='utf8') as f2:
        for e1 in errTarget:
            f2.write(e1 + "\r\n")
    f2.close()
    with open('out/jsonurl_target', 'w+', encoding='utf8') as f3:
        for e1 in jsonUrl:
            f3.write(e1 + "\r\n")
    f3.close()


def findJson(urls):
        target_list = urls
        jsonUrl = []
        errTarget = []

        browser = start_chrom()
        while len(target_list) != 0:
            target = target_list.pop(0)
            try:
                reUrl,errTarget = check_jsonurl(target,errTarget,browser)
                if reUrl:
                    print('Find json url : '+reUrl)
                    jsonUrl.append(reUrl)
                    continue
            except Exception as e:
                if 'ERR_CONNECTION_TIMED_OUT' in str(e):
                    print('域名访问失败，已跳过任务')
        browser.quit()

        writeTmpOut(jsonUrl,errTarget)

        print("[+] 获区url结束，正在关闭浏览器，请稍等")
        return jsonUrl

if __name__ == '__main__':

    f = open("url.txt", 'r')
    urls = f.readlines()
    f.close()

    findJson(urls)