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


class ReadyGrantApi():
    def __init__(self):
        super().__init__()
        self.host = env.get().get('api','')

    def ready_grant(self, driver, options):
        '''
        @Desc    : 获取资金申报-准备发放账单
        @Author  : 洪润涛
        @Time    : 2024/07/24 13:36:46
        '''
        if "site" not in options:
            raise TaskParamsException("缺少 site")
        site = options.get("site")

        print('-----------------开始获取资金申报【账单--准备发放状态】所有金额数据')
        page_size = 100
        load_data = {
            "_timezone": -8,
            "isOpen": False,
            "queryType": "STATEMENT",
            "currentPage": 1,
            "pageSize": page_size,
            "startDate": "",
            "endDate": "",
            "statementReleaseStatus": "1"
        }
        # 接口api
        api = 'mtop.lazada.finance.sellerfund3.release.queryPageStatement'
        while True:
            # 发送请求
            response = lazadaService.get_api_response(driver, load_data, site, api)
            print('********请求【账单--准备发放状态】得到的数据：', type(response), response)

            data = json.loads(response).get('data', {}).get('data', {})
            dataSourc = data.get('dataSource')
            pageInfo = data.get('pageInfo')
            if not pageInfo:
                break
            # total 总数据量
            total = pageInfo.get('total', 0)

            # 数据格式转换
            if isinstance(response, (dict, list)):
                response = json.dumps(response, ensure_ascii=False)
            # 保存数据
            options['request_id'] = str(uuid.uuid4())
            options['page_number'] = load_data['currentPage']  # 页码
            options['page_size'] = page_size  # 页数
            options['list_count'] = len(dataSourc)  # 列表数据
            options['total_count'] = total  # 总数据
            options['response'] = response
            taskRequest.save(options)

            if total < (load_data['currentPage'] * page_size):
                break
            # 翻页
            load_data['currentPage'] += 1
            time.sleep(0.5)
            print('[翻页]')