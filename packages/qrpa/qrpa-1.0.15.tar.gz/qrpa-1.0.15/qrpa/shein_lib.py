from qrpa import read_dict_from_file, write_dict_to_file, read_dict_from_file_ex, write_dict_to_file_ex
from qrpa import log, fetch, send_exception, md5_string
from qrpa import time_utils, get_safe_value

import math
import time
import json
from datetime import datetime
from playwright.sync_api import Page

class SheinLib:

    def __init__(self, config, bridge, web_page: Page, store_username, store_name):
        self.config = config
        self.bridge = bridge
        self.store_username = store_username
        self.store_name = store_name
        self.web_page = web_page
        self.dt = None

        self.deal_auth()

    # 处理鉴权
    def deal_auth(self):
        web_page = self.web_page
        while not web_page.locator('//div[contains(text(),"商家后台")]').nth(1).is_visible():
            if web_page.locator('xpath=//div[@id="container" and @alita-name="gmpsso"]//button[@type="button" and @id]').nth(0).is_visible():
                web_page.locator('xpath=//div[@id="container" and @alita-name="gmpsso"]//button[@type="button" and @id]').nth(0).click()
                log("鉴权确定按钮可见 点击'确定'按钮")
                web_page.wait_for_load_state("load")
                web_page.wait_for_timeout(1000)
                # time.sleep(1)
            if web_page.locator('//input[@name="username"]').is_visible():
                log("用户名输入框可见 等待5秒点击'登录'按钮")
                web_page.wait_for_timeout(5000)
                log('点击"登录"')
                web_page.locator('//button[contains(@class,"login_btn")]').click()
                web_page.wait_for_load_state("load")
                log('再延时5秒')
                web_page.wait_for_timeout(5000)
            if web_page.locator('//span[contains(text(),"商品管理")]').nth(1).is_visible():
                log('商品管理菜单可见 退出鉴权处理')
                return
            log('商家后台不可见', web_page.title(), web_page.url)
            web_page.wait_for_load_state("load")
            # time.sleep(1)
            web_page.wait_for_timeout(1000)
            if 'SHEIN全球商家中心' in web_page.title() and 'https://sso.geiwohuo.com/#/home' in web_page.url:
                log('SHEIN全球商家中心 中断循环')
                break
            if '后台首页' in web_page.title() and 'https://sso.geiwohuo.com/#/home' in web_page.url:
                log('后台首页 中断循环')
                break
            if '商家后台' in web_page.title() and 'https://sso.geiwohuo.com/#/home' in web_page.url:
                log('后台首页 中断循环')
                break
            if 'mrs.biz.sheincorp.cn' in web_page.url and '商家后台' in web_page.title():
                web_page.goto('https://sso.geiwohuo.com/#/home')
                web_page.wait_for_load_state("load")
                web_page.wait_for_timeout(3000)
                # time.sleep(3)
            if web_page.locator('//h1[contains(text(),"鉴权")]').is_visible():
                log('检测到鉴权 刷新页面')
                web_page.reload()
                web_page.wait_for_load_state('load')
                # time.sleep(3)
                web_page.wait_for_timeout(3000)
                web_page.reload()
                # time.sleep(3)
                web_page.wait_for_timeout(3000)
            if web_page.title() == 'SHEIN':
                web_page.goto('https://sso.geiwohuo.com/#/home')
                web_page.wait_for_load_state("load")
                # time.sleep(3)
                web_page.wait_for_timeout(3000)

            # web_page.goto('https://sso.geiwohuo.com')
        log('鉴权处理结束')

    def get_product_list(self):
        self.web_page.goto('https://sso.geiwohuo.com/#/spmp/commdities/list')
        self.web_page.wait_for_load_state("load")

        cache_file = f'{self.config.auto_dir}/shein/dict/product_list_{self.store_username}.json'
        DictSpuInfo = read_dict_from_file(cache_file, 3600)
        if len(DictSpuInfo) > 0:
            return DictSpuInfo

        page_num = 1
        page_size = 100

        url = f"https://sso.geiwohuo.com/spmp-api-prefix/spmp/product/list?page_num={page_num}&page_size={page_size}"
        payload = {
            "language"              : "zh-cn",
            "only_recommend_resell" : False,
            "only_spmb_copy_product": False,
            "search_abandon_product": False,
            "sort_type"             : 1
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))

        spu_list = response_text['info']['data']
        total = response_text['info']['meta']['count']
        totalPage = math.ceil(total / page_size)

        for page_num in range(2, totalPage + 1):
            log(f'获取商品列表 第{page_num}/{totalPage}页')
            url = f"https://sso.geiwohuo.com/spmp-api-prefix/spmp/product/list?page_num={page_num}&page_size={page_size}"
            response_text = fetch(self.web_page, url, payload)
            spu_list_new = response_text['info']['data']
            spu_list += spu_list_new
            time.sleep(0.3)

        DictSkcShelf = {}
        DictSkcProduct = {}
        DictSpuInfo = {}
        for spu_item in spu_list:
            spu = spu_item['spu_name']
            first_shelf_time = spu_item['first_shelf_time']
            for skc_item in spu_item['skc_info_list']:
                skc_name = skc_item['skc_name']
                DictSkcShelf[skc_name] = first_shelf_time
                DictSkcProduct[skc_name] = spu_item
            DictSpuInfo[spu] = spu_item

        cache_file2 = f'{self.config.auto_dir}/shein/dict/skc_shelf_{self.store_username}.json'
        write_dict_to_file(cache_file2, DictSkcShelf)
        cache_file3 = f'{self.config.auto_dir}/dict/skc_product_{self.store_username}.json'
        write_dict_to_file(cache_file3, DictSkcProduct)

        write_dict_to_file(cache_file, DictSpuInfo)
        return DictSpuInfo

    def query_obm_activity_list(self):
        page_num = 1
        page_size = 100
        date_60_days_ago = time_utils.get_past_nth_day(59)
        cache_file = f'{self.config.auto_dir}/shein/cache/obm_activity_{self.store_name}_{date_60_days_ago}_{time_utils.today_date()}.json'
        list_item = read_dict_from_file(cache_file, 3600 * 8)
        if len(list_item) > 0:
            return list_item

        url = f"https://sso.geiwohuo.com/mrs-api-prefix/promotion/obm/query_obm_activity_list"
        payload = {
            "insert_end_time"  : f"{time_utils.today_date()} 23:59:59",
            "insert_start_time": f"{date_60_days_ago} 00:00:00",
            "page_num"         : page_num,
            "page_size"        : page_size,
            "system"           : "mrs",
            "time_zone"        : "Asia/Shanghai",
            # "state": 3, # 活动开启中 不能用这个条件
            "type_id"          : 31  # 限时折扣
        }

        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))

        list_item = response_text['info']['data']
        total = response_text['info']['meta']['count']
        totalPage = math.ceil(total / page_size)

        for page in range(2, totalPage + 1):
            log(f'获取营销工具列表 第{page}/{totalPage}页')
            payload["page_num"] = page
            response_text = fetch(self.web_page, url, payload)
            list_item += response_text['info']['data']
            time.sleep(0.1)

        write_dict_to_file(cache_file, list_item)
        return list_item

    def query_goods_detail(self, activity_id):
        # web_page.goto(f'https://sso.geiwohuo.com/#/mrs/tools/activity/obm-time-limit-info/{activity_id}')
        # web_page.wait_for_load_state('load')
        log(f'正在获取 {self.store_name} {activity_id} 营销工具商品详情')

        cache_file = f'{self.config.auto_dir}/shein/cache/query_goods_detail_{activity_id}.json'
        list_item = read_dict_from_file(cache_file, 3600 * 8)
        if len(list_item) > 0:
            return list_item

        page_num = 1
        page_size = 100
        url = "https://sso.geiwohuo.com/mrs-api-prefix/promotion/simple_platform/query_goods_detail"
        payload = {
            "activity_id": activity_id,
            "page_num"   : page_num,
            "page_size"  : page_size
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        list_item = response_text['info']['data']
        total = response_text['info']['meta']['count']
        totalPage = math.ceil(total / page_size)

        for page in range(2, totalPage + 1):
            log(f'获取营销工具商品列表 第{page}/{totalPage}页')
            payload["page_num"] = page
            response_text = fetch(self.web_page, url, payload)
            list_item += response_text['info']['data']
            time.sleep(0.1)

        write_dict_to_file(cache_file, list_item)
        return list_item

    def get_partake_activity_goods_list(self):
        # self.web_page.goto(f'https://sso.geiwohuo.com/#/mbrs/marketing/list/1')
        # self.web_page.wait_for_load_state('load')
        log(f'正在获取 {self.store_name} 活动列表')
        page_num = 1
        page_size = 100
        date_60_days_ago = time_utils.get_past_nth_day(59)
        cache_file = f'{self.config.auto_dir}/shein/cache/platform_activity_{self.store_name}_{date_60_days_ago}_{time_utils.today_date()}.json'
        list_item = read_dict_from_file(cache_file, 3600 * 8)
        if len(list_item) > 0:
            return list_item

        url = f"https://sso.geiwohuo.com/mrs-api-prefix/mbrs/activity/get_partake_activity_goods_list?page_num={page_num}&page_size={page_size}"
        payload = {
            "goods_audit_status"    : 1,
            "insert_zone_time_end"  : f"{time_utils.today_date()} 23:59:59",
            "insert_zone_time_start": f"{date_60_days_ago} 00:00:00"
        }

        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        list_item = response_text['info']['data']
        total = response_text['info']['meta']['count']
        totalPage = math.ceil(total / page_size)

        for page in range(2, totalPage + 1):
            log(f'获取活动列表 第{page}/{totalPage}页')
            payload["page_num"] = page
            response_text = fetch(self.web_page, url, payload)
            list_item += response_text['info']['data']
            time.sleep(0.1)

        write_dict_to_file(cache_file, list_item)
        return list_item

    def generate_activity_price_dict(self):
        cache_file = f'{self.config.auto_dir}/shein/dict/activity_price_{self.store_name}.json'
        dict_activity_price = {}
        activity_list = self.query_obm_activity_list()
        for activity in activity_list:
            activity_id = activity['activity_id']
            activity_name = activity['act_name']
            sub_type_id = activity['sub_type_id']  # 1.不限量 2.限量
            dateBegin = time_utils.convert_datetime_to_date(activity['start_time'])
            dateEnd = time_utils.convert_datetime_to_date(activity['end_time'])
            skc_list = self.query_goods_detail(activity_id)
            for skc_item in skc_list:
                attend_num_sum = skc_item['attend_num_sum']
                product_act_price = skc_item['product_act_price']  # 活动价
                if sub_type_id == 1:
                    attend_num_sum = '不限量'
                for sku_item in skc_item['sku_info_list']:
                    sku = sku_item['sku']  # 平台sku
                    product_act_price = sku_item['product_act_price'] if sku_item[
                        'product_act_price'] else product_act_price  # 活动价
                    key = f'{sku}_{dateBegin}_{dateEnd}_{activity_name}'
                    dict_activity_price[key] = [product_act_price, attend_num_sum]

        platform_activity_list = self.get_partake_activity_goods_list()
        for platform_activity in platform_activity_list:
            activity_name = platform_activity['activity_name']
            text_tag_content = platform_activity['text_tag_content']
            attend_num = platform_activity['attend_num']
            dateBegin = time_utils.convert_timestamp_to_date(platform_activity['start_time'])
            dateEnd = time_utils.convert_timestamp_to_date(platform_activity['end_time'])
            if text_tag_content != '新品':
                attend_num = '-'
            for sku_item in platform_activity['activity_sku_list']:
                sku = sku_item['sku_code']
                enroll_price = sku_item['enroll_display_str'][:-3]
                key = f'{sku}_{dateBegin}_{dateEnd}_{activity_name}'
                dict_activity_price[key] = [enroll_price, attend_num]

        write_dict_to_file(cache_file, dict_activity_price)

    def get_skc_week_actual_sales(self, skc):
        first_day, last_day = time_utils.TimeUtils.get_past_7_days_range()
        cache_file = f'{self.config.auto_dir}/shein/cache/{skc}_{first_day}_{last_day}.json'
        if datetime.now().hour >= 9:
            DictSkuSalesDate = read_dict_from_file(cache_file)
        else:
            DictSkuSalesDate = read_dict_from_file(cache_file, 1800)
        if len(DictSkuSalesDate) > 0:
            return DictSkuSalesDate

        url = f"https://sso.geiwohuo.com/idms/sale-trend/detail"
        payload = {
            "skc"      : skc,
            "startDate": first_day,
            "endDate"  : last_day,
            "daysToAdd": 0
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            log(response_text)
            return {}
        list_item = response_text['info']['salesVolumeDateVoList']
        for item in list_item:
            key = item['date']
            DictSkuSalesDate[key] = item['salesVolumeMap']
        list_item2 = response_text['info']['actualSalesVolumeMap']
        for item in list_item2:
            sku = item['skuCode']
            if sku is not None:
                DictSkuSalesDate[sku] = item['actualSalesVolume']

        write_dict_to_file(cache_file, DictSkuSalesDate)
        return DictSkuSalesDate

    def get_preemption_list(self, skc_list):
        url = f"https://sso.geiwohuo.com/idms/goods-skc/preemption-num"
        payload = skc_list
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))

        dict = response_text['info']

        cache_file = f'{self.config.auto_dir}/shein/preemption_num/preemption_num_{self.store_username}.json'
        dict_preemption_num = read_dict_from_file(cache_file)
        dict_preemption_num.update(dict)
        write_dict_to_file(cache_file, dict_preemption_num)

        return dict

    def get_activity_label(self, skc_list):
        url = f"https://sso.geiwohuo.com/idms/goods-skc/activity-label"
        payload = skc_list
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        dict = response_text['info']

        cache_file = f'{self.config.auto_dir}/shein/activity_label/activity_label_{self.store_username}.json'
        dict_label = read_dict_from_file(cache_file)
        dict_label.update(dict)
        write_dict_to_file(cache_file, dict_label)

        return dict

    def get_sku_price_v2(self, skc_list):
        log(f'获取sku价格列表', skc_list)
        url = "https://sso.geiwohuo.com/idms/goods-skc/price"
        response_text = fetch(self.web_page, url, skc_list)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        dict = response_text['info']

        cache_file = f'{self.config.auto_dir}/shein/sku_price/sku_price_{self.store_username}.json'
        dict_sku_price = read_dict_from_file(cache_file)
        dict_sku_price.update(dict)
        write_dict_to_file(cache_file, dict_sku_price)

        return dict

    def get_stock_advice(self, skc_list):
        log(f'获取sku库存建议列表', skc_list)
        url = f"https://sso.geiwohuo.com/idms/goods-skc/get-vmi-spot-advice"
        payload = skc_list
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        dict = response_text['info']

        cache_file = f'{self.config.auto_dir}/shein/vmi_spot_advice/spot_advice_{self.store_username}.json'
        dict_advice = read_dict_from_file(cache_file)
        dict_advice.update(dict)
        write_dict_to_file(cache_file, dict_advice)

        return dict

    def get_dt_time(self):
        if self.dt is not None:
            log(f'字典dt: {self.dt}')
            return self.dt
        log('获取非实时更新时间')
        url = "https://sso.geiwohuo.com/sbn/common/get_update_time"
        payload = {
            "pageCode": "Index",
            "areaCd"  : "cn"
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))
        self.dt = response_text.get('info').get('dt')
        log(f'dt: {self.dt}')
        return self.dt

    # 获取一个skc一周内的销售趋势（商品明细中的）
    def get_dict_skc_week_trend_v2(self, spu, skc):
        dt = self.get_dt_time()

        date_7_days_ago = time_utils.TimeUtils.get_past_nth_day(7, None, '%Y%m%d')
        log('-7', date_7_days_ago)
        date_1_days_ago = time_utils.TimeUtils.get_past_nth_day(1, None, '%Y%m%d')
        log('-1', date_1_days_ago)

        cache_file = f'{self.config.auto_dir}/shein/dict/dict_skc_week_trend_{skc}_{date_7_days_ago}_{date_1_days_ago}.json'
        if datetime.now().hour >= 9:
            DictSkc = read_dict_from_file(cache_file)
        else:
            DictSkc = read_dict_from_file(cache_file, 1800)
        if len(DictSkc) > 0:
            return DictSkc

        url = f"https://sso.geiwohuo.com/sbn/new_goods/get_skc_diagnose_trend"
        payload = {
            "areaCd"     : "cn",
            "countrySite": [
                "shein-all"
            ],
            "dt"         : dt,
            "endDate"    : date_1_days_ago,
            "spu"        : [spu],
            "skc"        : [skc],
            "startDate"  : date_7_days_ago,
        }
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))

        data_list = response_text['info']
        DictSkc = {}
        for date_item in data_list:
            dataDate = date_item['dataDate']
            # epsUvIdx = date_item['epsUvIdx']
            # saleCnt = date_item['saleCnt']
            DictSkc[dataDate] = date_item

        log('len(DictSkc)', len(DictSkc))
        write_dict_to_file(cache_file, DictSkc)
        return DictSkc

    def get_skc_week_sale_list(self, spu, skc, sku):
        dict_skc = self.get_dict_skc_week_trend_v2(spu, skc)
        date_list = time_utils.get_past_7_days_list()
        first_day, last_day = time_utils.TimeUtils.get_past_7_days_range()
        cache_file = f'{self.config.auto_dir}/shein/cache/{skc}_{first_day}_{last_day}.json'
        DictSkuSalesDate = read_dict_from_file(cache_file)
        sales_detail = []
        for date in date_list:
            sales_num = DictSkuSalesDate.get(date, {}).get(sku, {}).get("hisActualValue", 0)
            sales_num = sales_num if sales_num is not None else 0

            saleCnt = get_safe_value(dict_skc.get(date, {}), 'saleCnt', 0)
            epsUvIdx = get_safe_value(dict_skc.get(date, {}), 'epsUvIdx', 0)

            sales_detail.append(f'{date}({time_utils.get_weekday_name(date)}): {sales_num}/{saleCnt}/{epsUvIdx}')

        sales_data = []
        for date in date_list:
            goodsUvIdx = get_safe_value(dict_skc.get(date, {}), 'goodsUvIdx', 0)  # 商详访客
            epsGdsCtrIdx = get_safe_value(dict_skc.get(date, {}), 'epsGdsCtrIdx', 0)  # 点击率

            payUvIdx = get_safe_value(dict_skc.get(date, {}), 'payUvIdx', 0)  # 支付人数
            gdsPayCtrIdx = get_safe_value(dict_skc.get(date, {}), 'gdsPayCtrIdx', 0)  # 转化率

            sales_data.append(f'{date}({time_utils.get_weekday_name(date)}): {epsGdsCtrIdx:.2%}({goodsUvIdx})/{gdsPayCtrIdx:.2%}({payUvIdx})')

        return sales_detail, sales_data

    def get_activity_price(self, activity_dict, sku, activity_name, dateBegin, dateEnd):
        key = f'{sku}_{dateBegin}_{dateEnd}_{activity_name}'
        price_info = activity_dict.get(key, ['-', '-'])
        return f'活动价:¥{price_info[0]}, 活动库存:{price_info[1]}'

    def get_skc_activity_label(self, skc, sku, dict_activity_price=None):
        cache_file = f'{self.config.auto_dir}/shein/activity_label/activity_label_{self.store_username}.json'
        dict_label = read_dict_from_file(cache_file)
        operateLabelList = dict_label[skc]['operateLabelList']
        activityList = []
        activityList2 = []
        for item in operateLabelList:
            if item['name'] == '活动中':
                activityList.extend(item.get('activityList', []))
            if item['name'] == '即将开始':
                activityList2.extend(item.get('activityList', []))

        if activityList:
            activityLabel = '\n'.join([
                f'  [{act["date"]}]\n【{self.get_activity_price(dict_activity_price, sku, act["name"], act["dateBegin"], act["dateEnd"])}】{act["name"]}\n'
                for act in activityList])
        else:
            activityLabel = '无'
        if activityList2:
            activityLabel2 = '\n'.join([
                f'  [{act["date"]}]\n【{self.get_activity_price(dict_activity_price, sku, act["name"], act["dateBegin"], act["dateEnd"])}】{act["name"]}\n'
                for act in activityList2])
        else:
            activityLabel2 = '无'
        return f'活动中:\n{activityLabel}\n即将开始:\n{activityLabel2}'

    # 获取商品包含sku销量的列表
    # mode = 1.备货建议 2.已上架 3.昨日上架 4.昨日出单
    # 5.采购-缺货要补货      (有现货建议 建议采购为正 有销量)
    # 6.运营采购-滞销清库存   (无现货建议 建议采购为负 30天外 无销量)
    # 7.运营-新品上架需要优化 (无现货建议 建议采购为负 上架15天内)
    # 8.运营-潜在滞销款      (无现货建议 30天外 有销量)
    # 9.运营-潜力热销款      (有现货建议 30天内 有销量)
    # 10.运营-热销款         (有现货建议 30天外 有销量)
    def get_bak_advice(self, mode=1, skcs=None, source='mb'):
        log(f'获取备货信息商品列表 做成字典')
        global DictSkuInfo
        if skcs == None or len(skcs) == 0:
            # if mode == 3:
            #     skcs = "sh2405133614611175"  # 这是一个不存在的skc
            # else:
            skcs = ""
        else:
            skcs = ",".join(skcs)

        url = "https://sso.geiwohuo.com/idms/goods-skc/list"
        pageNumber = 1
        pageSize = 100
        dictPayload = {
            "pageNumber"            : pageNumber,
            "pageSize"              : pageSize,
            "supplierCodes"         : "",
            "skcs"                  : skcs,
            "spu"                   : "",
            "c7dSaleCntBegin"       : "",
            "c7dSaleCntEnd"         : "",
            "goodsLevelIdList"      : [10, 107, 61, 90, 87, 237, 220, 219, 88, 75, 62, 227, 12, 230, 80, 58, 224, 97],
            "supplyStatus"          : "",
            "shelfStatus"           : "",
            "categoryIdList"        : [],
            "skcStockBegin"         : "",
            "skcStockEnd"           : "",
            "skuStockBegin"         : "",
            "skuStockEnd"           : "",
            "skcSaleDaysBegin"      : "",
            "skcSaleDaysEnd"        : "",
            "skuSaleDaysBegin"      : "",
            "skuSaleDaysEnd"        : "",
            "planUrgentCountBegin"  : "",
            "planUrgentCountEnd"    : "",
            "skcAvailableOrderBegin": "",
            "skcAvailableOrderEnd"  : "",
            "skuAvailableOrderBegin": "",
            "skuAvailableOrderEnd"  : "",
            "shelfDateBegin"        : "",
            "shelfDateEnd"          : "",
            "stockWarnStatusList"   : [],
            "labelFakeIdList"       : [],
            "sheinSaleByInventory"  : "",
            "tspIdList"             : [],
            "adviceStatus"          : [],
            "sortBy7dSaleCnt"       : 2,
            "goodsLevelFakeIdList"  : [1, 2, 3, 8, 14, 15, 4, 11]
        }
        payload = dictPayload
        response_text = fetch(self.web_page, url, payload)
        error_code = response_text.get('code')
        if str(error_code) != '0':
            raise send_exception(json.dumps(response_text, ensure_ascii=False))

        spu_list = response_text['info']['list']

        skc_list = [item['skc'] for item in spu_list]
        self.get_activity_label(skc_list)
        self.get_preemption_list(skc_list)
        self.get_sku_price_v2(skc_list)
        self.get_stock_advice(skc_list)

        total = response_text['info']['count']
        totalPage = math.ceil(total / pageSize)
        for page in range(2, totalPage + 1):
            log(f'获取备货信息商品列表 第{page}/{totalPage}页')
            dictPayload['pageNumber'] = page
            payload = dictPayload
            response_text = fetch(self.web_page, url, payload)
            spu_list_new = response_text['info']['list']

            skc_list = [item['skc'] for item in spu_list_new]
            self.get_activity_label(skc_list)
            self.get_preemption_list(skc_list)
            self.get_sku_price_v2(skc_list)
            self.get_stock_advice(skc_list)

            spu_list += spu_list_new
            time.sleep(0.3)

        cache_file = f'{self.config.auto_dir}/shein/dict/activity_price_{self.store_name}.json'
        dictActivityPrice = read_dict_from_file(cache_file)
        # cache_file = f'{self.config.auto_dir}/shein/dict/product_list_{self.store_username}.json'
        # DictSpuInfo = read_dict_from_file(cache_file, 5)
        cache_file = f'{self.config.auto_dir}/shein/preemption_num/preemption_num_{self.store_username}.json'
        dict_preemption_num = read_dict_from_file(cache_file)
        cache_file = f'{self.config.auto_dir}/shein/vmi_spot_advice/spot_advice_{self.store_username}.json'
        dict_advice = read_dict_from_file(cache_file)
        cache_file = f'{self.config.auto_dir}/shein/sku_price/sku_price_{self.store_username}.json'
        dict_sku_price = read_dict_from_file(cache_file)
        date_list = time_utils.get_past_7_days_list()
        if mode in [2, 5, 6, 7, 8, 9, 10]:
            excel_data = [[
                '店铺名称', 'SKC图片', 'SKU图片', '商品信息', '建议现货数量', '现有库存数量', '已采购数量', '预测日销',
                '本地和采购可售天数', '生产天数', '建议采购', '产品起定量',
                '备货周期(天)', '备货建议', '近7天SKU销量/SKC销量/SKC曝光', 'SKC点击率/SKC转化率', '自主参与活动',
                'SKC',
                "SKU"
            ]]
        else:
            excel_data = [[
                '店铺名称', 'SKC图片', 'SKU图片', '商品信息', '备货建议', '近7天SKU销量/SKC销量/SKC曝光',
                'SKC点击率/SKC转化率', '自主参与活动', 'SKC', "SKU"
            ]]
        for spu_info in spu_list:
            spu = str(spu_info['spu'])
            skc = str(spu_info['skc'])

            status_cn = spu_info['shelfStatus']['name']
            if status_cn != '已上架':
                continue

            # shelf_status = DictSpuInfo.get(spu, {}).get('shelf_status', '')
            # if mode != 1:
            #     if shelf_status != 'ON_SHELF' and shelf_status != 'SOLD_OUT':
            #         log('跳过', skc, shelf_status)
            #         continue

            # if mode in [5, 6, 7, 8, 9, 10] and shelf_status == 'SOLD_OUT':
            #     continue
            #
            # dictStatus = {
            #     'WAIT_SHELF': "待上架",
            #     'ON_SHELF': "已上架",
            #     'SOLD_OUT': "已售罄",
            #     'OUT_SHELF': "已下架"
            # }
            # status_cn = dictStatus.get(shelf_status, '-')

            sale_model = spu_info['saleModel']['name']
            goods_level = spu_info['goodsLevel']['name']
            goods_label = [label["name"] for label in spu_info['goodsLabelList']]
            skc_img = spu_info['picUrl']
            shelfDate = spu_info['shelfDate']
            shelfDays = spu_info['shelfDays']
            categoryName = spu_info['categoryName']

            if mode in [3] and shelfDays != 1:
                continue

            DictSkuSalesDate = self.get_skc_week_actual_sales(skc)

            for sku_info in spu_info['skuList']:
                row_item = []
                attr = sku_info['attr']
                if attr == '合计':
                    continue
                predictDaySales = sku_info['predictDaySales']
                availableOrderCount = sku_info['availableOrderCount']
                if mode == 1:
                    if availableOrderCount is None or availableOrderCount <= 0:
                        log('跳过', skc, availableOrderCount)
                        continue

                row_item.append(f'{self.store_name}\n({status_cn})\n{goods_level}\n{",".join(goods_label)}')
                row_item.append(skc_img)
                sku = sku_info['skuCode']
                skuExtCode = str(sku_info['supplierSku'])
                sku_img = self.bridge.get_sku_img(skuExtCode, source)
                row_item.append(sku_img)

                transit = sku_info['transit']  # 在途

                stock = self.bridge.get_sku_stock(skuExtCode, source)
                cost_price = self.bridge.get_sku_cost(skuExtCode, source)

                supplyPrice = dict_sku_price[sku]
                shein_stock = sku_info['stock']
                if cost_price == '-':
                    profit = '-'
                else:
                    profit = f'{float(supplyPrice) - float(cost_price):.2f}'

                min_spot_advice = dict_advice.get(skc, {}).get(sku, {}).get('minSpotAdvice', 0)
                max_spot_advice = dict_advice.get(skc, {}).get(sku, {}).get('maxSpotAdvice', 0)
                stock_advice = f'{min_spot_advice}~{max_spot_advice}'
                log('stock_advice', stock_advice)
                # 建议现货数量
                advice_stock_number = round((min_spot_advice + max_spot_advice) / 4)

                # 有现货建议
                if mode in [5, 9, 10] and advice_stock_number == 0:
                    continue

                # 无现货建议
                if mode in [6, 7, 8] and advice_stock_number > 0:
                    continue

                stockSaleDays = sku_info['stockSaleDays']

                product_info = (
                    f'SPU: {spu}\n'
                    f'SKC: {skc}\n'
                    f'SKU货号: {skuExtCode}\n'
                    f'属性集: {attr}\n'
                    f'商品分类: {categoryName}\n'
                    f'上架日期: {shelfDate}\n'
                    f'上架天数: {shelfDays}\n'
                    f'库存可售天数/现货建议: {stockSaleDays}/{stock_advice}\n'
                )
                row_item.append(product_info)

                # 建议采购数量逻辑
                try:
                    # 尝试将字符串数字转换为 float，再转为 int（如有必要）
                    current_stock = float(stock)
                    advice_purchase_number = advice_stock_number - int(current_stock)

                    # 建议采购为正
                    if (mode == 5 and advice_purchase_number <= 0):
                        continue

                except (ValueError, TypeError):
                    # 无法转换为数值时
                    advice_purchase_number = '-'

                if mode in [2, 5, 6, 7, 8, 9, 10]:
                    row_item.append(advice_stock_number)
                    row_item.append(stock)

                    row_item.append(0)
                    row_item.append(predictDaySales)
                    row_item.append(0)
                    row_item.append(7)

                    row_item.append(advice_purchase_number)
                    row_item.append(0)  # 产品起定量
                    row_item.append(0)  # 备货周期(天)

                adviceOrderCount = sku_info['adviceOrderCount'] if sku_info['adviceOrderCount'] is not None else '-'
                if sku_info['autoOrderStatus'] is not None:
                    autoOrderStatus = ['-', '是', '否'][sku_info['autoOrderStatus']] if sku_info[
                                                                                            'adviceOrderCount'] is not None else '-'
                else:
                    autoOrderStatus = '-'
                orderCount = sku_info['orderCount']  # 已下单数
                c7dSaleCnt = sku_info['c7dSaleCnt']
                c30dSaleCnt = sku_info['c30dSaleCnt']
                orderCnt = sku_info['orderCnt']
                totalSaleVolume = sku_info['totalSaleVolume']
                planUrgentCount = sku_info['planUrgentCount']
                preemptionCount = dict_preemption_num[skc][sku]
                predictDaySales = sku_info['predictDaySales']
                goodsDate = sku_info['goodsDate']
                stockDays = sku_info['stockDays']

                real_transit = transit + sku_info['stayShelf'] - sku_info['transitSale']

                sales_info = (
                    f'近7天/30天销量: {c7dSaleCnt}/{c30dSaleCnt}\n'
                    f'当天销量/购买单数: {totalSaleVolume}/{orderCnt}\n'
                    f'预测日销/下单参数: {predictDaySales}/{goodsDate}+{stockDays}\n'
                    f'预占数/预计急采数: {preemptionCount}/{planUrgentCount}\n'
                    f'建议下单/已下单数: {adviceOrderCount}/{orderCount}\n'
                    f'拟下单数/自动下单: {availableOrderCount}/{autoOrderStatus}\n'
                    f'模式/本地/在途/希音: {sale_model[:2]}/{stock}/{real_transit}/{shein_stock}\n'
                    f'成本/核价/利润: ¥{cost_price}/¥{supplyPrice}/¥{profit}\n'
                )

                row_item.append(sales_info)

                flag_yesterday = 0
                sales7cn = 0
                for date in date_list:
                    sales_num = DictSkuSalesDate.get(date, {}).get(sku, {}).get("hisActualValue", 0)
                    sales_num = sales_num if sales_num is not None else 0
                    sales7cn += sales_num
                    if time_utils.is_yesterday_date(date) and sales_num == 0:
                        flag_yesterday = 1

                if mode == 4 and flag_yesterday:
                    continue

                # 过滤掉未建立马帮信息的
                if mode in [5, 6, 7, 8, 9, 10] and advice_purchase_number == '-':
                    continue

                # 建议采购为正
                if mode in [5] and advice_purchase_number < 0:
                    continue

                # 建议采购为负
                if mode in [6, 7] and advice_purchase_number >= 0:
                    continue

                # 30内
                if mode in [9] and shelfDays > 31:
                    continue

                # 15天内
                if mode in [7] and shelfDays > 15:
                    continue

                # 30外
                if mode in [6, 8, 10] and shelfDays < 31:
                    continue

                # 有销量
                if mode in [5, 8, 9, 10] and sales7cn == 0:
                    continue

                # 无销量
                if mode in [6] and sales7cn > 0:
                    continue

                sale_num_list, sale_data_list = self.get_skc_week_sale_list(spu, skc, sku)
                row_item.append("\n".join(sale_num_list))
                row_item.append("\n".join(sale_data_list))
                row_item.append(self.get_skc_activity_label(skc, sku, dictActivityPrice))
                row_item.append(skc)
                row_item.append(sku)
                excel_data.append(row_item)

        cache_file = f'{self.config.auto_dir}/shein/cache/bak_advice_{mode}_{time_utils.today_date()}.json'
        write_dict_to_file_ex(cache_file, {self.store_name: excel_data}, {self.store_name})

        cache_file = f'{self.config.auto_dir}/shein/cache/bak_advice_notify_{mode}_{time_utils.today_date()}.json'
        NotifyItem = [self.store_name, len(excel_data[1:])]
        write_dict_to_file_ex(cache_file, {self.store_name: NotifyItem}, {self.store_name})

        return excel_data
