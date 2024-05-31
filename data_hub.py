from databases import DataBase
from figurant_hub import FigurantHub
from re import match
from json import loads

class DataHub(FigurantHub):
    var_01_contr_acc = None
    var_02_contr_name = None
    var_03_contr_ipn = None
    var_04_contr_bank_code = None
    var_05_contr_bank_name = None
    var_06_pay_purp = None
    var_07_doc_num = None
    var_08_doc_date = None
    var_09_direction = None
    var_10_sum_ct = None
    var_11_sum_dt = None
    
    def __init__(self, filename, **kwargs):
        super().__init__(filename)
        self.div_table = kwargs['div_table']
        self.cents = kwargs['cents']
        self.filename = kwargs['file_path']
        self.key_index = loads(kwargs['key_index'].replace("'",'"'))
        
        if self.div_table == "Так":
            self.fig_acc_list = kwargs['fig_acc'].split(";")
        else:
            self.fig_acc = kwargs['fig_acc']
        
        self.i = int()
        self.fill_up = False
        self.attr_list = [attr for attr in dir(DataHub) if attr.startswith('var')]

    def divider(self):
        '''
        Divide one df to multiple by key word 
        '^Выписка по счету №.*' = Банк Південний ---> xls ---> Viktor-T-37
        '^ЗАРЕЗЕРВИРОВАННЫЕ СУММЫ ПО СЧЕТУ.*' = Кліринговий Дім ---> Viktor-T-3
        '^Виконавець$' =  ---> Viktor-T-1
        '''
        regexes =   ['^ЗАРЕЗЕРВИРОВАННЫЕ СУММЫ ПО СЧЕТУ.*',
                    '^Выписка по счету №.*',
                    '^Виконавець$']
        #  "Виписка руху коштів"] # F:\Codes_Work\Bankir-Code\Tranz\Bank-Code\Examples\ОТП\xlsx\Eugene
        
        if match("(" + ")|(".join(regexes) + ")", self.element):
            self.fig_acc = self.fig_acc_list[self.i]
            self.i += 1
            return self.fig_acc

    def auto_fill(self, ii):
        if self.row[self.key_index[list(self.name_list)[ii]]] is not None:
            return self.row[self.key_index[list(self.name_list)[ii]]]
        if self.row[0] == 'Виконавець' or self.row[0] == 'Клієнт':
            self.fill_up = True
        elif self.row[0] == 'КОРЕСПОНДЕНТ:':
            if self.row[2] is not None:
                self.row[self.key_index['08. Контрагент_ПІБ']] = self.row[2]
            if self.row[3] is not None:
                self.row[self.key_index['08. Контрагент_ПІБ']] = self.row[3]
        elif self.row[0] == 'БАНК:' or self.row[0] == "НАДАВАЧ ПЛАТІЖНИХ ПОСЛУГ:":
            if self.row[2] is not None:
                self.row[self.key_index['11. Контрагент_Найменування банку']] = self.row[2]
            if self.row[3] is not None:
                self.row[self.key_index['11. Контрагент_Найменування банку']] = self.row[3]
        elif self.row[0] == 'ПРИЗНАЧЕННЯ:':
            if self.row[2] is not None:
                self.row[self.key_index['12. Призначення платежу']] = self.row[2]
            if self.row[3] is not None:
                self.row[self.key_index['12. Призначення платежу']] = self.row[3]

    def executor(self):
        db = DataBase(self.db_name)
        db.main_db()
        
        self.i = 0
        for self.row in super().file_reader():
            if self.div_table == "Так":
                for self.index, self.element in enumerate(self.row):
                    try:
                        self.divider()
                    except:
                        pass
            
            super().setter_maincol()
            try:
                self.row[self.key_index['01. Фігурант_Рахунок']] = self.fig_acc
            except:
                pass

            super().db_ct_for_onecol()
            super().date_time_formatting()
            super().bank_code_empty()
            super().uah_convertor()

            if self.cents == "Так":
                try:
                    self.row[self.key_index['16. Сумма операції Кт']] = self.row[self.key_index['16. Сумма операції Кт']] / 100
                except:
                    pass
                try:
                    self.row[self.key_index['17. Сумма операції Дт']] = self.row[self.key_index['17. Сумма операції Дт']] / 100
                except:
                    pass

            for ii in range(11):
                try:
                    setattr(DataHub, self.attr_list[ii], self.auto_fill(ii+6))
                except:
                    print("error auto_fill")
                    pass

            # не записувати в базу рядки з технічною інформацією
            try:
                if (
                    self.row[-4] == 8 or str(self.row[-4]) == "12" or
                    "Дата" in str(self.row[self.key_index['14. Дата документа']]) or
                    "Проводок" in str(self.row[self.key_index['14. Дата документа']]) or
                    "Вхідний" in str(self.row[self.key_index['14. Дата документа']]) or
                    "Вхiдний" in str(self.row[self.key_index['14. Дата документа']]) or
                    "Вихiдний" in str(self.row[self.key_index['14. Дата документа']]) or
                    "Вихідний" in str(self.row[self.key_index['14. Дата документа']])
                    ):
                    pass
                else:
                    if DataHub.var_01_contr_acc == "":
                        DataHub.var_01_contr_acc = DataHub.var_02_contr_name
                    db.write_db(
                        self.row[self.key_index['01. Фігурант_Рахунок']],
                        self.row[self.key_index['02. Валюта операції']],
                        self.row[self.key_index['03. Фігурант_ПІБ']],
                        self.row[self.key_index['04. Фігурант_ІПН']],
                        self.row[self.key_index['05. Фігурант_Код банку']],
                        self.row[self.key_index['06. Фігурант_Найменування банку']],
                        DataHub.var_01_contr_acc,
                        DataHub.var_02_contr_name,
                        DataHub.var_03_contr_ipn,
                        DataHub.var_04_contr_bank_code,
                        DataHub.var_05_contr_bank_name,
                        DataHub.var_06_pay_purp,
                        DataHub.var_07_doc_num,
                        DataHub.var_08_doc_date,
                        DataHub.var_09_direction,
                        DataHub.var_10_sum_ct,
                        DataHub.var_11_sum_dt,
                        self.fill_up
                        )
            except:
                print('error') # подумать как логировать ошибки!
                pass

# class old:
    
#     def standard_columns(self, finish_column_name, column_for_colnum, column_for_rownum, filter_criteria):
#         try:
#             info = self.data[column_for_colnum][self.data[column_for_rownum].astype(str).str.contains(filter_criteria)]
#         except:
#             info = pd.Series(['nan'], index=['Test'])
        
#         if (len(info) == 1 and info.unique()[0] == "nan") or len(info) == 0:
#             # print("empty", ";", finish_column_name, ";", column_for_colnum, ";", column_for_rownum, ";", filter_criteria)
#             pass
#         else:
#             try:
#                 self.data[finish_column_name] = info
#                 self.data[finish_column_name] = self.data[finish_column_name].fillna(method="bfill")
#                 if "Банк:Номер карты" in self.data.columns:
#                     self.data[['Банк', 'Номер карты']] = self.data['Банк:Номер карты'].str.split(' : ', expand=True)
#                 # print(info, ";", finish_column_name, ";", column_for_colnum, ";", column_for_rownum, ";", filter_criteria)
#             except:
#                 # print("error", ";", finish_column_name, ";", column_for_colnum, ";", column_for_rownum, ";", filter_criteria)
#                 pass
        
#         return self.data

    
#     @DataDecorators.formating_cents
#     @DataDecorators.balance
#     def procesor(self):
#         # Кліринговий Дім Victor-T-2
#         if self.data.columns[0] == 'Дата д-та':
#             self.data['Банк:ЄДРПОУ'] = self.data.iloc[:, [3]]
#             self.data[['Банк', 'ЄДРПОУ']] = self.data['Банк:ЄДРПОУ'].str.split(' : ', expand=True)
#             self.data['Кредит'] = self.data.iloc[:, [9]]

#         # Кліринговий Дім Viktor-T-3
#         if self.data.columns[0] == 'Номер карты':
#             self.data.columns.values[1] = "Дата и время операции"
#             if "Дата списания/" in self.data.columns:
#                 self.data.columns.values[5] = "Кредит"
#                 self.data.columns.values[6] = "Дебет"
#             else:
#                 self.data.columns.values[4] = "Кредит"
#                 self.data.columns.values[5] = "Дебет"
#             self.data = (self.data  .replace("ВЫПИСКА ПО СЧЕТУ","")
#                                     .replace("Всего операций за период",""))
        
#         # Кліринговий Дім Viktor-T-22-23
#         if self.data.columns.values[0] == "Дата док":
#             self.data.columns.values[1] = "Банк"

#         # Formatting ПриватБанк ---> xls ---> Vlad
#         if self.data.columns.values[0] == "Направление":
#             self.data.columns.values[6] = "Банк платника"
#             self.data.columns.values[8] = "Номер/код платника"
#             self.data.columns.values[9] = "Найменування платника"

#             self.data.columns.values[10] = "Банк отримувача"
#             self.data.columns.values[12] = "Номер/код отримувача"
#             self.data.columns.values[13] = "Найменування отримувача"

#         return self.data



   
