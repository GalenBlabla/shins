# Tests for the FastAPI application.

import urllib.parse
import urllib.request

#接口地址
url = 'http://106.ihuyi.com/webservice/sms.php?method=Submit'

#定义请求的数据
values = {
        'account': 'C92695365',
        'password': 'e29804a05ed8cec5ccd27f12aa0379a5',
    'mobile':'18009082890',
    'content':'您的验证码是：7835。请不要把验证码泄露给其他人。',
    'format':'json',
}

#将数据进行编码
data = urllib.parse.urlencode(values).encode(encoding='UTF8')

#发起请求
req = urllib.request.Request(url, data)
response = urllib.request.urlopen(req)
res = response.read()

#打印结果
print(res.decode("utf8"))
