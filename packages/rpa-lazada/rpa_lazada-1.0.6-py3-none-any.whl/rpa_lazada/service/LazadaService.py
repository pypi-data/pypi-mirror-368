import hashlib
import json
import time
from rpa_common import Env
from rpa_common.library import Request
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from rpa_common import Common
from rpa_common.library import Chrome
from rpa_common.service import ExecuteService
from rpa_common.request import ShopRequest
from rpa_lazada.api.ShopApi import ShopApi

env = Env()
common = Common()
request = Request()
chrome = Chrome()
executeService = ExecuteService()
shopRequest = ShopRequest()
shopApi = ShopApi()

class LazadaService():
    def __init__(self):
        super().__init__()
        self.host = env.get().get('api','')

    def login(self,driver, data, options):
        # 记录开始时间
        print('**********options',options)
        start_time = time.time()
        storage_data = data.get("storage_data")
        # 根据 need_login 决定是否执行登录逻辑
        need_login = True
        # 如果 storage_data 存在，注入缓存
        if storage_data.get('cookies'):
            print("🌐 主账号缓存尝试自动登录")
            self.inject_storage(driver, storage_data)

            # 获取登录信息
            res = shopApi.getInfoList(driver, data, options)
            print("使用缓存登录获取登录信息", res)
            try:
                res = json.loads(res)
                if res.get('data'):
                    print("✅ 成功获取店铺信息，使用缓存登录成功")
                    need_login = False
                else:
                    print("🔒 可能未登录")
                    print(res)
                    need_login = True
            except Exception as e:
                need_login = True

        if need_login:
            # 执行登录流程
            login_res = self.account_login(driver, data, options)
            # 登录失败
            if login_res['status'] == 0:
                return login_res
        else:
            # 已登录
            print("✅ 主账号已登录")
        print("🌐 站点账号缓存自动登录")
        self.inject_storage_site(driver)
        # 计算运行时长（秒）
        run_duration = time.time() - start_time
        print(f"用时：{run_duration}秒")
        print("✅ 登录成功")

        return common.back(1, '登录成功')

    def account_login(self, driver, data, options):
        '''
        @Desc    : 账号登录
        @Author  : 洪润涛
        @Time    : 2024/07/15 10:20:22
        '''
        print("账号登录")
        print('data',data)
        shop_global_id = data.get("shop_global_id")
        login_name = data.get("login_name")
        password = data.get("password")
        is_local = data.get("is_local")
        # 访问页面
        if is_local in [0, '0']:
            # 非本土登录URL
            driver.get("https://gsp.lazada.com/page/login")
        if is_local in [1, '1']:
            # 本土登录URL
            driver.get(f"https://sellercenter.lazada{self.site_map(options['params']['site'])}/apps/seller/login")

        wait = WebDriverWait(driver, 15)

        email_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="account"]')))
        email_input.send_keys(login_name)
        print("✅ 账号已填写")
        time.sleep(1)

        password_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@id="password"]')))
        password_input.send_keys(password)
        print("✅ 密码已填写")
        time.sleep(1)

        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-spm="home_next"]')))
        login_button.click()
        print("✅ 点击了登录按钮")
        time.sleep(1)

        print("等待5秒")
        time.sleep(5)

        # 获取当前URL
        current_url = driver.current_url
        if 'login' not in current_url:
            # 获取登录信息
            res = shopApi.getInfoList(driver, data, options)
            print("获取登录信息", res)
            if not json.loads(res).get('data'):
                raise ValueError('获取登录信息异常')

        # 保存店铺缓存
        self.save_storage(driver,data,options,shop_global_id)

        return common.back(1, '登录成功')

    def save_storage(self, driver,data,options,shop_global_id):
        '''
        @Desc    : 保存店铺缓存
        @Author  : 洪润涛
        @Time    : 2024/07/21 18:15:22
        '''
        # 获取 cookies
        print("获取 cookies")
        cookies = driver.get_cookies()
        print(cookies)
        # 获取 API域名的缓存
        print("获取 API域名的缓存")
        is_local = data.get('is_local')
        if is_local in [0, '0']:
            driver.get("https://gsp.lazada.com/api/account/manage/query.do?_timezone=-8&tab=account")
        if is_local in [1, '1']:
            driver.get(f'https://acs-m.lazada{self.site_map(options["params"]["site"])}/h5/mtop.global.merchant.subaccount.otp.userinfo/1.0/')
        time.sleep(3)
        cookies += driver.get_cookies()

        storage_data = {
            "shop_global_id": shop_global_id,
            "cookies": json.dumps(cookies)
        }

        # 保存店铺缓存
        print("保存店铺缓存")
        res = shopRequest.saveStorage(storage_data)
        if res['code'] != 1:
            print("保存缓存成功")
            return common.back(0, res['msg'])

        print("保存缓存成功")

    def inject_storage(self, driver, storage_data):
        '''
        @Desc    : 注入缓存
        @Author  : 洪润涛
        @Time    : 2024/07/21 18:15:22
        '''
        try:
            cookies = storage_data.get("cookies")

            driver.execute_cdp_cmd("Network.enable", {})
            for cookie in cookies:
                try:
                    # 新域名 cookie
                    driver.execute_cdp_cmd("Network.setCookie", {
                        "name": cookie["name"],
                        "value": cookie["value"],
                        "domain": cookie["domain"],
                        "path": cookie.get("path", "/"),
                        "secure": cookie.get("secure", False),
                        "httpOnly": cookie.get("httpOnly", False),
                        "sameSite": cookie.get("sameSite", "None")
                    })
                except Exception as e:
                    print(f"⚠️ CDP 注入 cookie 失败：{cookie}, 错误：{e}")

        except Exception as e:
            print(f"⚠️ 缓存登录失败: {e}")

        print("注入缓存成功")

    def inject_storage_site(self, driver):
        '''
        @Desc    : 注入站点缓存
        @Author  : 洪润涛
        @Time    : 2024/07/21 18:15:22
        '''
        try:
            cookies = driver.get_cookies()
            cookie = {item['name']:item['value'] for item in cookies}
            JSID = cookie.get('JSID')
            driver.execute_cdp_cmd("Network.enable", {})
            try:
                for site in ['ph','id','th','my','sg','vn']:
                    site_domin = '.lazada'+self.site_map(site)
                    driver.execute_cdp_cmd("Network.setCookie", {
                        "name": "JSID",
                        "value": JSID,
                        "domain": site_domin,
                        "path": "/",
                        "secure": True,
                        "httpOnly": True,
                        "sameSite": "None"
                    })
                    # 设置中文
                    driver.execute_cdp_cmd("Network.setCookie", {
                        "name": "_lang",
                        "value": "zh_CN",
                        "domain": site_domin,
                        "path": "/",
                        "secure": True,
                        "httpOnly": True,
                        "sameSite": "None"
                    })
            except Exception as e:
                print(f"⚠️ CDP 注入 cookie 失败：{cookie}, 错误：{e}")

        except Exception as e:
            print(f"⚠️ 缓存登录失败: {e}")

        print("注入缓存成功")

    def get_sign(self, driver, load_data: dict, g=''):
        """
        @Desc     : 生成sign专用
        @Author   : 洪润涛
        @Time     : 2025/07/21 16:53:36
        @Params   :
            - load_data: 要加密的data数据，dict格式
            - g: 30267743: 有权限的  4272:未知   12574478: 无权限，临时的
        """
        _m_h5_tk = None
        # 双重cookie获取
        _m_h5_tk = common.getCookie(driver, '_m_h5_tk')
        if not _m_h5_tk:
            for _ in range(10):
                # 获取浏览器cookie
                # 这里使用driver.get_cookies()会获取到空的cookie，所以直接返回document.cookie
                cookie_str = driver.execute_script('return document.cookie')
                print('[cookies] ->', cookie_str)
                pairs = [pair.strip() for pair in cookie_str.split(';')]
                for pair in pairs:
                    if '=' in pair:
                        name, value = pair.split('=', 1)  # 只分割一次
                        if name.strip() == '_m_h5_tk':
                            _m_h5_tk = value
                            break
                break
        if not _m_h5_tk:
            raise ValueError('获取token[_m_h5_tk]失败，无法继续')
        token = _m_h5_tk.split('_')[0]
        print('[token] -->', token)
        i = str(int(time.time() * 1000))
        g = g or ''
        data = json.dumps(load_data, separators=(',', ':'))
        print('[data] -->', data)
        # MD5哈希
        print('[hash_data] -->',(token + "&" + i + "&" + g + "&" + data))
        md5_hash = hashlib.md5()
        md5_hash.update((token + "&" + i + "&" + g + "&" + data).encode('utf-8'))
        sign = md5_hash.hexdigest()
        print('[sign] -->', sign)
        return {
            't': i,
            'appKey': g,
            'sign': sign,
            'data': data,
        }

    def site_map(self,site):
        # 站点映射
        site_map = {
            'ph': '.com.ph',
            'my': '.com.my',
            'id': '.co.id',
            'sg': '.sg',
            'th': '.co.th',
            'vn': '.vn',
        }.get(site.lower())
        if not site_map:
            raise ValueError(f"{site}站点不支持")
        return site_map

    def get_params(self, sign_data, site, api):
        """
        @Desc     : 生成params专用
        @Author   : 洪润涛
        @Time     : 2025/07/22 10:53:36
        @Params   :
            - sign_data: sign_data
            - site: 站点
            - api: Lazada接口api
        """
        return {
            "jsv": "2.6.1",
            "appKey": sign_data['appKey'],
            "t": sign_data['t'],
            "sign": sign_data['sign'],
            "v": "1.0",
            "timeout": "30000",
            "H5Request": "true",
            "url": api,
            "type": "originaljson",
            "method": "GET",
            "api": api,
            "dataType": "json",
            "valueType": "original",
            "x-i18n-regionID": "LAZADA_" + site.upper(),
            "data": sign_data['data']
        }

    def get_api_response(self, driver, load_data, site, api, g='4272'):
        """
        @Desc     : Lazada api请求封装
        @Author   : 洪润涛
        @Time     : 2025/07/24 09:15:50
        @Params   : 30267743: 有权限的  4272:未知   12574478: 无权限，临时的  默认4272
            - load_data: 请求参数data
            - site: 站点
            - api: Lazada接口api
            - g: 默认4272
        """
        # 访问接口页面
        driver.get(f'https://acs-m.lazada{self.site_map(site)}/h5/{api}/1.0/')
        time.sleep(2)
        # 获取sign_data
        sign_data = self.get_sign(driver, load_data, g)
        # 获取params
        params = self.get_params(sign_data=sign_data, site=site, api=api)
        # 请求 URL
        url = f'https://acs-m.lazada{self.site_map(site)}/h5/{api}/1.0/?' + common.object_to_params(params)
        # 发送请求
        response = executeService.request(driver, url, method='GET')
        return response
