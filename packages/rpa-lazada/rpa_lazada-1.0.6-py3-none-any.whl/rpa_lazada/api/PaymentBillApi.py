import json
import time
import uuid
from datetime import datetime, timedelta
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


class PaymentBillApi():
    def __init__(self):
        super().__init__()
        self.host = env.get().get('api','')

    def payment_bill(self, driver, options):
        '''
        @Desc    : 获取打款账单
        @Author  : 洪润涛
        @Time    : 2024/07/15 14:25:35
        '''
        if "site" not in options:
            raise TaskParamsException("缺少 site")
        site = options.get("site")

        # 结束时间  使用当前时间转 %Y-%m-%d  eg：2025-07-07
        now = datetime.now()
        end_time = now.strftime("%Y-%m-%d")
        print('[结束时间]',end_time)

        # 开始时间 使用当前时间的前一周转 %Y-%m-%d   eg：2025-07-01
        one_week_ago = now - timedelta(days=7)
        start_time = one_week_ago.strftime("%Y-%m-%d")
        print('[开始时间]', start_time)

        # 获取当前URL
        current_url = driver.current_url
        print('[当前url] --> ', current_url)
        # 网站问题返回空数据的情况
        if 'apps/seller/account_health' in current_url:
            print('[网页因健康分问题导致没有数据，直接返回空]')
            options['request_id'] = str(uuid.uuid4())
            options['response'] = '[]'
            taskRequest.save(options)
        elif 'apps/seller/unaccessable' in current_url:
            print('[网页未开通钱包导致没有数据，直接返回空]')
            options['request_id'] = str(uuid.uuid4())
            options['response'] = '[]'
            taskRequest.save(options)
        elif 'apps/seller/landing' in current_url:
            print('[网页钱包未激活导致没有数据，直接返回空]')
            options['request_id'] = str(uuid.uuid4())
            options['response'] = '[]'
            taskRequest.save(options)
        else:
            PAGE = 1
            PAGE_SIZE = 100
            # 接口api
            api = 'mtop.lazada.finance.sellerwallet.statement.query'
            while True:
                load_data = {
                    "_timezone": -8,
                    "type": "",
                    "status": "",
                    "pageSize": PAGE_SIZE,
                    "pageNum": PAGE,
                    "current": 1,
                    "total": 8,
                    "pinDialog": "{}",
                    "liteDialog": "{}",
                    "kybDialog": "{}",
                    "timestamp": int(time.time() * 1000),
                    "startTime": start_time.replace('-', ''),
                    "endTime": end_time.replace('-', ''),
                }
                load_data['pageNum'] = PAGE
                load_data['pageSize'] = PAGE_SIZE
                # 获取响应
                response = lazadaService.get_api_response(driver, load_data, site, api)
                print('********请求得到的数据：', type(response),response)

                data = json.loads(response).get('data', {}).get('data', {})
                pageInfo = data.get('pageInfo')
                details = data.get('details')
                if not pageInfo:
                    break
                # 总页数
                totalPage = pageInfo.get('totalPage')
                # 总数据
                totalCount = pageInfo.get('totalCount')

                # 数据格式转换
                if isinstance(response, (dict, list)):
                    response = json.dumps(response, ensure_ascii=False)
                # 保存数据
                options['request_id'] = str(uuid.uuid4())
                options['page_number'] = PAGE  # 页码
                options['page_size'] = PAGE_SIZE  # 页数
                options['list_count'] = len(details)  # 列表数据
                options['total_count'] = totalCount  # 总数据
                options['response'] = response
                taskRequest.save(options)

                # 翻页
                if PAGE >= totalPage:
                    break
                PAGE += 1

                time.sleep(0.5)
