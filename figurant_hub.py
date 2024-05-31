from file_reader import FileReader
import re

class FigurantHub(FileReader):
    def __init__(self, filename):
        super().__init__(filename)
        self.fig_acc = str()

    def get_acc_list(self):
        try:
            if len(self.fig_acc[0][0])==0:
                self.fig_acc = self.fig_acc[0][1]
            else:
                self.fig_acc = self.fig_acc[0][0]
        except:
            pass
        return self.fig_acc
    
    def getter_fig_acc(self):
        self.fig_acc = re.findall(r'.*(UA\d{27}).*|.*(\d{14}).*', self.filename)

        if len(self.fig_acc)==0:
            self.fig_acc = re.findall(r'.*(UA\d{27}).*|.*(\d{14}).*', self.element)
        
        self.get_acc_list()
        
        return self.fig_acc

    def exe_getter_fig_acc(self):
        i = 0
        for self.row in super().file_reader():
            for self.index, self.element in enumerate(self.row):
                super().formatting_element()
                try:
                    super().getter_colname()
                except:
                    pass
                
                if len(self.fig_acc)==0:
                    try:
                        self.getter_fig_acc()
                    except:
                        pass
            
            # super().setter_maincol()
            
            i += 1
            if i==21 or (len(self.fig_acc)>0 and len(self.key_index)==len(self.row)):
                break
        
        super().setter_maincol()
        return self.fig_acc
    

# list_of_col_standard_columns = {'КОРЕСПОНДЕНТ':         {"Банк":    {"Дата":    ["КОРЕСПОНДЕНТ:"],
#                                                                     "Документ": ["КОРЕСПОНДЕНТ:"]
#                                                                     },
                                                                    
#                                                         "Тип":      {"Дата":    ["КОРЕСПОНДЕНТ:"],
#                                                                      "Час":     ["КОРЕСПОНДЕНТ:"]
#                                                                     },
                                                        
#                                                         "Дата д-та":    {"Дата д-та":["Кореспондент:"]
#                                                                         },
#                                                         },

#                                 'Призначення платежу':  {"Банк":    {"Дата":    ["ПРИЗНАЧЕННЯ:"],
#                                                                     "Документ": ["ПРИЗНАЧЕННЯ:"]
#                                                                     },

#                                                         "Тип":      {"Дата":    ["ПРИЗНАЧЕННЯ:"],
#                                                                      "Час":     ["ПРИЗНАЧЕННЯ:"]
#                                                                     },

#                                                         "Дата д-та":    {"Дата д-та":["Призначення:"]
#                                                                         },
#                                                         },
                                        
#                                 'Найменування банка':   {"Банк":    {"Дата":    ["БАНК:|КОРЕСПОНДЕНТ:"],
#                                                                     "Документ": ["БАНК:|КОРЕСПОНДЕНТ:"]
#                                                                     },
                                                        
#                                                         "Тип":      {"Час":     ["НАДАВАЧ ПЛАТІЖНИХ ПОСЛУГ::"]
#                                                                     },
                                                        
#                                                         "Дата д-та":    {"Дата д-та":["Банк кор-та:"]
#                                                                         },
#                                                         },
                                
#                                 'Банк:Номер карты':     {"Дата док":    {"Дата док":[" : "]
#                                                                         },
#                                                         },
#                                         }
