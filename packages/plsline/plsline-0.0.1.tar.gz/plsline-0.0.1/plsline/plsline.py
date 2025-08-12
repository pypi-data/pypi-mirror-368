
"""Add decoration to print"""
from inspect import (
                    currentframe, 
                    getfile,
                    )
import re
import os
from time import sleep
os.system("")      
        
        
# 文字数を数える関数
def count_characters(var):
    return len(str(var))
def c_i(var):
    return len(str(var))        
        
#モノクロ用                
class printmonochrome:
    """
    {directory} {file_name}{line_number}{type}{var_name}{var}
    
    """
    def __init__(self, 
        print_normal_content="",
        print_normal_content_sub="",
        print_normal_content_three="",
        view_print= True, 
        line_fast_int  = 2,
        line_end_int   = 0,
        line_int = 3,           
        max_file_int = 20,
        max_varname_int = 30,
        max_type_int = 9,
        encoding='utf-8',
        sleep_time = 0,
         ):

        if view_print:  #trueの場合のみ表示
            self.sleep_time = sleep_time
            self.encoding = encoding
            self.line_int = line_int
            self.line_end_int  =  line_end_int
            self.line_all_int  = max_file_int
            self.varname_line_int = max_varname_int
            self.print_normal_content = print_normal_content
            self.print_normal_content_sub = print_normal_content_sub
            self.print_normal_content_three = print_normal_content_three

            self.page_list = []
            self.page_all_list = []
            
            #lineの設定
            self.frame = currentframe()
            self.current_frame = self.frame.f_back
            self.line_fast_int  = line_fast_int
            
            self.caller_frame = self.frame.f_back
            self.line_number_int = self.caller_frame.f_lineno
            self.line_number = str(self.line_number_int).zfill(4) # 先頭に0を追加して4桁に調整  
            self.file_path = getfile(self.current_frame)
            #typeの設定
            self.type_int = max_type_int
            self.content_type = type(print_normal_content).__name__ 
            self.line_type = "".join(["-" for _ in range(self.type_int - len(self.content_type))])            
            self.type_int = len(self.content_type) + len(self.line_type)
            self.df_check_is = False
            self.list_check_is = False
            self.dict_check_is = False
            
            if self.content_type == "DataFrame":
                self.df_check_is =  True
            if self.content_type == "list":
                self.list_check_is =  True                
            # if self.content_type == "dict":
            #     self.dict_check_is =  True       
                
            self.set_line()
            self.get_var_name()
            
            if len(self.varname) > self.varname_line_int:
                self.varname = self.varname[:self.varname_line_int]
            self.linevarname = "".join(["-" for _ in range(self.varname_line_int - len(self.varname))])
            
            self.printlinestart()   

    def set_line(self):     #-を作る場所        
        self.line = "".join(["-" for _ in range(self.line_int)])
        self.linefast = "".join(["-" for _ in range(self.line_fast_int)])
        self.lineend  = "".join(["-" for _ in range(self.line_end_int)])
        self.len_print_normal_content = len(str(self.print_normal_content))
        
        self.total_line_int =c_i(self.file_path) + c_i(self.line_number) + c_i(self.linefast) 
        self.tyousei_line_int = self.line_all_int - self.total_line_int
        
        self.tyousei_line = "".join(["-" for _ in range(self.tyousei_line_int)])
        


    def get_var_name(self):
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as file:
                current_line = 1
                for line in file:
                    if current_line == self.line_number_int:
                        self.page_list.append(line.strip())
                    current_line += 1
        except FileNotFoundError:
            self.page_list.append("None")
        except Exception as e:
            self.page_list.append("None")

        def make_var_name(start_char='(', end_char=[',',')']):
            try:
                self.page_list = self.page_list[0]
                start_idx = self.page_list.index(start_char)
                end_idx = float('inf')
                for char in end_char:
                    position = self.page_list.find(char, start_idx)
                    if position != -1 and position < end_idx:
                        end_idx = position        
                        self.varname = self.page_list[start_idx + 1:end_idx]
            except ValueError:
                self.varname = "None"
        make_var_name()

    def printlinestart(self):
        self.file_path = self.file_path[- self.line_all_int : ]   
        if re.search(r'\b(DataFrame)\b', str(self.content_type)):
            print(f"{self.linefast }{self.file_path}{self.tyousei_line}-{self.line_number}{self.line}{self.content_type}{self.line_type}{self.varname}{self.linevarname}{self.lineend}",end = '\n')           
            print(self.print_normal_content)
            if not self.print_normal_content_sub == "":
                print(self.print_normal_content_sub)
            if not self.print_normal_content_three == "":
                print(self.print_normal_content_three)
            
        elif self.list_check_is:    #listの場合改行する
            list_content = [f"{self.linefast }{self.line_number}{self.line}{i:04d}--{type(item).__name__}---{str(item)}" for i, item in enumerate(self.print_normal_content, 0)]
            print(f"{self.linefast }{self.file_path}{self.tyousei_line}-{self.line_number}{self.line}{self.content_type}{self.line_type}{self.varname}{self.linevarname}---{self.lineend}",end = '\n') 
            print("\n".join(list_content))
            if not self.print_normal_content_sub == "":
                print(self.print_normal_content_sub)
            if not self.print_normal_content_three == "":
                print(self.print_normal_content_three)

        else:   #通常の場合.
            print(f"{self.linefast }{self.file_path}{self.tyousei_line}-{self.line_number}{self.line}{self.content_type}{self.line_type}{self.varname}{self.linevarname}---{self.print_normal_content}{self.print_normal_content_sub}{self.print_normal_content_three}{self.lineend}",end = '\n') 

        sleep(self.sleep_time)


#color用を作る
class printcolor:
    """
    {directory} {file_name}{line_number}{type}{var_name} {var}
    
    """
    def __init__(self, 
        print_normal_content="",
        print_normal_content_sub="",
        print_normal_content_three="",
        view_print= True, 
        line_fast_int  = 2,
        line_end_int   = 0,
        line_int = 3,           
        line_all_int = 20,
        var_name_line_int = 30,
        max_type_int = 9,
        encoding='utf-8',
        sleep_time = 0,
        color = "white",
        color_back = "black", 
        colorreset = "\033[0m",
        help = False,        
        
         ):

        if view_print:  #trueの場合のみ表示
            self.sleep_time = sleep_time
            self.encoding = encoding
            self.line_int = line_int
            self.line_end_int  =  line_end_int
            self.line_all_int  = line_all_int
            self.varname_line_int = var_name_line_int
            self.print_normal_content = print_normal_content
            self.print_normal_content_sub = print_normal_content_sub
            self.print_normal_content_three = print_normal_content_three
            self.page_list = []
            self.page_all_list = [] 
            
            #lineの設定
            self.frame = currentframe()
            self.current_frame = self.frame.f_back
            self.line_fast_int  = line_fast_int
            
            self.caller_frame = self.frame.f_back
            self.line_number_int = self.caller_frame.f_lineno
            self.line_number = str(self.line_number_int).zfill(4) # 先頭に0を追加して4桁に調整  
            self.file_path = getfile(self.current_frame)  
            
            #typeの設定
            self.type_int = max_type_int
            self.content_type = type(print_normal_content).__name__ 
            self.line_type = "".join(["-" for _ in range(self.type_int - len(self.content_type))])            
            self.type_int = len(self.content_type) + len(self.line_type)
            self.df_check_is = False
            self.list_check_is = False
            self.dict_check_is = False
            
            if self.content_type == "DataFrame":
                self.df_check_is =  True
            if self.content_type == "list":
                self.list_check_is =  True                
            # if self.content_type == "dict":
            #     self.dict_check_is =  True   
            
            self.color_codes = {
                "black": "\033[30m",
                "red": "\033[31m",
                "green": "\033[32m",
                "yellow": "\033[33m",
                "blue": "\033[34m",
                "magenta": "\033[35m",
                "cyan": "\033[36m",
                "white": "\033[37m",
                "reset": "\033[0m",

                "b": "\033[30m",
                "r": "\033[31m",
                "g": "\033[32m",
                "y": "\033[33m",
                "bl": "\033[34m",
                "m": "\033[35m",
                "c": "\033[36m",
                "w": "\033[37m",   
                "r": "\033[0m",             
                
            }
            self.color_codes_back = {
                "black": "\033[40m",
                "red": "\033[41m",
                "green": "\033[42m",
                "yellow": "\033[43m",
                "blue": "\033[44m",
                "magenta": "\033[45m",
                "cyan": "\033[46m",
                "white": "\033[47m",
                "reset": "\033[0m",

                "b": "\033[40m",
                "r": "\033[41m",
                "g": "\033[42m",
                "y": "\033[43m",
                "bl": "\033[44m",
                "m": "\033[45m",
                "c": "\033[46m",
                "w": "\033[47m",
                "r": "\033[0m",
            }

            self.line_color = self.color_codes[color]
            line_color_back = self.color_codes_back[color_back]    #経由するとできるから分けている
            self.line_color_back = line_color_back
            self.colorreset = colorreset
            self.help_color_codes = help

            self.set_line()
            self.get_var_name()
            if len(self.varname) > self.varname_line_int:
                self.varname = self.varname[:self.varname_line_int]
            self.linevarname = "".join(["-" for _ in range(self.varname_line_int - len(self.varname))])
            self.printlinestart()  
    
    def set_line(self):     #-を作る場所        
        self.line = "".join(["-" for _ in range(self.line_int)])
        self.linefast = "".join(["-" for _ in range(self.line_fast_int)])
        self.lineend  = "".join(["-" for _ in range(self.line_end_int)])
        self.len_print_normal_content = len(str(self.print_normal_content))
        
        self.total_line_int =c_i(self.file_path) + c_i(self.line_number) + c_i(self.linefast) 
        self.tyousei_line_int = self.line_all_int - self.total_line_int
        
        self.tyousei_line = "".join(["-" for _ in range(self.tyousei_line_int)])

    def get_var_name(self):
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as file:
                current_line = 1
                for line in file:
                    if current_line == self.line_number_int:
                        self.page_list.append(line.strip())
                    current_line += 1
        except FileNotFoundError:
            self.page_list.append("None")
        except Exception:
            self.page_list.append("None")
        
        def make_var_name(start_char='(', end_char=[',',')']):
            try:
                self.page_list = self.page_list[0]
                start_idx = self.page_list.index(start_char)
                end_idx = float('inf')
                for char in end_char:
                    position = self.page_list.find(char, start_idx)
                    if position != -1 and position < end_idx:
                        end_idx = position        
                        self.varname = self.page_list[start_idx + 1:end_idx]
            except ValueError:
                self.varname = "None"
        make_var_name()
        
    def printlinestart(self):
        self.file_path = self.file_path[- self.line_all_int : ]
        #DataFrameの場合は特別な処理をする
        if re.search(r'\b(DataFrame)\b', str(self.content_type)):
            print(self.line_color,end = "")
            print(self.line_color_back,end = "")

            print(f"{self.linefast }{self.file_path}{self.tyousei_line}-{self.line_number}{self.line}{self.content_type}{self.line_type}{self.varname}{self.linevarname}{self.lineend}",end = '\n')             
            print(self.print_normal_content)
            if not self.print_normal_content_sub == "":
                print(self.print_normal_content_sub)
            if not self.print_normal_content_three == "":
                print(self.print_normal_content_three)
            print(self.colorreset,end = '\n')
            
        elif self.list_check_is:    #listの場合改行する
            print(self.line_color,end = "")
            print(self.line_color_back,end = "")
            
            list_content = [f"{self.linefast }{self.line_number}{self.line}{i:04d}--{type(item).__name__}---{str(item)}" for i, item in enumerate(self.print_normal_content, 0)]
            print(f"{self.linefast }{self.file_path}{self.tyousei_line}-{self.line_number}{self.line}{self.content_type}{self.line_type}{self.varname}{self.linevarname}---{self.lineend}",end = '\n') 
            print("\n".join(list_content))
            if not self.print_normal_content_sub == "":
                print(self.print_normal_content_sub)
            if not self.print_normal_content_three == "":
                print(self.print_normal_content_three)
            print(self.colorreset,end = '\n')
            
        else:   #通常の場合.
            if self.print_normal_content =="" and self.print_normal_content_sub == "" and self.help_color_codes:
                    print("Foreground Colors:")
                    for color, code in self.color_codes.items():
                        print(f"\033[0m{code}{color}: {color}\033[0m")
                    print("\nBackground Colors:")
                    for color, code in self.color_codes_back.items():
                        print(f"\033[0m{code}{color}: {color}\033[0m")     
            else:                   
                print(self.line_color_back,end = "")
                print(self.line_color,end = "")
                print(f"{self.linefast }{self.file_path}{self.tyousei_line}-{self.line_number}{self.line}{self.content_type}{self.line_type}{self.varname}{self.linevarname}---{self.print_normal_content}{self.print_normal_content_sub}{self.print_normal_content_three}{self.lineend}{self.colorreset}",end = '\n') 

        sleep(self.sleep_time)


#シンプルなのを作る
class printsimple:
    """
    {line_number}{type}{var_name} {var}
    
    """
    def __init__(self, 
        print_normal_content="",
        print_normal_content_sub="",
        print_normal_content_three="",
        view_print= True, 
        line_int = 3, 
        max_type_int = 9,
        sleep_time = 0,
         ):
        if view_print:  #trueの場合のみ表示
            self.sleep_time = sleep_time
            #lineの設定
            self.frame = currentframe()
            self.caller_frame = self.frame.f_back
            self.line_number_int = self.caller_frame.f_lineno
            self.line_number = str(self.line_number_int).zfill(4) # 先頭に0を追加して4桁に調整  
            self.line = "".join(["-" for _ in range(line_int)])
            
            #typeの設定
            self.type_int = max_type_int
            self.content_type = type(print_normal_content).__name__ 
            self.line_type = "".join(["-" for _ in range(self.type_int - len(self.content_type))])            
            self.type_int = len(self.content_type) + len(self.line_type)
            self.df_check_is = False
            self.list_check_is = False
            self.dict_check_is = False
            if self.content_type == "DataFrame":
                self.df_check_is =  True
            if self.content_type == "list":
                self.list_check_is =  True                
            # if self.content_type == "dict":
            #     self.dict_check_is =  True   
            
            if re.search(r'\b(DataFrame)\b', str(self.content_type)):
                print(f"--{self.line_number}{self.line}{self.content_type}",end = '\n')           
                print(print_normal_content)
                if not print_normal_content_sub == "":
                    print(print_normal_content_sub)
                if not print_normal_content_three == "":
                    print(print_normal_content_three)
            
            if self.list_check_is: 
                list_content = [f"--{self.line_number}{self.line}{i:04d}--{type(item).__name__}---{str(item)}" for i, item in enumerate(print_normal_content, 0)]
                print(f"{self.line_number}{self.line}{self.content_type}----------",end = '\n') 
                print("\n".join(list_content))
                if not print_normal_content_sub == "":
                    print(print_normal_content_sub)
                if not print_normal_content_three == "":
                    print(print_normal_content_three)
                    
            else:
                print(f"--{self.line_number}{self.line}{self.content_type}--{print_normal_content}{print_normal_content_sub}{print_normal_content_three}")    
                
        sleep(self.sleep_time)
                
                
                
                