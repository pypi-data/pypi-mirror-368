import json
import time
import uuid
from rpa_common import Env
from rpa_common.library import Request
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from rpa_common.service import ExecuteService
from rpa_common.request import TaskRequest
from rpa_common.exceptions import TaskParamsException
from rpa_lazada.service.LazadaService import LazadaService

env = Env()
request = Request()
executeService = ExecuteService()
taskRequest = TaskRequest()
lazadaService = LazadaService()


class WalletBalanceApi():
    def __init__(self):
        super().__init__()
        self.host = env.get().get('api','')

    def wallet_balance(self, driver, options):
        '''
        @Desc    : 获取资金申报-钱包余额
        @Author  : 洪润涛
        @Time    : 2024/07/24 14:02:15
        '''
        if "site" not in options:
            raise TaskParamsException("缺少 site")
        site = options.get("site")

        print('-----------------判断店铺是否开通钱包')
        load_data = { "_timezone": -8, "fromPage": "HOME_PAGE" }
        # 接口api
        api = 'mtop.lazada.finance.sellerwallet.activation.query'
        # 发送请求
        response = lazadaService.get_api_response(driver, load_data, site, api)
        print('*******钱包开通数据：',type(response),response)
        if json.loads(response).get('data',{}).get('data',[])[0].get('activeStatus'):
            print('-----------------开始获取资金申报【钱包余额】数据')
            load_data = {"_timezone": -8, "userIdentityType": "SELLER"}
            # 接口api
            api = 'mtop.lazada.finance.sellerwallet.account.inquiry'
            # 发送请求
            response = lazadaService.get_api_response(driver, load_data, site, api)
            print('********请求【钱包】得到的数据：', type(response), response)
            # 数据格式转换
            if isinstance(response, (dict, list)):
                response = json.dumps(response, ensure_ascii=False)
            # 保存数据
            options['request_id'] = str(uuid.uuid4())
            options['response'] = response
            taskRequest.save(options)
        else:
            print('*******钱包未开通')
            # 保存数据
            options['request_id'] = str(uuid.uuid4())
            options['response'] = '钱包未开通'
            taskRequest.save(options)