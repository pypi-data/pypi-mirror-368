import json
from rpa_common import Common
from rpa_lazada.api.PromoApi import PromoApi
from rpa_lazada.service.LazadaService import LazadaService

common = Common()
promoApi = PromoApi()
lazadaService = LazadaService()

class PromoService():
    def __init__(self):
        super().__init__()

    def getPromo(self, driver, shop_data, options):
        '''
        @Desc    : 获取促销费
        @Author  : 洪润涛
        @Time    : 2024/07/21 09:50:13
        '''
        # 获取促销费
        promoApi.shop_promo(driver, options)
