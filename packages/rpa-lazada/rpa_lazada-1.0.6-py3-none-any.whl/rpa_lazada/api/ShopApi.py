from rpa_common import Env
from rpa_common.library import Request
from rpa_common.service import ExecuteService
from rpa_common.request import TaskRequest

env = Env()
request = Request()
executeService = ExecuteService()
taskRequest = TaskRequest()

class ShopApi():
    def __init__(self):
        super().__init__()
        self.host = env.get().get('api','')

    def getInfoList(self, driver, data, options):
        '''
        @Desc    : 获取店铺信息
        @Author  : 洪润涛
        @Time    : 2024/07/21 18:15:22
        '''
        site = options.get('params').get('site')
        is_local = data.get('is_local')
        # 获取用户信息
        if is_local in [0, '0']:
            # 非本土
            url = 'https://gsp.lazada.com/api/account/manage/query.do?_timezone=-8&tab=account'
            driver.get(url)
            response = executeService.request(driver, url, method="GET")
            return response

        if is_local in [1, '1']:
            # 本土
            from rpa_lazada.service.LazadaService import LazadaService
            lazadaService = LazadaService()

            api = 'mtop.global.merchant.subaccount.otp.userinfo/1.0/'
            response = lazadaService.get_api_response(driver, {}, site, api)
            return response
