from .fun_excel import *
from .fun_base import log
from .fun_file import read_dict_from_file, read_dict_from_file_ex, write_dict_to_file, write_dict_to_file_ex
from .time_utils import TimeUtils

class SheinExcel:

    def __init__(self, config):
        self.config = config
        pass

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
            store_name = dict_store.get(store_username)
            sheet_name = store_name
            write_data(excel_path_1, sheet_name, excel_data)
            self.format_jit(excel_path_1, sheet_name)
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
            store_name = dict_store.get(store_username)
            sheet_name = store_name
            write_data(excel_path_2, sheet_name, excel_data)
            self.format_jit(excel_path_2, sheet_name)
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
