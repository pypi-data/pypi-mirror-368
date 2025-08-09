import json
import uuid
from rpa_common import Env
from rpa_common.library import Request
from rpa_common import Common as common
from rpa_common.service import ExecuteService
from rpa_common.request import TaskRequest
from rpa_common.exceptions import TaskParamsException
from rpa_lazada.service.LazadaService import LazadaService

env = Env()
request = Request()
executeService = ExecuteService()
taskRequest = TaskRequest()
lazadaService = LazadaService()


class EarnestAmountApi():
    def __init__(self):
        super().__init__()
        self.host = env.get().get('api','')

    def earnest_amount(self, driver, options):
        '''
        @Desc    : 获取资金申报-保证金
        @Author  : 洪润涛
        @Time    : 2024/07/24 11:50:37
        '''
        if "site" not in options:
            raise TaskParamsException("缺少 site")
        site = options.get("site")

        # 获取保证金，只有非本土才有保证金，不是所有非本土都有保证金
        print('-----------------开始获取资金申报【保证金】数据')
        load_data = {"_timezone": -8}
        # 接口api
        api = 'mtop.lazada.onboard.cb.deposit.getDepositDetail'
        # 发送请求  保证金站点固定为MY
        response = lazadaService.get_api_response(driver, load_data, 'MY', api)
        print('********请求【保证金】得到的数据：', type(response), response)
        # 数据格式转换
        if isinstance(response, (dict, list)):
            response = json.dumps(response, ensure_ascii=False)
        # 保存数据
        options['request_id'] = str(uuid.uuid4())
        options['response'] = response
        taskRequest.save(options)
