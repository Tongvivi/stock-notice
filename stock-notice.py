import re
import requests
from bs4 import BeautifulSoup
from time import sleep
from pushnotifier import PushNotifier as pn

#app登录信息 到这里获取 https://pushnotifier.de/
PN_loin = { "user_name" : "xxxxx",
            "password" :"xxxxx",
            "package" :"com.xxxxx.app",
            "token" :"xxxxx",
            "devices" : "xxxxx"
                     }

#监测股票列表
stock_codes = [ {"ts_code": "SZ300750", "name": "宁德时代"},
                {"ts_code": "SZ002594", "name": "比亚迪"},
                {"ts_code": "SH688111", "name": "金山办公"}]

# 涨幅幅度%
strategy_change_val = 1

#发送消息
def push_notic(text):

    if len(text) >= 255:
        text = text[0:255]

    pn_tool = pn.PushNotifier(PN_loin["user_name"], PN_loin["password"],PN_loin["package"],PN_loin["token"])

    return pn_tool.send_text(text, silent=False, devices=[PN_loin["devices"]])

#获取实时数据
def get_current_info(ts_code):

    session = requests.session()
    headers = {
        'accept-encoding': 'gzip, deflate, br',
        'Host': 'xueqiu.com',
        'Referer': 'https://xueqiu.com/S/SZ300750',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        'Cookie': 'st = c4dac0d45c2bafdb5a46ae47b574a1de'
    }

    url = 'https://xueqiu.com/S/{}'.format(ts_code)
    resp = session.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")

    stock = {'ts_code' : ts_code}

    stock_name = soup.select_one(".stock__main>.stock-name")
    print(url)

    if stock_name :
        stock_name = stock_name.get_text()
        stock_name = re.sub("[A-Za-z0-9\!\%\[\]\,\。:\(\)]+", "", stock_name)
        stock["name"] = stock_name

    stock_price = soup.select_one(".stock-current")
    if stock_price :
        stock["price"] = str(stock_price.get_text()).replace("¥", "")

    stock_change = soup.select_one(".stock-change")
    if stock_change :
        stock_change = str(stock_change.get_text()).replace("+", "").replace("%", "")
        stock_change = stock_change.split()
        stock["change"] = stock_change[0]
        stock["pct_chg"] = stock_change[1]

    stock_status = soup.select_one(".quote-market-status")
    if len(stock_status) > 0:
        stock["status"] = stock_status.get_text()

    print(stock)
    return stock

#策略1 涨幅判断
def strategy_change(stocks):

    text = ""
    for s in stocks:
        if float(s["pct_chg"]) > strategy_change_val:

            text += s["name"] + "\t"
            text += s["price"] + "\t"
            text += s["pct_chg"] + "% ,\t"

    return text

if __name__ == '__main__':

    #获取实时股票数据
    stocks = []
    for c in stock_codes:
        st = get_current_info(c["ts_code"])
        stocks.append(st)
        sleep(2)

    #处理数据,判断生成推送消息
    notic_text = ""
    notic_text = strategy_change(stocks)
    print("\n" + notic_text)

    #推送消息
    if len(notic_text) > 0:
        re = push_notic(notic_text)
        print(re)
        if re == "200" :
            print("发送成功")
        else:
            print("发送失败")