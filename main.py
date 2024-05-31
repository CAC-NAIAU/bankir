import typing
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from gui import Ui_MainWindow
from figurant_hub import FigurantHub
from data_hub import DataHub
from cashflow_analysis import CashFlowAnalysis
import time
import logging
import os

import sys

class Window(QtWidgets.QMainWindow):
    idCounter = 0

    def __init__(self):
        super(Window, self).__init__()
        self.filenames = []
        self.filename = ''
        self.cashflow_info = {}

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.pushButton_4.clicked.connect(self.analyseCashFlow)          # "Аналіз"
        self.ui.pushButton_5.clicked.connect(self.processingTableData)      # "Обробка"
        self.ui.pushButton_6.clicked.connect(self.getInfoFilesDownloader)   # "Завантажити"
        self.ui.pushButton_7.clicked.connect(self.removeRow)                # "Очистити"
        self.ui.pushButton_8.clicked.connect(self.removeDataBase)           # "Видалити базу"
    
    def getInfoFilesDownloader(self):
        '''
        Кнопка Завантажити - обрати файли для обробки та використати щодо них функцію loadCashFlow()
        '''
        self.filenames = QtWidgets.QFileDialog.getOpenFileNames()[0]
        self.loadCashFlow()
        return self.filenames
    
    def removeDataBase(self):
        if os.path.exists("database.db"):
            os.remove("database.db")
        self.show_message("Повідомлення", "БАЗУ видалено")
    
    def removeRow(self):
        '''
        Функція очищення інформації про файл з інтерфейсу програми
        '''
        if self.ui.tableWidget.rowCount() > 0:
            currentRow = self.ui.tableWidget.currentRow()
            self.ui.tableWidget.removeRow(currentRow)
            Window.idCounter -= 1
    
    def show_message(self, title, text):
        error = QMessageBox()
        error.setWindowTitle(title)
        error.setText(text)
        error.setIcon(QMessageBox.Warning)
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()
    
    def logger(self, func_name, action, name_of_file, log_write=True):
        '''
        Функція логування помилок
        '''
        f = open("log_error.txt", "a")
        f.write(f"\n\n_________{name_of_file.split('/')[-1]}_________\n_________{func_name}\n\n")
        f.close()
        logging.basicConfig(filename='log_error.txt',level=logging.DEBUG)
        logging.exception("message")

        if log_write:
            self.ui.tableWidget.setRowCount(Window.idCounter + 1)
            self.ui.tableWidget.setItem(Window.idCounter, 0, QTableWidgetItem(str(name_of_file.split('/')[-1])))
            self.ui.tableWidget.setItem(Window.idCounter, 1, QTableWidgetItem(str("0")))
            self.ui.tableWidget.setItem(Window.idCounter, 2, QTableWidgetItem(f"Помилка під час {action}"))
            self.ui.tableWidget.setItem(Window.idCounter, 9, QTableWidgetItem(str(name_of_file)))
            Window.idCounter += 1

        self.show_message("Помилка", name_of_file)
                
    def loadCashFlow(self):
        '''
        Отримати первинну інформацію з файлу, а саме:
        - його назва, 
        - пор. ном. таблиці (якщо в одному файлі 2 і біл. виписок),
        - чи форматувати в копійки. Також в цьому стовпці висвітлюєтсья інформація про помилку під час роботи з файлом
        - номер фігурантського рахунку
        - шлях до файлу
        Генерація файлу csv за результатами виклику FigurantHub().executor()
        '''
        self.ui.tableWidget.setColumnCount(6)
        self.ui.tableWidget.setHorizontalHeaderLabels(("Файл", "Розділити виписку?", "Копійки", "Рахунок", "Шлях", "Індекс"))
        
        i = 1
        for self.filename in self.filenames:
            obj = FigurantHub(self.filename)
            try:
                self.ui.tableWidget.setRowCount(Window.idCounter + 1)
                self.ui.tableWidget.setItem(Window.idCounter, 0, QTableWidgetItem(str(self.filename.split('/')[-1])))
                self.ui.tableWidget.setItem(Window.idCounter, 1, QTableWidgetItem("Ні"))
                self.ui.tableWidget.setItem(Window.idCounter, 2, QTableWidgetItem("Ні"))
                self.ui.tableWidget.setItem(Window.idCounter, 3, QTableWidgetItem(str(obj.exe_getter_fig_acc())))
                self.ui.tableWidget.setItem(Window.idCounter, 4, QTableWidgetItem(str(self.filename)))
                self.ui.tableWidget.setItem(Window.idCounter, 5, QTableWidgetItem(str(obj.key_index)))
                Window.idCounter += 1
            except:
                self.logger("def loadCashFlow(self)", "завантаження", self.filename, log_write=True)
            
            self.ui.progressBar.setValue(int(((i+1)/len(self.filenames))*100))
            time.sleep(0.01)
            i += 1
        self.ui.progressBar.setValue(0)
        self.show_message("Повідомлення", "Завантаження файлів завершено")

    def readTableData(self):
        '''
        Функція для зчитування даних з інтерфейсу програми
        '''
        rowCount =  self.ui.tableWidget.rowCount()
        columnCount = self.ui.tableWidget.columnCount()
        rowDatas = []
        for row in range(rowCount):
            rowData = ''
            for column in range(columnCount):
                widgetItem = self.ui.tableWidget.item(row, column)
                if (widgetItem and widgetItem.text):
                    rowData = rowData + '~' + widgetItem.text()
                else:
                    rowData = rowData + '~' + 'nan'
            rowDatas.append(list(rowData.split('~')))
        return rowDatas

    def processingTableData(self):
        '''
        Функція обробки файлів csv з метою додавання правильної інформації про фігуранта через виклик функції
        DataHub().executor()
        '''
        rowDatas = self.readTableData()
        i = 1
        for rowData in rowDatas:
            if rowData[3] != 'Помилка під час завантаження' and rowData[3] != 'Помилка під час обробки' and rowData[3] != 'Помилка під час аналізу' and rowData[3] != 'Помилка під час отримання даних':
                try:
                    DataHub(self, div_table=rowData[2], cents=rowData[3], fig_acc=rowData[4], file_path=rowData[5], key_index=rowData[6]).executor()
                except:
                    self.logger("def processingTableData(self)", "обробки", rowData[1], log_write=True)
                    
            self.ui.progressBar.setValue(int(((i+1)/len(rowDatas))*100))
            time.sleep(0.01)
            i += 1
        self.ui.progressBar.setValue(0)
        self.show_message("Повідомлення", "Завантаження в БАЗУ завершено")
        return rowDatas

    def analyseCashFlow(self):
        '''
        Функція створення xlsx файлу через виклик CashFlowAnalysis().executor()
        '''
        # i = 1
            # try:
        CashFlowAnalysis("database.db").executor()
            # except:
            #     self.logger("def analyseCashFlow(self)", "аналізу", file_path, log_write=True)

        # self.ui.progressBar.setValue(int(((i+1)/len(os.listdir("./csv")))*100))
        # time.sleep(0.01)
        # i += 1
        self.ui.progressBar.setValue(0)
        self.show_message("Повідомлення", "Конвертацію в XLSX завершено")

def application():
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    application()
