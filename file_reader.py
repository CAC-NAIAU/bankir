from dict import data_for_rename
from numpy import integer, int64

from openpyxl import load_workbook as load_openpyxl
from xlrd import open_workbook as open_xlrd
from csv import reader as csv_reader
import xml.etree.ElementTree as ET
import xlwings as xw

import datetime
import logging

class FileReader:
    def __init__(self, filename):
        self.filename = filename
        self.data = None
        self.element = str()
        self.row = str()
        self.q = 0
        self.index = int()
        self.fig_acc = str()
        self.db_name = "database.db"
        self.check_col = 0

        self.key_index = dict()
        self.row = list()
        self.list_df = list()

        self.name_list = [
                        "01. Фігурант_Рахунок", "02. Валюта операції", "03. Фігурант_ПІБ",
                        "04. Фігурант_ІПН", "05. Фігурант_Код банку", "06. Фігурант_Найменування банку",
                        "07. Контрагент_Рахунок", "08. Контрагент_ПІБ", "09. Контрагент_ІПН",
                        "10. Контрагент_Код банку", "11. Контрагент_Найменування банку", "12. Призначення платежу",
                        "13. Номер документа", "14. Дата документа", "15. Напрямок",
                        "16. Сумма операції Кт", "17. Сумма операції Дт"
                         ]

    def formatting_element(self):
        # try except to avoid errors with None
        try:
            self.element =  (self.element.replace("_x000D_\n","")
                                    .replace("~", "@").replace(";", "@")
                                    .replace('-\n', '').replace(" \n"," ")
                                    .replace("\n"," ").replace("отриму-вача","отримувача")
                                    .replace("одер-жувача", "одержувача").replace("доку-мента", "документа")
                            )
        except:
            pass
        # print("'"+self.element+"'")
        return self.element
    
    def getter_colname(self):
        '''
        Rename columns name
        '''
        for key in data_for_rename:
            for item in data_for_rename[key]:
                if item==self.element:
                    self.key_index[key] = self.index
                    # print(item, self.element, self.key_index[key], self.index)
                    break
        if len(self.key_index) == 0:
            try:
                self.check_col = int64(self.row[-1])
            except:
                try:
                    self.check_col = int64(self.row[-1].replace(".",""))
                except:
                    self.check_col = self.row[-1]
            
            if isinstance(self.check_col, integer) and len(self.row)==20:
                self.key_index=     {
                                    '13. Номер документа':0, 
                                    '14. Дата документа':1,
                                    '18. Сумма операції':2,
                                    '18_1. Сума операції (UAH)':3,
                                    '02. Валюта операції':4,
                                    '19. Номер рахунку платника':5,
                                    '20. Код банку платника':6,
                                    '21. Банк платника':7,
                                    '23. Найменування платника':8,
                                    '22. Номер/код платника':9,
                                    '24. ІР-адреса платника':10,
                                    '26. Код банку отримувача':11,
                                    '27. Банк отримувача':12,
                                    '29. Найменування отримувача':13,
                                    '25. Номер рахунку отримувача':14,
                                    '28. Номер/код отримувача':15,
                                    '12. Призначення платежу':16,
                                    '30. Дата проведення операції':17,
                                    '31. Час здійснення операції':18,
                                    '32. Залишок коштів на рахунку':19
                                    }

            elif isinstance(self.check_col, integer) and len(self.row)==19:
                self.key_index=     {
                                    '13. Номер документа':0, 
                                    '14. Дата документа':1,
                                    '18. Сумма операції':2,
                                    '18_1. Сума операції (UAH)':3,
                                    '02. Валюта операції':4,
                                    '19. Номер рахунку платника':5,
                                    '20. Код банку платника':6,
                                    '21. Банк платника':7,
                                    '23. Найменування платника':8,
                                    '22. Номер/код платника':9,
                                    '25. Номер рахунку отримувача':10, # якщо АЙПИ то видаляти
                                    '26. Код банку отримувача':11,
                                    '27. Банк отримувача':12,
                                    '29. Найменування отримувача':13,
                                    '28. Номер/код отримувача':14,
                                    '12. Призначення платежу':15,
                                    '30. Дата проведення операції':16,
                                    '31. Час здійснення операції':17,
                                    '32. Залишок коштів на рахунку':18
                                    }
            
            elif isinstance(self.check_col, integer) and len(self.row)==18:
                self.key_index=     {
                                    '13. Номер документа':0, 
                                    '14. Дата документа':1,
                                    '18. Сумма операції':2,
                                    '18_1. Сума операції (UAH)':3,
                                    '02. Валюта операції':4,
                                    '19. Номер рахунку платника':5,
                                    '20. Код банку платника':6,
                                    '21. Банк платника':7,
                                    '23. Найменування платника':8,
                                    '22. Номер/код платника':9,
                                    '26. Код банку отримувача':10,
                                    '27. Банк отримувача':11,
                                    '29. Найменування отримувача':12,
                                    '28. Номер/код отримувача':13,
                                    '12. Призначення платежу':14,
                                    '30. Дата проведення операції':15,
                                    '31. Час здійснення операції':16,
                                    '32. Залишок коштів на рахунку':17
                                    }
                
            elif isinstance(self.row[2], integer) and len(self.row)==23:
                self.key_index=     {
                                    '13. Номер документа':0, 
                                    '14. Дата документа':1,
                                    '35. Вхідний залишок на початок дня':2,
                                    '37. Вихідний залишок на кінець дня':3,
                                    '36. Вхідний залишок на початок дня (UAH)':4,
                                    '38. Вихідний залишок на кінець дня (UAH)':5,
                                    '18. Сумма операції':6,
                                    '18_1. Сума операції (UAH)':7,
                                    '02. Валюта операції':8,
                                    '19. Номер рахунку платника':9,
                                    '20. Код банку платника':10,
                                    '21. Банк платника':11,
                                    '23. Найменування платника':12,
                                    '22. Номер/код платника':13,
                                    '25. Номер рахунку отримувача':14,
                                    '26. Код банку отримувача':15,
                                    '27. Банк отримувача':16,
                                    '29. Найменування отримувача':17,
                                    '28. Номер/код отримувача':18,
                                    '12. Призначення платежу':19,
                                    '01. Фігурант_Рахунок':20,
                                    '30. Дата проведення операції':21,
                                    '31. Час здійснення операції':22
                                    }
        return self.key_index
    
    def setter_maincol(self):
        if len(self.key_index)>0:
            for item in self.name_list:
                if item not in self.key_index:
                    self.key_index[item] = len(self.row)
                try:
                    self.row[self.key_index[item]]
                except:
                    self.row.append(None)
                try:
                    self.row[self.key_index[item]]
                except:
                    self.row.append(None)
        return self.row
    
    def db_ct_for_onecol(self):
        try:
            if "." in self.row[self.key_index['18. Сумма операції']]:
                self.row[self.key_index['18. Сумма операції']] = float(self.row[self.key_index['18. Сумма операції']].strip().replace(" ","").replace(",",""))
            else:
                self.row[self.key_index['18. Сумма операції']] = float(self.row[self.key_index['18. Сумма операції']].strip().replace(" ","").replace(",","."))
        except:
            try:
                self.row[self.key_index['18. Сумма операції']] = float(self.row[self.key_index['18. Сумма операції']])
            except:
                pass

        try:
            if self.row[self.key_index['16. Сумма операції Кт']]==None and self.row[self.key_index['17. Сумма операції Дт']]==None:
                if str(self.row[self.key_index['01. Фігурант_Рахунок']]) in str(self.row[self.key_index['19. Номер рахунку платника']]) or str(self.row[self.key_index['19. Номер рахунку платника']]) in str(self.row[self.key_index['01. Фігурант_Рахунок']]):
                    self.row[self.key_index['17. Сумма операції Дт']] = abs(float(self.row[self.key_index['18. Сумма операції']]))
                elif str(self.row[self.key_index['01. Фігурант_Рахунок']]) in str(self.row[self.key_index['25. Номер рахунку отримувача']]) or str(self.row[self.key_index['25. Номер рахунку отримувача']]) in str(self.row[self.key_index['01. Фігурант_Рахунок']]):
                    self.row[self.key_index['16. Сумма операції Кт']] = float(self.row[self.key_index['18. Сумма операції']])
                else:
                    raise
        except:
            try:
                if self.row[self.key_index['15. Напрямок']] == "Надходження" or self.row[self.key_index['15. Напрямок']].strip() == "Кт" or self.row[self.key_index['15. Напрямок']].strip() == "CR":
                    self.row[self.key_index['16. Сумма операції Кт']] = float(self.row[self.key_index['18. Сумма операції']])
                elif self.row[self.key_index['15. Напрямок']] == "Витрати" or self.row[self.key_index['15. Напрямок']].strip() == "Дт" or self.row[self.key_index['15. Напрямок']].strip() == "DB":
                    self.row[self.key_index['17. Сумма операції Дт']] = abs(float(self.row[self.key_index['18. Сумма операції']]))
                elif float(self.row[self.key_index['18. Сумма операції']])>0:
                    self.row[self.key_index['16. Сумма операції Кт']] = float(self.row[self.key_index['18. Сумма операції']])
                elif float(self.row[self.key_index['18. Сумма операції']])<0:
                    self.row[self.key_index['17. Сумма операції Дт']] = abs(float(self.row[self.key_index['18. Сумма операції']]))
                else:
                    self.row[self.key_index['16. Сумма операції Кт']] = float(self.row[self.key_index['18. Сумма операції']])
                    self.row[self.key_index['17. Сумма операції Дт']] = float(self.row[self.key_index['18. Сумма операції']])
            except:
                pass
        #
        cols = {
               "03. Фігурант_ПІБ":                  ["23. Найменування платника", "29. Найменування отримувача"], 
               "04. Фігурант_ІПН":                  ["22. Номер/код платника", "28. Номер/код отримувача"],
               "05. Фігурант_Код банку":            ["20. Код банку платника", "26. Код банку отримувача"],
               "06. Фігурант_Найменування банку":   ["21. Банк платника", "27. Банк отримувача"],
               
               "07. Контрагент_Рахунок":            ["25. Номер рахунку отримувача", "19. Номер рахунку платника"], 
               "08. Контрагент_ПІБ":                ["29. Найменування отримувача", "23. Найменування платника"],
               "09. Контрагент_ІПН":                ["28. Номер/код отримувача", "22. Номер/код платника"],
               "10. Контрагент_Код банку":          ["26. Код банку отримувача", "20. Код банку платника"],
               "11. Контрагент_Найменування банку": ["27. Банк отримувача", "21. Банк платника"]
               }
        
        for item, value in cols.items():
            try:
                if (self.row[self.key_index['19. Номер рахунку платника']] is None or str(self.row[self.key_index['01. Фігурант_Рахунок']]) in str(self.row[self.key_index['19. Номер рахунку платника']]) or str(self.row[self.key_index['19. Номер рахунку платника']]) in str(self.row[self.key_index['01. Фігурант_Рахунок']])) and str(self.row[self.key_index['19. Номер рахунку платника']]).strip() != "":
                    self.row[self.key_index[item]] = self.row[self.key_index[value[0]]]
                else:
                    self.row[self.key_index[item]] = self.row[self.key_index[value[1]]]
            except:
                pass

        try:
            if (isinstance(self.row[self.key_index['16. Сумма операції Кт']], float) or isinstance(self.row[self.key_index['16. Сумма операції Кт']], int)) and self.row[self.key_index['16. Сумма операції Кт']]>0:
                self.row[self.key_index['15. Напрямок']] = "CR"
                self.row[self.key_index['17. Сумма операції Дт']] = 0
            elif isinstance(self.row[self.key_index['17. Сумма операції Дт']], float) or isinstance(self.row[self.key_index['17. Сумма операції Дт']], int) and self.row[self.key_index['17. Сумма операції Дт']]>0:
                self.row[self.key_index['15. Напрямок']] = "DB"
                self.row[self.key_index['16. Сумма операції Кт']] = 0
        except:
            pass
        # print(self.key_index)
        # print(self.row)
        return self.row

    def date_time_formatting(self):
        # print(self.row[self.key_index["30. Дата проведення операції"]], type(self.row[self.key_index["30. Дата проведення операції"]]))
        # print(self.row[self.key_index["31. Час здійснення операції"]], type(self.row[self.key_index["31. Час здійснення операції"]]))
        if self.row[self.key_index['14. Дата документа']] is None:
            try:
                if isinstance(self.row[self.key_index["30. Дата проведення операції"]], datetime.datetime) or isinstance(self.row[self.key_index["30. Дата проведення операції"]], datetime.date):
                    dateoperation = self.row[self.key_index["30. Дата проведення операції"]].strftime("%Y-%m-%d")
                elif isinstance(self.row[self.key_index["30. Дата проведення операції"]], str):
                    dateoperation = self.row[self.key_index["30. Дата проведення операції"]].replace('.000','')
                elif isinstance(self.row[self.key_index["30. Дата проведення операції"]], float):
                    dateoperation = self.row[self.key_index["30. Дата проведення операції"]]
            except:
                dateoperation = ''

            try:
                if isinstance(self.row[self.key_index["31. Час здійснення операції"]], datetime.time):
                    timeoperation = ' ' + self.row[self.key_index["31. Час здійснення операції"]].strftime("%H:%M:%S")
                elif isinstance(self.row[self.key_index["31. Час здійснення операції"]], str):
                    timeoperation = ' ' + self.row[self.key_index["31. Час здійснення операції"]]
                elif isinstance(self.row[self.key_index["31. Час здійснення операції"]], float):
                    timeoperation = self.row[self.key_index["31. Час здійснення операції"]]
            except:
                timeoperation = ''

            try:
                self.row[self.key_index['14. Дата документа']] = dateoperation + timeoperation
            except:
                pass
        # print(self.key_index)
        # print(self.row)
        return self.row

    def bank_code_empty(self):
        try:
            if self.row[self.key_index["10. Контрагент_Код банку"]] is None:
                self.row[self.key_index["10. Контрагент_Код банку"]] = self.row[self.key_index["11. Контрагент_Найменування банку"]]
        except:
            pass
        return self.row
    
    def uah_convertor(self):
        print(self.row[self.key_index["14. Дата документа"]])
        print(self.row[self.key_index["02. Валюта операції"]], self.row[self.key_index['16. Сумма операції Кт']], self.row[self.key_index['17. Сумма операції Дт']])
        
        
        return self.row
    
    def file_reader(self):
        if ".xls" in self.filename:
            while self.data is None:
                try:
                    # openpyxl
                    self.data = load_openpyxl(self.filename).worksheets[0]
                    for self.row in self.data.iter_rows(values_only=True):
                        self.row = list(self.row)
                        yield self.row
                    break
                except Exception as Argument: 
                    logging.exception(f"{self.filename} - Error with openpyxl") 

                try:
                    # xlrd
                    wb = open_xlrd(self.filename)
                    sheet = wb.sheet_by_index(0)
                    for i in range(0, sheet.nrows):
                        self.row = sheet.row_values(i)
                        yield self.row
                    break
                except Exception as Argument: 
                    logging.exception(f"{self.filename} - Error with xlrd") 
                
                try:
                    # xls as xml
                    tree = ET.parse(self.filename)
                    root = tree.getroot()
                    worksheet = root.find(".//{urn:schemas-microsoft-com:office:spreadsheet}Worksheet[@{urn:schemas-microsoft-com:office:spreadsheet}Name='MainRep']")
                    self.data = []
                    for row in worksheet.findall(".//{urn:schemas-microsoft-com:office:spreadsheet}Row"):
                        row_data = []
                        for cell in row.findall(".//{urn:schemas-microsoft-com:office:spreadsheet}Cell"):
                            cell_value = cell.find("{urn:schemas-microsoft-com:office:spreadsheet}Data")
                            row_data.append(cell_value.text if cell_value is not None else "")
                        self.data.append(row_data)
                    # Display the extracted table data
                    for self.row in self.data:
                        yield self.row
                    break
                except Exception as Argument: 
                    logging.exception(f"{self.filename} - Error with xls as xml")

                try:
                    book = xw.Book(self.filename)
                    sheet = book.sheets(0)
                    # Find the last row with data in column A
                    last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row
                    last_column = sheet.range('AA1').end('left').column
                    i = 12
                    while last_column == 1:
                        last_column = sheet.range(f'AA{i}').end('left').column
                        i+=1
                    
                    self.data = []
                    # Iterate through rows
                    for row in range(1, last_row + 1):
                        data_in_row = []
                        # Iterate through columns
                        for column in range(1, last_column+1):
                            # Access cell value
                            cell_value = sheet.cells(row, column).value
                            data_in_row.append(cell_value)
                        self.data.append(data_in_row)
                    book.close()
                    # Display the extracted table data
                    for self.row in self.data:
                        if len(self.row) == 1:
                            try:
                                self.row = self.row[0].split(";")
                            except:
                                pass
                        yield self.row
                    break
                except Exception as Argument: 
                    logging.exception(f"{self.filename} - Error with xls as xw")
        
        elif ".csv" in self.filename:
            with open(rf"{self.filename}", encoding='cp1251') as file_obj:
                self.data = csv_reader(file_obj, delimiter=";")
                for self.row in self.data:
                    yield self.row
        
        else:
            logging.exception(f"{self.filename} - Unknown file format")
