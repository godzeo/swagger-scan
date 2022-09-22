# swagger-scan

主要是对在测试中常见的swagger页面泄露 ，进行批量的测试

- 自动爬取所有接口，配置好传参发包访问
- 可以代理到 Xray或者sqlmap 被动扫描



流程：

1. 抓取 html 页面，利用chromedriver去解析
2. 找到具体存放数据的json文件
3. 数据进行解析，构造请求包，获取响应
4. 记录发包、参数、加入被动的漏洞扫描


python findJson.py （自动把url.txt的地址批量找到json文件）

python swagger.py -u http://www.baidu.com/openapi.json
python swagger.py -f /xxxx/xxx/targert.txt

参考，借鉴代码，修改了一些实际测试的bug

https://github.com/jayus0821/swagger-hack
https://github.com/lijiejie/swagger-exp

