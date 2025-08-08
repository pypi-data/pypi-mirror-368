import uuid
import json
import time
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

class PromoApi():
    def __init__(self):
        super().__init__()
        self.host = env.get().get('api','')

    def shop_promo(self, driver, options):
        '''
        @Desc    : 获取促销费
        @Author  : 洪润涛
        @Time    : 2024/07/21 09:51:35
        '''
        if "site" not in options:
            raise TaskParamsException("缺少 site")
        site = options.get("site")

        # 1 和 7 分别代表 已加入 和 历史
        page_size = 100
        # 接口api
        api = 'mtop.lazada.signing.seller.program.query'
        for sellerProgramNewStatus in [1, 7]:
            # sellerProgramNewStatus：1 = 已加入  7 = 历史
            # pageSize：每页数量
            load_data = {
                "spm": "",
                "tab": "1",
                "sellerProgramNewStatus": sellerProgramNewStatus,
                "current": 1,
                "pageSize": page_size
            }
            while True:
                response = lazadaService.get_api_response(driver, load_data, site, api)
                print('********请求得到的数据：', type(response), response)

                data = json.loads(response).get('data', {}).get('data', {})
                dataSourc = data.get('dataSource')
                pageInfo = data.get('pageInfo')
                if not pageInfo:
                    break
                # total 总数据量
                total = pageInfo.get('total',0)

                # 数据格式转换
                if isinstance(response, (dict, list)):
                    response = json.dumps(response, ensure_ascii=False)
                # 保存数据
                options['request_id'] = str(uuid.uuid4())
                options['page_number'] = load_data['current']  # 页码
                options['page_size'] = page_size  # 页数
                options['list_count'] = len(dataSourc)  # 列表数据
                options['total_count'] = total  # 总数据
                options['response'] = response
                taskRequest.save(options)

                if total < (load_data['current'] * page_size):
                    break
                # 翻页
                load_data['current'] += 1
                time.sleep(0.5)