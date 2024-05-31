from databases import DataBase
from xlsxwriter.workbook import Workbook
from os import makedirs, remove

class CashFlowAnalysis(DataBase):
    def __init__(self, db_name):
        super().__init__(db_name)
        
        self.columns =      (
                            "01. Фігурант_Рахунок","02. Валюта операції","03. Фігурант_ПІБ",
                            "04. Фігурант_ІПН", "05. Фігурант_Код банку", "06. Фігурант_Найменування банку",
                            "07. Контрагент_Рахунок", "08. Контрагент_ПІБ", "09. Контрагент_ІПН",
                            "10. Контрагент_Код банку", "11. Контрагент_Найменування банку", "12. Призначення платежу",
                            "13. Номер документа", "14. Дата документа", "15. Напрямок",
                            "16. Сумма операції Кт", "17. Сумма операції Дт"
                            )
        
        self.columns_pt =   (
                            "Перша транзакція", "Остання транзакція",
                            "К-ть Вхід", "Сума Вхід",
                            "К-ть Вихід", "Сума Вихід",
                            "Контрагент_Рахунок", "Контрагент_ПІБ", "Контрагент_ІПН",
                            "Контрагент_Код банку", "Контрагент_Найменування банку",
                            )
    
    def write_to_xlsx(self, workbook, worksheet_name, columns_name, sql_function):
        worksheet = workbook.add_worksheet(worksheet_name)
        # перший рядок - назва стовпців
        for j, value in enumerate(columns_name):
            worksheet.write(0, j, value)
        # запис транзакції
        for i, row in enumerate(sql_function):
            for j, value in enumerate(row):
                worksheet.write(i+1, j, value)
    
    def create_xlsx(self):
        makedirs("xlsx", exist_ok=True)
        self.conn = self.create_connection(self.db_name)
        for unique_row in self.select_unique_acc_and_curr():
            workbook = Workbook(f"./xlsx/{unique_row[0]}_{unique_row[1]}.xlsx")
            try:
                self.write_to_xlsx(workbook, "Info", self.columns, self.select_transactions(unique_row[0], unique_row[1], unique_row[2]))
            except:
                pass
            try:
                self.write_to_xlsx(workbook, "pt", self.columns_pt, self.create_pt(unique_row[2]))
            except:
                pass
            workbook.close()

    def executor(self):
        self.create_xlsx()
