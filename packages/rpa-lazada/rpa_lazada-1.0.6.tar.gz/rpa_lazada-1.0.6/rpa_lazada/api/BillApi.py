import json
import time
import uuid
from rpa_common import Env
from datetime import datetime, timedelta
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


class BillApi():
    def __init__(self):
        super().__init__()
        self.host = env.get().get('api','')

    def bill(self, driver, options):
        '''
        @Desc    : 获取账单
        @Author  : 洪润涛
        @Time    : 2024/07/24 17:04:25
        '''
        if "site" not in options:
            raise TaskParamsException("缺少 site")
        site = options.get("site")

        # 结束时间  使用当前时间转 %Y-%m-%d  eg：2025-07-07
        now = datetime.now()
        end_time = now.strftime("%Y-%m-%d")
        print('[结束时间]', end_time)

        # 开始时间 使用当前时间的前一周转 %Y-%m-%d   eg：2025-07-01
        one_week_ago = now - timedelta(days=7)
        start_time = one_week_ago.strftime("%Y-%m-%d")
        print('[开始时间]', start_time)

        # 站点映射
        site_map = lazadaService.site_map(site)
        # 接口api
        api = 'mtop.lazada.finance.sellerfund3.release.queryPageStatement'

        load_data = {
            "_timezone": -8,
             "isOpen": False,
             "queryType": "STATEMENT",
             "currentPage": 1,
             "pageSize": 100,
             "startDate": "",
             "endDate": "",
             "statementReleaseStatus": "2"
         }
        # 发送请求
        resp = lazadaService.get_api_response(driver, load_data, site, api)
        print('********请求【账单】得到的数据：', type(resp), resp)
        try:
            # 账单存在标识
            is_data = None
            dataSource_list = json.loads(resp).get('data', {}).get('data',{}).get('dataSource')
            if dataSource_list:
                for dataSource in dataSource_list:
                    # 获取数据-->账期
                    bill_data = dataSource.get('statementPeriod')
                    if bill_data:
                        # 05 May 2025  --> 2025-05-05 00:00:00
                        bill_start = self.parse_date(bill_data.split('-')[0].strip())
                        bill_end = self.parse_date(bill_data.split('-')[1].strip())
                        print('[账期开始时间]', bill_start)
                        print('[账期结束时间]', bill_end)

                        # 判断筛选开始日期到结束日期是否在网页账期的开始时间和结束时间中，是的话代表有数据，不是的话则筛选时间没有数据
                        if self.is_time_range_contained(start_time,end_time,bill_start,bill_end):
                            print('[存在账单数据]',bill_data)
                            is_data = True

                            # 获取生成表格参数
                            sellerId = dataSource.get('action', {}).get('exportOptions')[0].get('bizParam',{}).get('sellerId')
                            print('[sellerId]',sellerId)

                            fileName = dataSource.get('action', {}).get('exportOptions')[0].get('bizParam',{}).get('statementNumber')
                            print('[fileName]',fileName)

                            billCycle = int(''.join(fileName.split('-')[1:]).strip())
                            print('[billCycle]',billCycle)

                            print('【开始创建表格】')
                            self.create_file(driver, fileName, billCycle, site,sellerId)

                            print('【下载表格】')
                            # 获取excel链接
                            excel_url = self.download_file(driver,site)
                            print('[excel表格链接]',excel_url)

                            # 获取cookie，用于excel_url请求
                            cookies = driver.get_cookies()
                            if not cookies:raise ValueError('获取cookie失败')
                            cookies = {d['name']: d['value'] for d in cookies if site_map in d['domain']}
                            print('[cookie]', cookies)
                            # 请求excel链接，返回表格json数据
                            dataXlsx = request.downloadExcel(excel_url,{"cookies": cookies})
                            if not dataXlsx:
                                raise ValueError('表格下载失败')
                            print('[表格json数据]',dataXlsx)

                            # 拆分保存，1页2500条
                            print('【拆分保存，1页2500条】')

                            # 提取所有数据
                            value_list = dataXlsx['Income Overview']
                            # 总数据量
                            total_count = len(value_list)
                            # 设置每批次的条数,相当于设置每页2500条数据
                            page_size = 2500
                            # 页数
                            page_number = 1
                            # 循环切割列表直到处理完所有数据
                            while value_list:
                                # 每次取出前page_size个元素
                                batch_value = value_list[:page_size]
                                # 当前页面数据量
                                list_count = len(batch_value)

                                # 保存数据
                                options['request_id'] = str(uuid.uuid4())
                                options['page_number'] = page_number  # 页码
                                options['page_size'] = page_size  # 页数
                                options['list_count'] = list_count  # 列表数据
                                options['total_count'] = total_count  # 总数据
                                options['response'] = json.dumps({'Income Overview':batch_value},ensure_ascii=False)
                                print('[options]',options)
                                taskRequest.save(options)

                                # 更新原始列表，移除已处理的部分
                                value_list = value_list[page_size:]
                                # 翻页
                                page_number += 1
                            break

                        else:
                            print('【未找得到满足筛选日期的账单，返回空】')
                    else:
                        print('【没有账单数据，返回空】')
            else:
                print('【没有账单数据，返回空】')
            if not is_data:
                # 没有账单数据，返回空
                # 保存数据
                options['request_id'] = str(uuid.uuid4())
                options['page_number'] = 1  # 页码
                options['page_size'] = 2500  # 页数
                options['list_count'] = 0  # 列表数据
                options['total_count'] = 0  # 总数据
                options['response'] = '[]'
                taskRequest.save(options)
        except Exception as e:
            raise ValueError('【账单】获取失败', str(e), resp)

    def parse_date(self,date_str):
        # 分割原始字符串（处理多余空格）
        parts = date_str.split(' ')

        day = parts[0]
        month = parts[1]
        year = parts[2]

        # 构建可解析的日期字符串（格式：月 日, 年）
        date_string = f"{month} {day}, {year}"

        # 解析日期（匹配缩写月份如 May/Jun/Jul）
        return datetime.strptime(date_string, '%b %d, %Y').strftime("%Y-%m-%d")

    def is_time_range_contained(self,start_time, end_time, start_time1, end_time1):
        """
        筛选时间 [start_time, end_time]
        账期时间 [start_time1, end_time1]
        """
        # 确保所有日期都是 datetime 对象（如果是字符串则先转换）
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, '%Y-%m-%d')
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, '%Y-%m-%d')
        if isinstance(start_time1, str):
            start_time1 = datetime.strptime(start_time1, '%Y-%m-%d')
        if isinstance(end_time1, str):
            end_time1 = datetime.strptime(end_time1, '%Y-%m-%d')

        # 判断 start_time 和 end_time 是否有时间在 start_time1 和 end_time1 之间
        return not (end_time1 < start_time or start_time1 > end_time)

    def create_file(self,driver, fileName, billCycle, site, sellerId):
        # 创建表格
        load_data = {
            "_timezone": -8,
            "businessAction": "income_overview_export",
            "businessCode": f"LAZADA_{site}_finance_viewconvert_statement3",
            "fileType": "XLSX",
            "taskType": "CustomizeExport",
            "bizParam": json.dumps({
                "sellerId": sellerId,
                "exportPageType": "STATEMENT",
                "tag": "MP2",
                "billCycle": billCycle,
                "statementNumber": fileName,
            }),
            "fileStoreType": 4
        }
        # 接口api
        api = 'mtop.lazada.finance.sellerfund3.create.download.task'
        # 发送请求
        resp = lazadaService.get_api_response(driver, load_data, site, api)
        if json.loads(resp).get('data', {}).get('succeeded'):
            print('【表格创建成功】')
        else:
            raise ValueError('表格创建失败')

    def download_file(self,driver, site):
        # 下载表格
        load_data = {"_timezone":-8,"pageSize":10,"current":1,"channel":"statement"}
        count = 0
        while count != 20:
            # 接口api
            api = 'mtop.lazada.finance.sellerfund3.query.download.task'
            # 发送请求
            resp = lazadaService.get_api_response(driver, load_data, site, api)
            data = json.loads(resp).get('data', {}).get('data', {})
            fileLinkList = data.get('dataSource')[0].get('fileLinkList')
            if len(fileLinkList) < 1:
                print('[表格下载中，请稍等]')
                time.sleep(6)
                count += 1
                if count == 19:raise ValueError('表格文件较大，下载时间超过2分钟，请延长下载时间！！！')
            else:
                print('【表格下载完成】')
                return fileLinkList[0]['value']
