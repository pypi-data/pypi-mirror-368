from .fun_excel import *
from .fun_base import log
from .fun_file import read_dict_from_file, read_dict_from_file_ex, write_dict_to_file, write_dict_to_file_ex, delete_file
from .time_utils import TimeUtils
from .wxwork import WxWorkBot
from .shein_daily_report_model import SheinStoreSalesDetailManager, SheinStoreSalesDetail

class SheinExcel:

    def __init__(self, config):
        self.config = config
        pass

    def write_sales_data(self):
        yesterday = TimeUtils.get_yesterday()
        model = SheinStoreSalesDetailManager(self.config.database_url)
        records = model.get_one_day_records(yesterday, SheinStoreSalesDetail.sales_amount.desc())
        data_day = []
        dict_store_manager_shein = self.config.shein_store_manager
        dict_store_name = read_dict_from_file(self.config.shein_store_alias)

        # 准备每日汇总数据
        for record in records:
            store_data = []
            store_data.append(dict_store_name.get(record.store_username))
            store_data.append(dict_store_manager_shein.get(str(record.store_username).lower(), '-'))
            store_data.append(record.sales_num)
            store_data.append(record.sales_num_inc)
            store_data.append(record.sales_amount)
            store_data.append(record.sales_amount_inc)
            store_data.append(record.visitor_num)
            store_data.append(record.visitor_num_inc)
            store_data.append(record.bak_A_num)
            store_data.append(record.bak_A_num_inc)
            store_data.append(record.new_A_num)
            store_data.append(record.new_A_num_inc)
            store_data.append(record.on_sales_product_num)
            store_data.append(record.on_sales_product_num_inc)
            store_data.append(record.wait_shelf_product_num)
            store_data.append(record.wait_shelf_product_num_inc)
            store_data.append(record.upload_product_num)
            store_data.append(record.upload_product_num_inc)
            store_data.append(record.sold_out_product_num)
            store_data.append(record.shelf_off_product_num)
            data_day.append(store_data)

        excel_path = create_file_path(self.config.excel_daily_report)
        delete_file(excel_path)
        sheet_name_first = 'SHEIN销售部每日店铺情况'

        # 准备批量操作列表
        operations = []

        # 添加每日汇总sheet的操作 - 自定义操作函数
        def write_daily_data(sheet):
            # 写入数据到B5位置，保持原有格式
            sheet.range('B5').value = data_day
            # 设置标题
            sheet.range('A1').value = f'销售部SHEIN{TimeUtils.get_current_month()}月店铺数据'
            # 设置日期和合并
            sheet.range('A4').value = f'{TimeUtils.format_date_cross_platform(yesterday)}\n({TimeUtils.get_chinese_weekday(yesterday)})'

        operations.append((sheet_name_first, 'format', write_daily_data))
        operations.append((sheet_name_first, 'format', self._format_daily_summary_sheet, yesterday, len(data_day)))
        operations.append(('Sheet1', 'delete'))
        operations.append((sheet_name_first, 'move', 1))

        # 获取店铺列表并准备月度数据
        store_list = model.get_distinct_store_sales_list()
        for store in store_list:
            store_username = store[0]
            store_name = dict_store_name.get(store_username)
            records = model.get_one_month_records(TimeUtils.get_current_year(), TimeUtils.get_current_month(), store_username)

            data_month = []
            for record in records:
                store_data = []
                store_data.append(record.day)
                store_data.append(record.sales_num)
                store_data.append(record.sales_num_inc)
                store_data.append(record.sales_amount)
                store_data.append(record.sales_amount_inc)
                store_data.append(record.visitor_num)
                store_data.append(record.visitor_num_inc)
                store_data.append(record.bak_A_num)
                store_data.append(record.bak_A_num_inc)
                store_data.append(record.new_A_num)
                store_data.append(record.new_A_num_inc)
                store_data.append(record.on_sales_product_num)
                store_data.append(record.on_sales_product_num_inc)
                store_data.append(record.wait_shelf_product_num)
                store_data.append(record.wait_shelf_product_num_inc)
                store_data.append(record.upload_product_num)
                store_data.append(record.upload_product_num_inc)
                store_data.append(record.sold_out_product_num)
                store_data.append(record.shelf_off_product_num)
                # store_data.append(record.remark)  # 月度数据不包含备注列，保持19列
                data_month.append(store_data)

            # 添加月度sheet操作 - 自定义操作函数
            def write_monthly_data(sheet, data=data_month, name=store_name):
                # 写入数据到A5位置（月度数据从A列开始）
                sheet.range('A5').value = data
                # 设置标题
                sheet.range('A1').value = f'{name}SHEIN{TimeUtils.get_current_month()}月店铺数据'

            operations.append((store_name, 'format', write_monthly_data))
            operations.append((store_name, 'format', self._format_store_monthly_sheet, store_name, len(data_month)))

        # 执行批量操作
        operations.append((sheet_name_first, 'active'))
        success = batch_excel_operations(excel_path, operations)

        if success:
            # 发送文件到企业微信
            WxWorkBot('b30aaa8d-1a1f-4378-841a-8b0f8295f2d9').send_file(excel_path)
            log(f"销售数据写入完成: {excel_path}")
        else:
            log(f"销售数据写入失败: {excel_path}")

    def _format_daily_summary_sheet(self, sheet, yesterday, data_length):
        """格式化每日汇总sheet"""
        las_row = data_length + 4  # 数据从第5行开始，4行header

        # 设置数据区域格式（从B5开始，因为数据写入到B5）
        sheet.range(f'B5:U{las_row}').api.Font.Color = 0x000000
        sheet.range(f'B5:U{las_row}').api.Font.Bold = False

        # 设置A4日期列的格式和合并
        sheet.range('A4').column_width = 16
        sheet.range('A4').api.VerticalAlignment = -4160  # 垂直顶部对齐
        sheet.range(f'A4:A{las_row}').merge()

        # 设置负数为红色（E,G,I,K列）
        self._set_negative_numbers_red(sheet, ['E', 'G', 'I', 'K'], 5, las_row)

        # 格式化表头
        self._format_daily_header(sheet, las_row)

        # 设置汇总公式和格式
        self._set_summary_formulas(sheet, las_row)

        # 设置边框
        self._set_borders(sheet, f'A2:U{las_row}')

        sheet.autofit()

    def _format_store_monthly_sheet(self, sheet, store_name, data_length):
        """格式化店铺月度sheet"""
        las_row = data_length + 4  # 数据从第5行开始，4行header

        # 数据已经写入，现在进行格式化
        # 设置数据区域格式（从A5开始到S列，月度数据是19列）
        sheet.range(f'A5:S{las_row}').api.Font.Color = 0x000000
        sheet.range(f'A5:S{las_row}').api.Font.Bold = False

        # 格式化表头
        self._format_monthly_header(sheet, las_row)

        # 设置汇总公式和格式
        self._set_monthly_summary_formulas(sheet, las_row)

        # 设置边框
        self._set_borders(sheet, f'A2:S{las_row}')

        sheet.autofit()

    def _set_negative_numbers_red(self, sheet, columns, start_row, end_row):
        """设置负数为红色"""
        for col in columns:
            column_range = sheet.range(f'{col}{start_row}:{col}{end_row}')
            for cell in column_range:
                if cell.value is not None and isinstance(cell.value, (int, float)) and cell.value < 0:
                    cell.font.color = (255, 0, 0)

    def _format_daily_header(self, sheet, las_row):
        """格式化每日汇总表头，完全按照原始格式"""
        # 第一行：标题
        range_one = f'A1:U1'
        sheet.range(range_one).merge()
        sheet.range(range_one).api.Font.Size = 24
        sheet.range(range_one).api.Font.Bold = True
        sheet.range(range_one).api.HorizontalAlignment = -4108
        sheet.range(range_one).api.VerticalAlignment = -4108

        # 第二行：分类标题
        range_two_part_1 = f'A2:C2'
        range_two_part_2 = f'D2:O2'
        range_two_part_3 = f'P2:U2'
        sheet.range(range_two_part_1).merge()
        sheet.range(range_two_part_2).merge()
        sheet.range(range_two_part_3).merge()

        sheet.range(f'A2:C3').color = 0x47a100

        sheet.range('D2').value = '店铺的结果和稳定性'
        sheet.range(range_two_part_2).api.Font.Size = 16
        sheet.range(range_two_part_2).api.Font.Color = 0xFFFFFF
        sheet.range(range_two_part_2).api.Font.Bold = True
        sheet.range(range_two_part_2).api.HorizontalAlignment = -4108
        sheet.range(range_two_part_2).api.VerticalAlignment = -4108
        sheet.range(f'D2:O3').color = 0x0000FF

        sheet.range('P2').value = '上新的质量和数量'
        sheet.range(range_two_part_3).api.Font.Size = 16
        sheet.range(range_two_part_3).api.Font.Color = 0xFFFFFF
        sheet.range(range_two_part_3).api.Font.Bold = True
        sheet.range(range_two_part_3).api.HorizontalAlignment = -4108
        sheet.range(range_two_part_3).api.VerticalAlignment = -4108
        sheet.range(f'P2:U3').color = 0x47a100

        # 第三行：列标题
        range_three = f'A3:U3'
        sheet.range('A3').value = ['日期', '店铺', '店长', '昨日单量', '对比前日', '昨日销售额', '对比前日', '昨日访客',
                                   '对比前天', '备货款A', '对比前日', '新款A', '对比前日', '在售商品', '对比前日', '待上架',
                                   '对比前日', '昨日上传', '对比前日', '已售罄', '已下架']
        sheet.range(range_three).api.Font.Size = 11
        sheet.range(range_three).api.Font.Color = 0xFFFFFF
        sheet.range(range_three).api.Font.Bold = True
        sheet.range(range_three).api.HorizontalAlignment = -4108
        sheet.range(range_three).api.VerticalAlignment = -4108

        # 第四行：汇总行
        range_four = f'B4:U4'
        sheet.range('B4').value = '汇总'
        sheet.range('C4').value = '-'
        sheet.range(range_four).api.Font.Size = 11
        sheet.range(range_four).api.HorizontalAlignment = -4108
        sheet.range(range_four).api.VerticalAlignment = -4108
        sheet.range(f'B4:U4').color = 0x50d092

    def _format_monthly_header(self, sheet, las_row):
        """格式化月度表头，完全按照原始格式"""
        # 第一行：标题（合并A1:S1）
        range_one = f'A1:S1'
        sheet.range(range_one).merge()
        sheet.range(range_one).api.Font.Size = 24
        sheet.range(range_one).api.Font.Bold = True
        sheet.range(range_one).api.HorizontalAlignment = -4108
        sheet.range(range_one).api.VerticalAlignment = -4108

        # 第二行：分类标题
        range_two_part_1 = f'A2'
        range_two_part_2 = f'B2:M2'
        range_two_part_3 = f'N2:S2'
        sheet.range(range_two_part_2).merge()
        sheet.range(range_two_part_3).merge()

        sheet.range(f'A2:A3').color = 0x47a100

        sheet.range('B2').value = '店铺的结果和稳定性'
        sheet.range(range_two_part_2).api.Font.Size = 16
        sheet.range(range_two_part_2).api.Font.Color = 0xFFFFFF
        sheet.range(range_two_part_2).api.Font.Bold = True
        sheet.range(range_two_part_2).api.HorizontalAlignment = -4108
        sheet.range(range_two_part_2).api.VerticalAlignment = -4108
        sheet.range(f'B2:M3').color = 0x0000FF

        sheet.range('N2').value = '上新的质量和数量'
        sheet.range(range_two_part_3).api.Font.Size = 16
        sheet.range(range_two_part_3).api.Font.Color = 0xFFFFFF
        sheet.range(range_two_part_3).api.Font.Bold = True
        sheet.range(range_two_part_3).api.HorizontalAlignment = -4108
        sheet.range(range_two_part_3).api.VerticalAlignment = -4108
        sheet.range(f'N2:S3').color = 0x47a100

        # 第三行：列标题
        range_three = f'A3:S3'
        sheet.range('A3').value = ['日期', '昨日单量', '对比前日', '昨日销售额', '对比前日', '昨日访客', '对比前天',
                                   '备货款A', '对比前日', '新款A', '对比前日', '在售商品', '对比前日', '待上架',
                                   '对比前日', '昨日上传', '对比前日', '已售罄', '已下架']
        sheet.range(range_three).api.Font.Size = 11
        sheet.range(range_three).api.Font.Color = 0xFFFFFF
        sheet.range(range_three).api.Font.Bold = True
        sheet.range(range_three).api.HorizontalAlignment = -4108
        sheet.range(range_three).api.VerticalAlignment = -4108

        # 第四行：汇总行
        range_four = f'A4:S4'
        sheet.range('A4').value = '汇总'
        sheet.range(range_four).api.Font.Size = 11
        sheet.range(range_four).api.HorizontalAlignment = -4108
        sheet.range(range_four).api.VerticalAlignment = -4108
        sheet.range(f'A4:S4').color = 0x50d092

    def _set_summary_formulas(self, sheet, las_row):
        """设置汇总公式"""
        for col in range(2, 22):  # B列到U列（跳过A列日期）
            col_letter = xw.utils.col_name(col)
            if col_letter not in ['A', 'B', 'C']:  # A列是日期，B列是汇总，C列是-
                sheet.range(f'{col_letter}4').formula = f'=SUM({col_letter}5:{col_letter}{las_row})'
            # 所有列水平居中和垂直居中
            sheet.range(f'{col_letter}:{col_letter}').api.HorizontalAlignment = -4108
            sheet.range(f'{col_letter}:{col_letter}').api.VerticalAlignment = -4108

    def _set_monthly_summary_formulas(self, sheet, las_row):
        """设置月度汇总公式"""
        for col in range(2, 20):  # B列到S列（对应原始代码的 2 到 20）
            col_letter = xw.utils.col_name(col)
            # 所有列水平居中和垂直居中
            sheet.range(f'{col_letter}:{col_letter}').api.HorizontalAlignment = -4108
            sheet.range(f'{col_letter}:{col_letter}').api.VerticalAlignment = -4108
            # 设置汇总公式（原始代码使用固定的36行）
            sheet.range(f'{col_letter}4').formula = f'=SUM({col_letter}5:{col_letter}36)'

    def _set_borders(self, sheet, range_str):
        """设置边框"""
        range_to_border = sheet.range(range_str)
        # 设置外部边框
        range_to_border.api.Borders(7).LineStyle = 1  # 上边框
        range_to_border.api.Borders(8).LineStyle = 1  # 下边框
        range_to_border.api.Borders(9).LineStyle = 1  # 左边框
        range_to_border.api.Borders(10).LineStyle = 1  # 右边框
        # 设置内部边框
        range_to_border.api.Borders(1).LineStyle = 1  # 内部上边框
        range_to_border.api.Borders(2).LineStyle = 1  # 内部下边框
        range_to_border.api.Borders(3).LineStyle = 1  # 内部左边框
        range_to_border.api.Borders(4).LineStyle = 1  # 内部右边框

    def format_bak_advice(self, excel_path, sheet_name, mode):
        app, wb, sheet = open_excel(excel_path, sheet_name)
        beautify_title(sheet)
        add_borders(sheet)
        column_to_left(sheet,
                       ["商品信息", "备货建议", "近7天SKU销量/SKC销量/SKC曝光", "SKC点击率/SKC转化率",
                        "自主参与活动"])
        autofit_column(sheet, ['店铺名称', '商品信息', '备货建议', "近7天SKU销量/SKC销量/SKC曝光",
                               "SKC点击率/SKC转化率",
                               "自主参与活动"])

        if mode in [2, 5, 6, 7, 8, 9, 10]:
            format_to_number(sheet, ['本地和采购可售天数'], 1)
            add_formula_for_column(sheet, '本地和采购可售天数', '=IF(H2>0, (F2+G2)/H2,0)')
            add_formula_for_column(sheet, '建议采购', '=IF(I2 > J2,0,E2)')

        colorize_by_field(app, wb, sheet, 'SKC')
        specify_column_width(sheet, ['商品信息'], 180 / 6)
        InsertImageV2(app, wb, sheet, ['SKC图片', 'SKU图片'])
        wb.save()
        close_excel(app, wb)
        if mode == 4:
            WxWorkBot('b30aaa8d-1a1f-4378-841a-8b0f8295f2d9').send_file(excel_path)

    def write_bak_advice(self, mode_list):
        excel_path_list = [
            [1, self.config.Excel_Bak_Advise],
            [2, self.config.Excel_Purchase_Advise2],
            [3, self.config.Excel_Product_On_Shelf_Yesterday],
            [4, f'{self.config.auto_dir}/shein/昨日出单/昨日出单(#len#)_#store_name#_{TimeUtils.today_date()}.xlsx'],
            [5, self.config.Excel_Purchase_Advise],
            [6, self.config.Excel_Purchase_Advise6],
            [7, self.config.Excel_Purchase_Advise7],
            [8, self.config.Excel_Purchase_Advise8],
            [9, self.config.Excel_Purchase_Advise9],
            [10, self.config.Excel_Purchase_Advise10],
        ]
        mode_excel_path_list = [row for row in excel_path_list if row[0] in mode_list]
        new_excel_path_list = []
        for mode, excel_path in mode_excel_path_list:
            summary_excel_data = []
            cache_file = f'{self.config.auto_dir}/shein/cache/bak_advice_{mode}_{TimeUtils.today_date()}.json'
            dict = read_dict_from_file(cache_file)
            header = []
            new_excel_path = excel_path
            for store_name, excel_data in dict.items():
                sheet_name = store_name
                # 处理每个店铺的数据

                if mode in [2, 4]:
                    new_excel_path = str(excel_path).replace('#len#', str(len(excel_data[1:])))
                    new_excel_path = new_excel_path.replace('#store_name#', store_name)
                    new_excel_path_list.append(new_excel_path)
                    sheet_name = 'Sheet1'

                log(new_excel_path)
                if mode in [2]:
                    excel_data = sort_by_column(excel_data, 4, 1)
                write_data(new_excel_path, sheet_name, excel_data)
                self.format_bak_advice(new_excel_path, sheet_name, mode)

                # 是否合并表格数据
                if mode in [1, 3]:
                    header = excel_data[0]
                    summary_excel_data += excel_data[1:]

            if mode in [1, 3]:
                sheet_name = 'Sheet1'
                write_data(new_excel_path, sheet_name, [header] + summary_excel_data)
                self.format_bak_advice(new_excel_path, sheet_name, mode)

        return new_excel_path_list

    def write_activity_list(self):
        cache_file = f'{self.config.auto_dir}/shein/activity_list/activity_list_{TimeUtils.today_date()}.json'
        dict_activity = read_dict_from_file(cache_file)
        all_data = []
        header = []
        for store_username, excel_data in dict_activity.items():
            header = excel_data[:1]
            all_data += excel_data[1:]

        all_data = header + all_data

        excel_path = create_file_path(self.config.excel_activity_list)
        sheet_name = 'Sheet1'
        write_data(excel_path, sheet_name, all_data)
        self.format_activity_list(excel_path, sheet_name)

    def format_activity_list(self, excel_path, sheet_name):
        app, wb, sheet = open_excel(excel_path, sheet_name)
        beautify_title(sheet)
        add_borders(sheet)
        column_to_left(sheet, ['活动信息'])
        colorize_by_field(app, wb, sheet, '店铺名称')
        autofit_column(sheet, ['店铺名称', '活动信息'])
        wb.save()
        close_excel(app, wb)

    def write_jit_data(self):
        excel_path_1 = create_file_path(self.config.Excel_Order_Type_1)
        summary_excel_data_1 = []

        cache_file_1 = f'{self.config.auto_dir}/shein/cache/jit_{TimeUtils.today_date()}_1_{TimeUtils.get_period()}.json'
        dict_1 = read_dict_from_file(cache_file_1)
        dict_store = read_dict_from_file(f'{self.config.auto_dir}/shein_store_alias.json')

        header = []
        for store_username, excel_data in dict_1.items():
            # store_name = dict_store.get(store_username)
            # sheet_name = store_name
            # write_data(excel_path_1, sheet_name, excel_data)
            # self.format_jit(excel_path_1, sheet_name)
            header = excel_data[0]
            summary_excel_data_1 += excel_data[1:]

        if len(summary_excel_data_1) > 0:
            sheet_name = 'Sheet1'
            write_data(excel_path_1, sheet_name, [header] + summary_excel_data_1)
            self.format_jit(excel_path_1, sheet_name)

        excel_path_2 = create_file_path(self.config.Excel_Order_Type_2)
        summary_excel_data_2 = []

        cache_file_2 = f'{self.config.auto_dir}/shein/cache/jit_{TimeUtils.today_date()}_2_{TimeUtils.get_period()}.json'
        dict_2 = read_dict_from_file(cache_file_2)

        header = []
        for store_username, excel_data in dict_2.items():
            # store_name = dict_store.get(store_username)
            # sheet_name = store_name
            # write_data(excel_path_2, sheet_name, excel_data)
            # self.format_jit(excel_path_2, sheet_name)
            header = excel_data[0]
            summary_excel_data_2 += excel_data[1:]

        if len(summary_excel_data_2) > 0:
            sheet_name = 'Sheet1'
            write_data(excel_path_2, sheet_name, [header] + summary_excel_data_2)
            self.format_jit(excel_path_2, sheet_name)

    def format_jit(self, excel_path, sheet_name):
        app, wb, sheet = open_excel(excel_path, sheet_name)
        beautify_title(sheet)
        add_borders(sheet)
        colorize_by_field(app, wb, sheet, 'SKC')
        column_to_left(sheet, ["商品信息", "近7天SKU销量/SKC销量/SKC曝光", "SKC点击率/SKC转化率", "自主参与活动"])
        autofit_column(sheet,
                       ['店铺名称', '商品信息', "近7天SKU销量/SKC销量/SKC曝光", "SKC点击率/SKC转化率", "自主参与活动"])
        InsertImageV2(app, wb, sheet, ['SKC图片', 'SKU图片'])
        wb.save()
        close_excel(app, wb)
        WxWorkBot('b30aaa8d-1a1f-4378-841a-8b0f8295f2d9').send_file(excel_path)

    def write_week_report(self):
        excel_path = create_file_path(self.config.excel_week_sales_report)
        log(excel_path)

        cache_file = f'{self.config.auto_dir}/shein/cache/week_sales_{TimeUtils.today_date()}.json'
        dict = read_dict_from_file(cache_file)

        summary_excel_data = []
        header = []
        for store_name, excel_data in dict.items():
            # sheet_name = store_name
            # write_data(excel_path, sheet_name, excel_data)
            # self.format_week_report(excel_path, sheet_name)
            header = excel_data[0]
            summary_excel_data += excel_data[1:]
        summary_excel_data = [header] + summary_excel_data
        sheet_name = 'Sheet1'
        write_data(excel_path, sheet_name, summary_excel_data)
        self.format_week_report(excel_path, sheet_name)

    def format_week_report(self, excel_path, sheet_name):
        app, wb, sheet = open_excel(excel_path, sheet_name)
        beautify_title(sheet)
        column_to_left(sheet, ['商品信息'])
        format_to_money(sheet, ['申报价', '成本价', '毛利润', '利润'])
        format_to_percent(sheet, ['支付率', '点击率', '毛利率'])
        self.dealFormula(sheet)  # 有空再封装优化
        colorize_by_field(app, wb, sheet, 'SPU')
        autofit_column(sheet, ['商品信息', '店铺名称', 'SKC点击率/SKC转化率', '自主参与活动'])
        column_to_left(sheet, ['店铺名称', 'SKC点击率/SKC转化率', '自主参与活动'])
        specify_column_width(sheet, ['商品标题'], 150 / 6)
        add_borders(sheet)
        InsertImageV2(app, wb, sheet, ['SKC图片', 'SKU图片'], 'shein', 120, None, None, True)
        wb.save()
        close_excel(app, wb)

    # 处理公式计算
    def dealFormula(self, sheet):
        # 增加列 周销增量 月销增量
        col_week_increment = find_column_by_data(sheet, 1, '周销增量')
        if col_week_increment is None:
            col_week_increment = find_column_by_data(sheet, 1, '远30天销量')
            log(f'{col_week_increment}:{col_week_increment}')
            sheet.range(f'{col_week_increment}:{col_week_increment}').insert('right')
            sheet.range(f'{col_week_increment}1').value = '周销增量'
            log('已增加列 周销增量')

        col_month_increment = find_column_by_data(sheet, 1, '月销增量')
        if col_month_increment is None:
            col_month_increment = find_column_by_data(sheet, 1, '总销量')
            log(f'{col_month_increment}:{col_month_increment}')
            sheet.range(f'{col_month_increment}:{col_month_increment}').insert('right')
            sheet.range(f'{col_month_increment}1').value = '月销增量'
            log('已增加列 月销增量')

        col_month_profit = find_column_by_data(sheet, 1, '近30天利润')
        if col_month_profit is None:
            col_month_profit = find_column_by_data(sheet, 1, '总利润')
            sheet.range(f'{col_month_profit}:{col_month_profit}').insert('right')
            log((f'{col_month_profit}:{col_month_profit}'))
            sheet.range(f'{col_month_profit}1').value = '近30天利润'
            log('已增加列 近30天利润')

        col_week_profit = find_column_by_data(sheet, 1, '近7天利润')
        if col_week_profit is None:
            col_week_profit = find_column_by_data(sheet, 1, '近30天利润')
            sheet.range(f'{col_week_profit}:{col_week_profit}').insert('right')
            log((f'{col_week_profit}:{col_week_profit}'))
            sheet.range(f'{col_week_profit}1').value = '近7天利润'
            log('已增加列 近7天利润')

        # return

        # 查找 申报价，成本价，毛利润，毛利润率 所在列
        col_verify_price = find_column_by_data(sheet, 1, '申报价')
        col_cost_price = find_column_by_data(sheet, 1, '成本价')
        col_gross_profit = find_column_by_data(sheet, 1, '毛利润')
        col_gross_margin = find_column_by_data(sheet, 1, '毛利率')

        col_week_1 = find_column_by_data(sheet, 1, '近7天销量')
        col_week_2 = find_column_by_data(sheet, 1, '远7天销量')
        col_month_1 = find_column_by_data(sheet, 1, '近30天销量')
        col_month_2 = find_column_by_data(sheet, 1, '远30天销量')

        # 遍历可用行
        used_range_row = sheet.range('A1').expand('down')
        for i, cell in enumerate(used_range_row):
            row = i + 1
            if row < 2:
                continue
            rangeA = f'{col_verify_price}{row}'
            rangeB = f'{col_cost_price}{row}'

            rangeC = f'{col_week_increment}{row}'
            rangeD = f'{col_month_increment}{row}'

            # rangeE = f'{col_total_profit}{row}'
            rangeF = f'{col_month_profit}{row}'
            rangeG = f'{col_week_profit}{row}'

            # 设置毛利润和毛利润率列公式与格式
            sheet.range(f'{col_gross_profit}{row}').formula = f'=IF(ISNUMBER({rangeB}),{rangeA}-{rangeB},"")'
            sheet.range(f'{col_gross_profit}{row}').number_format = '0.00'
            sheet.range(f'{col_gross_margin}{row}').formula = f'=IF(ISNUMBER({rangeB}),({rangeA}-{rangeB})/{rangeA},"")'
            sheet.range(f'{col_gross_margin}{row}').number_format = '0.00%'

            sheet.range(rangeC).formula = f'={col_week_1}{row}-{col_week_2}{row}'
            sheet.range(rangeC).number_format = '0'
            sheet.range(rangeD).formula = f'={col_month_1}{row}-{col_month_2}{row}'
            sheet.range(rangeD).number_format = '0'

            # sheet.range(rangeE).formula = f'=IF(ISNUMBER({rangeB}),{col_total}{row}*{col_gross_profit}{row},"")'
            # sheet.range(rangeE).number_format = '0.00'
            sheet.range(rangeF).formula = f'=IF(ISNUMBER({rangeB}),{col_month_1}{row}*{col_gross_profit}{row},"")'
            sheet.range(rangeF).number_format = '0.00'
            sheet.range(rangeG).formula = f'=IF(ISNUMBER({rangeB}),{col_week_1}{row}*{col_gross_profit}{row},"")'
            sheet.range(rangeG).number_format = '0.00'
