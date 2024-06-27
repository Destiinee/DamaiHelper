import json
from jsoncomment import JsonComment
from os.path import exists
from pickle import dump, load
from time import sleep, time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

class Concert(object):
    def __init__(self, date, session, price, real_name, nick_name, ticket_num, viewer_person, damai_url, target_url,
                 driver_path):
        self.date = date  # 日期序号
        self.session = session  # 场次序号优先级
        self.price = price  # 票价序号优先级
        self.real_name = real_name  # 实名者序号
        self.status = 0  # 状态标记
        self.time_start = 0  # 开始时间
        self.time_end = 0  # 结束时间
        self.num = 0  # 尝试次数
        self.ticket_num = ticket_num  # 购买票数
        self.viewer_person = viewer_person  # 观影人序号优先级
        self.nick_name = nick_name  # 用户昵称
        self.damai_url = damai_url  # 大麦网官网网址
        self.target_url = target_url  # 目标购票网址
        self.driver_path = driver_path  # 浏览器驱动地址
        self.driver = None

    def isClassPresent(self, item, name, ret=False):
        try:
            result = item.find_element(by=By.CLASS_NAME, value=name)
            if ret:
                return result
            else:
                return True
        except:
            return False

    # 获取账号的cookie信息
    def get_cookie(self):
        self.driver.get(self.damai_url)
        print("###请点击登录###")
        self.driver.find_element(by=By.CLASS_NAME, value='login-user').click()
        while self.driver.title.find('大麦网-全球演出赛事官方购票平台') != -1:  # 等待网页加载完成
            sleep(1)
        print("###请扫码登录###")
        while self.driver.title == '大麦登录':  # 等待扫码完成
            sleep(1)
        dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))
        print("###Cookie保存成功###")

    def set_cookie(self):
        try:
            cookies = load(open("cookies.pkl", "rb"))  # 载入cookie
            for cookie in cookies:
                cookie_dict = {
                    'domain': '.damai.cn',  # 必须有，不然就是假登录
                    'name': cookie.get('name'),
                    'value': cookie.get('value'),
                    "expires": "",
                    'path': '/',
                    'httpOnly': False,
                    'HostOnly': False,
                    'Secure': False}
                self.driver.add_cookie(cookie_dict)
            print("###载入Cookie###")
        except Exception as e:
            print(e)

    def login(self):
        print("###开始登录###")
        self.driver.get(self.target_url)
        WebDriverWait(self.driver, 10, 0.1).until(EC.title_contains('商品详情'))
        self.set_cookie()

    def enter_concert(self):
        self.time_start = time()  # 记录开始时间
        print("###打开浏览器，进入大麦网###")
        if not exists('cookies.pkl'):  # 如果不存在cookie.pkl,就获取一下
            service = Service(self.driver_path)
            self.driver = webdriver.Chrome(service=service)
            self.get_cookie()
            print("###成功获取Cookie，重启浏览器###")
            self.driver.quit()

        options = Options()
        # 禁止图片、js、css加载
        prefs = {"profile.managed_default_content_settings.images": 2,
                 "profile.managed_default_content_settings.javascript": 1,
                 'permissions.default.stylesheet': 2}
        mobile_emulation = {"deviceName": "Nexus 6"}
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        # 去掉webdriver痕迹
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--log-level=3')

        # 更换等待策略为不等待浏览器加载完全就进行下一步操作
        capa = DesiredCapabilities.CHROME
        capa["pageLoadStrategy"] = "eager"
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        # self.driver = webdriver.Chrome(service=service, options=options, desired_capabilities=capa)
        # 登录到具体抢购页面
        self.login()
        self.driver.refresh()

    # 其他方法保持不变...

if __name__ == '__main__':
    try:
        with open('D:\VS_Code\DamaiHelper-main\config.json', 'r', encoding='utf-8') as f:
            parser = JsonComment(json)
            config = parser.loads(f.read())
            # params: 场次优先级，票价优先级，实名者序号, 用户昵称， 购买票数， 官网网址， 目标网址, 浏览器驱动地址
        con = Concert(config['date'], config['sess'], config['price'], config['real_name'], config['nick_name'],
                      config['ticket_num'], config['viewer_person'], config['damai_url'], config['target_url'],
                      config['driver_path'])
        con.enter_concert()  # 进入到具体抢购页面
    except Exception as e:
        print(e)
        exit(1)

    while True:
        try:
            con.choose_ticket()
            retry = con.check_order()
            if not retry:
                break
        except Exception as e:
            con.driver.get(con.target_url)
            print(e)
            continue

    if con.status == 6:
        print("###经过%d轮奋斗，耗时%.1f秒，成功为您抢票！请及时确认订单信息并完成支付！###" % (
            con.num, round(con.time_end - con.time_start, 3)))
        input("按 Enter 键退出脚本")
import json
from jsoncomment import JsonComment
from os.path import exists
from pickle import dump, load
from time import sleep, time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

class Concert(object):
    def __init__(self, date, session, price, real_name, nick_name, ticket_num, viewer_person, damai_url, target_url,
                 driver_path):
        self.date = date  # 日期序号
        self.session = session  # 场次序号优先级
        self.price = price  # 票价序号优先级
        self.real_name = real_name  # 实名者序号
        self.status = 0  # 状态标记
        self.time_start = 0  # 开始时间
        self.time_end = 0  # 结束时间
        self.num = 0  # 尝试次数
        self.ticket_num = ticket_num  # 购买票数
        self.viewer_person = viewer_person  # 观影人序号优先级
        self.nick_name = nick_name  # 用户昵称
        self.damai_url = damai_url  # 大麦网官网网址
        self.target_url = target_url  # 目标购票网址
        self.driver_path = driver_path  # 浏览器驱动地址
        self.driver = None

    def isClassPresent(self, item, name, ret=False):
        try:
            result = item.find_element(by=By.CLASS_NAME, value=name)
            if ret:
                return result
            else:
                return True
        except:
            return False

    # 获取账号的cookie信息
    def get_cookie(self):
        self.driver.get(self.damai_url)
        print("###请点击登录###")
        self.driver.find_element(by=By.CLASS_NAME, value='login-user').click()
        while self.driver.title.find('大麦网-全球演出赛事官方购票平台') != -1:  # 等待网页加载完成
            sleep(1)
        print("###请扫码登录###")
        while self.driver.title == '大麦登录':  # 等待扫码完成
            sleep(1)
        dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))
        print("###Cookie保存成功###")

    def set_cookie(self):
        try:
            cookies = load(open("cookies.pkl", "rb"))  # 载入cookie
            for cookie in cookies:
                cookie_dict = {
                    'domain': '.damai.cn',  # 必须有，不然就是假登录
                    'name': cookie.get('name'),
                    'value': cookie.get('value'),
                    "expires": "",
                    'path': '/',
                    'httpOnly': False,
                    'HostOnly': False,
                    'Secure': False}
                self.driver.add_cookie(cookie_dict)
            print("###载入Cookie###")
        except Exception as e:
            print(e)

    def login(self):
        print("###开始登录###")
        self.driver.get(self.target_url)
        WebDriverWait(self.driver, 10, 0.1).until(EC.title_contains('商品详情'))
        self.set_cookie()

    def enter_concert(self):
        self.time_start = time()  # 记录开始时间
        print("###打开浏览器，进入大麦网###")
        if not exists('cookies.pkl'):  # 如果不存在cookie.pkl,就获取一下
            service = Service(self.driver_path)
            self.driver = webdriver.Chrome(service=service)
            self.get_cookie()
            print("###成功获取Cookie，重启浏览器###")
            self.driver.quit()

        options = Options()
        # 禁止图片、js、css加载
        prefs = {"profile.managed_default_content_settings.images": 2,
                 "profile.managed_default_content_settings.javascript": 1,
                 'permissions.default.stylesheet': 2}
        mobile_emulation = {"deviceName": "Nexus 6"}
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        # 去掉webdriver痕迹
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--log-level=3')

        # 更换等待策略为不等待浏览器加载完全就进行下一步操作
        capa = DesiredCapabilities.CHROME
        capa["pageLoadStrategy"] = "eager"
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=options, desired_capabilities=capa)
        # 登录到具体抢购页面
        self.login()
        self.driver.refresh()

    # 其他方法保持不变...

if __name__ == '__main__':
    try:
        with open('./config.json', 'r', encoding='utf-8') as f:
            parser = JsonComment(json)
            config = parser.loads(f.read())
            # params: 场次优先级，票价优先级，实名者序号, 用户昵称， 购买票数， 官网网址， 目标网址, 浏览器驱动地址
        con = Concert(config['date'], config['sess'], config['price'], config['real_name'], config['nick_name'],
                      config['ticket_num'], config['viewer_person'], config['damai_url'], config['target_url'],
                      config['driver_path'])
        con.enter_concert()  # 进入到具体抢购页面
    except Exception as e:
        print(e)
        exit(1)

    while True:
        try:
            con.choose_ticket()
            retry = con.check_order()
            if not retry:
                break
        except Exception as e:
            con.driver.get(con.target_url)
            print(e)
            continue

    if con.status == 6:
        print("###经过%d轮奋斗，耗时%.1f秒，成功为您抢票！请及时确认订单信息并完成支付！###" % (
            con.num, round(con.time_end - con.time_start, 3)))
        input("按 Enter 键退出脚本")
import json
from jsoncomment import JsonComment
from os.path import exists
from pickle import dump, load
from time import sleep, time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

class Concert(object):
    def __init__(self, date, session, price, real_name, nick_name, ticket_num, viewer_person, damai_url, target_url,
                 driver_path):
        self.date = date  # 日期序号
        self.session = session  # 场次序号优先级
        self.price = price  # 票价序号优先级
        self.real_name = real_name  # 实名者序号
        self.status = 0  # 状态标记
        self.time_start = 0  # 开始时间
        self.time_end = 0  # 结束时间
        self.num = 0  # 尝试次数
        self.ticket_num = ticket_num  # 购买票数
        self.viewer_person = viewer_person  # 观影人序号优先级
        self.nick_name = nick_name  # 用户昵称
        self.damai_url = damai_url  # 大麦网官网网址
        self.target_url = target_url  # 目标购票网址
        self.driver_path = driver_path  # 浏览器驱动地址
        self.driver = None

    def isClassPresent(self, item, name, ret=False):
        try:
            result = item.find_element(by=By.CLASS_NAME, value=name)
            if ret:
                return result
            else:
                return True
        except:
            return False

    # 获取账号的cookie信息
    def get_cookie(self):
        self.driver.get(self.damai_url)
        print("###请点击登录###")
        self.driver.find_element(by=By.CLASS_NAME, value='login-user').click()
        while self.driver.title.find('大麦网-全球演出赛事官方购票平台') != -1:  # 等待网页加载完成
            sleep(1)
        print("###请扫码登录###")
        while self.driver.title == '大麦登录':  # 等待扫码完成
            sleep(1)
        dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))
        print("###Cookie保存成功###")

    def set_cookie(self):
        try:
            cookies = load(open("cookies.pkl", "rb"))  # 载入cookie
            for cookie in cookies:
                cookie_dict = {
                    'domain': '.damai.cn',  # 必须有，不然就是假登录
                    'name': cookie.get('name'),
                    'value': cookie.get('value'),
                    "expires": "",
                    'path': '/',
                    'httpOnly': False,
                    'HostOnly': False,
                    'Secure': False}
                self.driver.add_cookie(cookie_dict)
            print("###载入Cookie###")
        except Exception as e:
            print(e)

    def login(self):
        print("###开始登录###")
        self.driver.get(self.target_url)
        WebDriverWait(self.driver, 10, 0.1).until(EC.title_contains('商品详情'))
        self.set_cookie()

    def enter_concert(self):
        self.time_start = time()  # 记录开始时间
        print("###打开浏览器，进入大麦网###")
        if not exists('cookies.pkl'):  # 如果不存在cookie.pkl,就获取一下
            service = Service(self.driver_path)
            self.driver = webdriver.Chrome(service=service)
            self.get_cookie()
            print("###成功获取Cookie，重启浏览器###")
            self.driver.quit()

        options = Options()
        # 禁止图片、js、css加载
        prefs = {"profile.managed_default_content_settings.images": 2,
                 "profile.managed_default_content_settings.javascript": 1,
                 'permissions.default.stylesheet': 2}
        mobile_emulation = {"deviceName": "Nexus 6"}
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        # 去掉webdriver痕迹
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--log-level=3')

        # 更换等待策略为不等待浏览器加载完全就进行下一步操作
        capa = DesiredCapabilities.CHROME
        capa["pageLoadStrategy"] = "eager"
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=options, desired_capabilities=capa)
        # 登录到具体抢购页面
        self.login()
        self.driver.refresh()

    # 其他方法保持不变...

if __name__ == '__main__':
    try:
        with open('./config.json', 'r', encoding='utf-8') as f:
            parser = JsonComment(json)
            config = parser.loads(f.read())
            # params: 场次优先级，票价优先级，实名者序号, 用户昵称， 购买票数， 官网网址， 目标网址, 浏览器驱动地址
        con = Concert(config['date'], config['sess'], config['price'], config['real_name'], config['nick_name'],
                      config['ticket_num'], config['viewer_person'], config['damai_url'], config['target_url'],
                      config['driver_path'])
        con.enter_concert()  # 进入到具体抢购页面
    except Exception as e:
        print(e)
        exit(1)

    while True:
        try:
            con.choose_ticket()
            retry = con.check_order()
            if not retry:
                break
        except Exception as e:
            con.driver.get(con.target_url)
            print(e)
            continue

    if con.status == 6:
        print("###经过%d轮奋斗，耗时%.1f秒，成功为您抢票！请及时确认订单信息并完成支付！###" % (
            con.num, round(con.time_end - con.time_start, 3)))
        input("按 Enter 键退出脚本")
