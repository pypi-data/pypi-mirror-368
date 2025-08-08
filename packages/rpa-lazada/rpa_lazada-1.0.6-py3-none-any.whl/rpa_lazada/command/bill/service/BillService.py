from rpa_common import Common
from rpa_lazada.api.PaymentBillApi import PaymentBillApi
from rpa_lazada.api.BillApi import BillApi
from rpa_common.library import Chrome
from rpa_common.request import ShopRequest
from rpa_lazada.service.LazadaService import LazadaService
from rpa_common.request import TaskRequest

common = Common()
chrome = Chrome()
paymentbillApi = PaymentBillApi()
billApi = BillApi()
shopRequest = ShopRequest()
lazadaService = LazadaService()
taskRequest = TaskRequest()

class BillService():
    def __init__(self):
        super().__init__()

    def getPaymentBillDetail(self, driver, shop_data, options):
        '''
        @Desc    : 获取打款账单
        @Author  : 洪润涛
        @Time    : 2024/07/15 14:20:33
        '''
        # 获取打款账单
        paymentbillApi.payment_bill(driver, options)

    def getBillDetail(self, driver, shop_data, options):
        '''
        @Desc    : 获取账单
        @Author  : 洪润涛
        @Time    : 2024/07/24 17:04:25
        '''
        # 获取账单
        billApi.bill(driver, options)
