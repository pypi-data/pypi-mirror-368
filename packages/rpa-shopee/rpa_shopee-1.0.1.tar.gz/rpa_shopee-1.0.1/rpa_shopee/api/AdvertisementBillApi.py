import json
import time
import random
import uuid
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse
from undetected_chromedriver import Chrome as unChrome

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from rpa_common import Common   # 公共库
from rpa_common import Env   # 环境配置
from rpa_common.library.Request import Request   # requests请求
from rpa_common.request import ShopRequest   # 店铺信息获取并操作
from rpa_common.service.EmailService import EmailService   # 邮箱操作
from rpa_common.service.ExecuteService import ExecuteService  # 请求
from rpa_common.exceptions import *
from rpa_common.request.TaskRequest import TaskRequest  # 任务数据保存

from rpa_shopee.api.ShopApi import ShopApi   # shopee店铺信息获取

env = Env()
request = Request()
common = Common()
executeService = ExecuteService()
taskRequest = TaskRequest()
shopRequest = ShopRequest()
emailService = EmailService()
shopApi = ShopApi()


class AdvertisementBillApi():
    def __init__(self):
        super().__init__()
        self.host = env.get()['api']

    def getAdsBill(self, driver: unChrome, options):
        """
        @Desc     : 获取广告费账单（非本土）
        @Author   : 祁国庆
        @Time     : 2025/07/23 17:54:31
        """
        print('——————————————【shopee获取广告费账单 非本土】')
        print('options', options)
        start_time = options.get('start_time', '')  # 开始时间 格式 2025-04-03
        end_time = options.get('end_time', '')  # 结束时间  格式 2025-04-03
        merchant_id = str(options.get('merchant_id', ''))  # 公司id (非shop_id)
        shop_id = str(options.get('shop_id', ''))  # 店铺id (shop_id)

        # 参数检测
        shopApi.TaskParamsException('非本土获取广告费账单', start_time, end_time, merchant_id, shop_id)

        if merchant_id != '0':  # 为0，则不用切换店铺
            # 切换店铺并返回当前店铺的信息 这个需要merchant_id,shop_id值
            shop_at = shopApi.switch_store(driver, options)
            common.print_('shop_at', shop_at)

        if shopApi.getShopOrHaveHoliday(driver=driver, options=options):
            raise UnknownException('店铺已休假，无法获取广告费账单')

        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json;charset=UTF-8",
        }
        url = f"https://seller.shopee.cn/api/pas/v1/transaction_history/get_csv/"
        timestamp = common.lambda_set()['date_to_timestamp_fill']
        data = {
            "start_time": timestamp(start_time, 1, 60 * 60 * 1),  # 10位时间戳 01:00:00
            "end_time": timestamp(end_time, 1, 86399 + 60 * 60 * 1),  # 10位时间戳 00:59:59
            "transaction_type_list": [],
            "new_transaction_log_flag": True
        }
        res = executeService.request(driver=driver, headers=headers, url=url, data=data, method="POST")
        res = json.loads(res)
        common.print_('请求返回信息', res)
        data = (res.get('data', {}) or {}).get('content', '')
        common.print_('提取的表格数据', data)
        data_handle = [_.strip() for _ in data.split('\n') if _.strip()]
        if not len(data_handle) >= 7:
            return common.back(status=1, message='没有数据')
        currency = ''
        title = []
        data_list = []
        for idx, text in enumerate(data_handle):
            if '货币' in text:
                common.print_('货币', text.split(','))
                currency = text.split(',')[1]
            elif idx == 5:
                # 标题
                title = text.split(',')
                common.print_('标题', title)
            elif idx >= 6:
                # 数据
                data = text.split(',')
                # 将 01/01/2025 转为 2025-01-01
                data[1] = data[1].replace('/','-')
                # data[1] = datetime.strptime(data[1], '%Y/%m/%d').strftime('%Y-%m-%d')
                common.print_('数据', data)
                data_list += [{**{a: b for a, b in zip(title, data)}, **{'currency': currency}}]

        request_id = str(uuid.uuid4())

        # 保存数据
        options['request_id'] = request_id
        options['response'] = json.dumps(data_list, ensure_ascii=False, separators=(',', ':'))
        taskRequest.save(options)

    def getAdsRechargeBill(self, driver: unChrome, options):
        """
        @Desc     : 获取广告充值记录账单（非本土）
        @Author   : 祁国庆
        @Time     : 2025/07/23 17:54:31
        """
        print('——————————————【shopee获取广告充值记录账单 非本土】')
        print('options', options)
        merchant_id = str(options.get('merchant_id', ''))  # 公司id (非shop_id)
        shop_id = str(options.get('shop_id', ''))  # 店铺id (shop_id)

        # 参数检测
        shopApi.TaskParamsException('非本土获取广告充值记录账单', merchant_id, shop_id)

        if merchant_id != '0':  # 为0，则不用切换店铺
            # 切换店铺并返回当前店铺的信息 这个需要merchant_id,shop_id值
            shop_at = shopApi.switch_store(driver, options)
            common.print_('shop_at', shop_at)

        if shopApi.getShopOrHaveHoliday(driver=driver, options=options):
            raise UnknownException('店铺已休假，无法获取广告充值记录账单')

        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "fil,fil-PH;q=0.9",
            "referer": f"https://seller.shopee.cn/portal/value-add/ads/order/list/all?supplierId=1",
        }
        params = {
            "SPC_CDS": "-",
            "SPC_CDS_VER": 2,
            "page_size": 100,
            "page_number": 1,
            "biz_id": 1
        }
        url = "https://seller.shopee.cn/api/valueadded/v1/get_order_list/"
        res = executeService.request(driver=driver, headers=headers, url=url, params=params, method="GET")
        res = json.loads(res)
        common.print_('SPC_CDS|请求返回信息', res)
        SPC_CDS = (re.findall('cookie_token=(.*?)$', res['message']) + [''])[0]
        params['SPC_CDS'] = SPC_CDS

        while True:
            res = executeService.request(driver=driver, headers=headers, url=url, params=params, method="GET")
            res_loads = json.loads(res)
            common.print_('请求返回信息', res_loads)

            data = res_loads['data']['list']
            if not data:
                return common.back(status=1, message='没有数据')

            request_id = str(uuid.uuid4())
            # 保存数据
            options['request_id'] = request_id
            options['page_number'] = params['page_number']  # 页码
            options['page_size'] = params['page_size']  # 每页数量
            options['list_count'] = len(data)  # 当前数据列表数据长度
            options['total_count'] = res_loads['data']['page_info']['total']  # 总数据量
            options['response'] = res
            taskRequest.save(options)

            params['page_number'] += 1

            time.sleep(random.uniform(1, 3))



