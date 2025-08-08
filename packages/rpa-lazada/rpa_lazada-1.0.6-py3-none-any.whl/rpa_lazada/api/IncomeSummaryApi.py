import json
import time
import uuid
from rpa_common import Env
from rpa_common.library import Request
from rpa_common.service import ExecuteService
from rpa_common.request import TaskRequest
from rpa_common.exceptions import TaskParamsException
from rpa_lazada.service.LazadaService import LazadaService

env = Env()
request = Request()
executeService = ExecuteService()
taskRequest = TaskRequest()
lazadaService = LazadaService()


class IncomeSummaryApi():
    def __init__(self):
        super().__init__()
        self.host = env.get().get('api','')

    def income_summary(self, driver, options):
        '''
        @Desc    : 获取资金申报-收入概括
        @Author  : 洪润涛
        @Time    : 2024/07/24 11:58:22
        '''
        if "site" not in options:
            raise TaskParamsException("缺少 site")
        site = options.get("site")

        print('-----------------开始获取资金申报【收入概括】数据')
        time.sleep(2)
        load_data = {"_timezone": -8, "userIdentityType": "SELLER"}
        # 接口api
        api = 'mtop.lazada.finance.sellerfund3.release.queryToReleaseAgg'
        # 发送请求
        response = lazadaService.get_api_response(driver, load_data, site, api)
        print('********请求【钱包余额】得到的数据：', type(response), response)
        # 数据格式转换
        if isinstance(response, (dict, list)):
            response = json.dumps(response, ensure_ascii=False)
        # 保存数据
        options['request_id'] = str(uuid.uuid4())
        options['response'] = response
        taskRequest.save(options)
