from rpa_common import Common
from rpa_lazada.api.EarnestAmountApi import EarnestAmountApi
from rpa_lazada.api.IncomeSummaryApi import IncomeSummaryApi
from rpa_lazada.api.ReadyGrantApi import ReadyGrantApi
from rpa_lazada.api.WalletBalanceApi import WalletBalanceApi
from rpa_lazada.service.LazadaService import LazadaService

common = Common()
earnestAmountApi = EarnestAmountApi()
incomeSummaryApi = IncomeSummaryApi()
readyGrantApi = ReadyGrantApi()
walletBalanceApi = WalletBalanceApi()
lazadaService = LazadaService()

class AmountService():
    def __init__(self):
        super().__init__()

    def getEarnestAmount(self, driver, shop_data, options):
        '''
        @Desc    : 获取资金申报-保证金（只有非本土才有）
        @Author  : 洪润涛
        @Time    : 2024/07/24 11:50:37
        '''
        # 获取资金申报-保证金
        earnestAmountApi.earnest_amount(driver, options)

    def getIncomeSummary(self, driver, shop_data, options):
        '''
        @Desc    : 获取资金申报-收入概括（本土、非本土都有）
        @Author  : 洪润涛
        @Time    : 2024/07/24 11:58:22
        '''
        # 获取资金申报-收入概括
        incomeSummaryApi.income_summary(driver, options)

    def getReadyGrant(self, driver, shop_data, options):
        '''
        @Desc    : 获取资金申报--准备发放账单（本土、非本土都有）
        @Author  : 洪润涛
        @Time    : 2024/07/24 13:36:46
        '''
        # 获取资金申报-准备发放账单
        readyGrantApi.ready_grant(driver, options)

    def getWalletBalance(self, driver, shop_data, options):
        '''
        @Desc    : 获取资金申报--钱包余额（本土、非本土都有）
        @Author  : 洪润涛
        @Time    : 2024/07/24 14:02:15
        '''
        # 获取资金申报-准备钱包余额
        walletBalanceApi.wallet_balance(driver, options)