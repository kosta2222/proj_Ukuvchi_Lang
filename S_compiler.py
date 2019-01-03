#-*-coding: utf-8-*-
"""
		Этот модуль - компилятор s-выражений выражений ,
		symbolic - expression просто говоря 2 скобки с данными ,
		данные это атомы т е числа и строки .
		Числа на этапе разделения на лексемы приводятся к типу float ,
		я решил , что виртуальная машина будет оперировать контейнером с
		float . Строки из букв в исходном тексте становятся литералами
		строк Python . Интерприттируются такие выражения так , первая
		строка идет как название функции , в ветках if-elif определяется
		что делать с такой функцией . Параметры ее - другие s - выражения могут
		передаваться рекурсивно компилятору , формируя байт-код для виртуальной машины .
                        О нотации индификаторов :
                        Для индификаторов переменных я попытался сделать наподобии Венгерской нотации т.е.
                        идет инфо о типе , потом семантический смысл переменной , например
                        str_char_op , int_ptr , mas_Str_OpStack означает массив с типом String ,
                        а mas_I_Or_Str_resOpnZapis список ( массив ) с типами Int или String .
                        Имена полей придваряются суффиксом fi ( field ) , например fi_dict_str_int_funcTable это
                        поле - карта с сключом Str , а значением Int .
                        Методы предваряются суффиксом me ( method ) . У функций и методов бывают сигнатуры в конце ,
                        после буквы S ( signature ) , т.е. какие типы функция / метод принимает , например
                        me_recurs_evalPerList_SMrV - метод recurs_evalPerList принимает M - массив / список ,
                        возвращае Пустое т.е V ( void ) . После буквы r ( Return ) идет возвращаемое 
                        функций / методом значение. I это всегда Int , D или F - вещественное число ,
                        Str - String.

"""
import libTestPydModuleFloat as vt
from struct import pack,unpack
(   NOOP    ,
    IADD    , 
    ISUB    ,
    IMUL    ,
    IDIV    ,
    IREM    ,
    IPOW    ,
    ILT     ,   
    IEQ     ,  
    BR      ,   
    BRT     ,   
    BRF     ,   
    ICONST  ,   
    LOAD    ,  
    GLOAD   ,  
    STORE   ,  
    GSTORE  ,  
    PRINT   ,  
    POP     ,  
    CALL    ,  
    RET     ,  
    STORE_RESULT,
    LOAD_RESULT,
    HALT    
)=range(24)


#import pdb
#pdb.set_trace()
import sys
import re
isa = isinstance
Symbol = str
  
def load_file(fName):
    """
       Считывает файл -исходнй текст проги,возвращает строку-выражение
    """     
    fContent=open(fName).read()
    return fContent
def op_prior(str_char_op):
    """
        Приоритет арифметической операции
    """    
    if str_char_op=="^":
        return 6
    elif str_char_op=="*":
        return 5
    elif str_char_op=="/":
        return 5
    elif str_char_op=="%":
        return 3
    elif str_char_op=="+":
        return 2
    elif str_char_op=="-":
        return 2 
def isOp(c):
    """
        Это арифметическая операция? 
    """     
    if c=="-" or c=="+" or c=="*" or c=="/" or c=="%"or c=="^" :return True
    return False
def opn(str_code):
    """
        Перевод в обратную польскую запись str_code-строка инфиксного выражения Ret список
    """    
    int_ptr=0
    mas_Str_OpStack=[]
    mas_I_Or_Str_resOpnZapis=[]
    while (int_ptr<len(str_code)): 
        v=str_code[int_ptr]
        int_ptr+=1
        if isa(v,float):
            mas_I_Or_Str_resOpnZapis.append(v)
        elif re.match("[A-Za-z]+",str(v)): 
            mas_I_Or_Str_resOpnZapis.append(v)            
        elif isOp(v):
                while(len(mas_Str_OpStack)>0 and 
                mas_Str_OpStack[-1]!="[" and 
                op_prior(v)<=op_prior(mas_Str_OpStack[-1]) ):
                    mas_I_Or_Str_resOpnZapis.append(mas_Str_OpStack.pop())
                 
                mas_Str_OpStack.append(v)       
        elif v==']':
            while len(mas_Str_OpStack)>0:
                x=mas_Str_OpStack.pop()
                if x=='[':
                    break
                mas_I_Or_Str_resOpnZapis.append(x)
        elif v=="[":
            mas_Str_OpStack.append(v)                                                          
    while len(mas_Str_OpStack)>0 :
           mas_I_Or_Str_resOpnZapis.append(mas_Str_OpStack.pop())
    return mas_I_Or_Str_resOpnZapis 
def floatToBytes_SfloatRbytes(float_val):
    """
        запаковать число как набор байт
    """    
    return pack('>f',float_val)
class LispMach:
 """
       Компилятор
 """    
 def __init__(self):
  """
       заводим карту для функций- <имя функции:индекс ее байткода>,индекс первой команды,которую нужно исполнять 
  """     
  self.fi_dict_str_int_funcTable={}
  self.fi_mas_I_byteCode=[]
  self.fi_int_startIp=0
  self.fi_int_nargs=0
 def me_gen_byteCode_SIrV(self,int_command):
     """"
          генерация байткода-int_command-опкод который нужно добавить для результирующего списка,для Vm
     """     
     self.fi_mas_I_byteCode.append(int_command)
 def me_recurs_evalPerList_SMrV(self,mas_I_Or_Str):
    """
         рекурсивный разбор s-выражения mas_I_Or_Str -список с числами и строками 
         как именами того какой байт-код генерировать
         смотря на аргумент self.method_genB_C_IrV можно понять синтаксис языка 
    """     
    print(mas_I_Or_Str)
    if isa(mas_I_Or_Str, Symbol) : 
        pass
    elif  isa(mas_I_Or_Str[0], float):# Это число
        self.me_gen_byteCode_SIrV(ICONST)
        for i1 in floatToBytes_SfloatRbytes(mas_I_Or_Str[0]):# расскладываем float число на байты 
            self.me_gen_byteCode_SIrV(i1)  # каждый байт записываем в выходной байт массив  
    elif mas_I_Or_Str[0] == '//': # Это комментарии
        pass
    elif mas_I_Or_Str[0] == 'set!': # записываем константу/выражение в индификатор
        (_, var, exp) = mas_I_Or_Str
        self.me_recurs_evalPerList_SMrV(exp)
        self.me_gen_byteCode_SIrV(STORE)
        int_ordLocToStore=ord(var)-ord("a") # определим индекс буквы
        self.me_gen_byteCode_SIrV(int_ordLocToStore)
    elif mas_I_Or_Str[0] == 'setResult!':  # сохранить из регистра возврата функций в некоторую переменную 
        (_, var) = mas_I_Or_Str
        self.me_gen_byteCode_SIrV(STORE_RESULT)
        int_ordLocToStoreRegistr=ord(var)-ord("a")
        self.me_gen_byteCode_SIrV(int_ordLocToStoreRegistr)               
    elif mas_I_Or_Str[0] == 'defun': #определить функцию          
        (_,str_nameFunc, list_arg,list_expr) = mas_I_Or_Str
        if str_nameFunc=='main':
            self.fi_int_startIp=len(self.fi_mas_I_byteCode)
        else:  
            self.fi_dict_str_int_funcTable[str_nameFunc]=len(self.fi_mas_I_byteCode)
        self.me_recurs_evalPerList_SMrV(list_arg)    
        self.me_recurs_evalPerList_SMrV(list_expr)
        
           
    elif mas_I_Or_Str[0] == '$': # выполнить выражения слева направо
        for exp in mas_I_Or_Str[1:]:
            val = self.me_recurs_evalPerList_SMrV(exp)
        return val
    elif mas_I_Or_Str[0]=='return': # завершить функцию
        self.me_gen_byteCode_SIrV(RET)     
    elif mas_I_Or_Str[0] == 'arif': # Это арифметическое выражение
        mas_I_Or_Str_resOpnZapis=opn(mas_I_Or_Str[1:]) # из инфиксной записи в ОПЗ 
        for i in mas_I_Or_Str_resOpnZapis:
            if isOp(i):
                if i=="+": 
                    self.me_gen_byteCode_SIrV(IADD)
                if i=="-":
                    self.me_gen_byteCode_SIrV(ISUB)
                if i=="*":
                    self.me_gen_byteCode_SIrV(IMUL)
                if i=="/": 
                    self.me_gen_byteCode_SIrV(IDIV)  
                if i=="%":
                    self.me_gen_byteCode_SIrV(IREM)
                if i=="^": 
                    self.me_gen_byteCode_SIrV(IPOW)     
            elif re.match("[a-z]+",str(i)):# Если это строковый индификатор и не есть z - загрузить его из локальных переменных 
                if str(i)!='z':
                  self.me_gen_byteCode_SIrV(LOAD)
                  self.me_gen_byteCode_SIrV(ord(i)-ord("a"))
                else:# если это z то згужаем с регистра
                    self.me_gen_byteCode_SIrV(LOAD_RESULT)
            elif isa(i,float):
                self.me_gen_byteCode_SIrV(ICONST)
                for i1 in floatToBytes_SfloatRbytes(i):
                    self.me_gen_byteCode_SIrV(i1)                    
    elif mas_I_Or_Str[0] == 'print':# отпечать букву - индидификатор
        for str_temp_BukvaKakChislo in mas_I_Or_Str[1:]:  
          self.me_gen_byteCode_SIrV(PRINT)
          self.me_gen_byteCode_SIrV(ord(str_temp_BukvaKakChislo)-ord('a'))
    elif mas_I_Or_Str[0] == 'call':# вызвать функцию
        (_,str_nameFunctionToCallFromMainFunction,list_args)=mas_I_Or_Str
        int_nameFunctionToCallFromMainFunction=self.fi_dict_str_int_funcTable[str_nameFunctionToCallFromMainFunction]
        print(int_nameFunctionToCallFromMainFunction)
        self.me_recurs_evalPerList_SMrV(list_args)
        self.me_gen_byteCode_SIrV(CALL)
        self.me_gen_byteCode_SIrV(int_nameFunctionToCallFromMainFunction)
        self.me_gen_byteCode_SIrV(self.fi_int_nargs)
    elif mas_I_Or_Str[0]=='<':# сравнить на меньше
        (_,list_arif1,list_arif2)=mas_I_Or_Str
        self.me_recurs_evalPerList_SMrV(list_arif1)
        self.me_recurs_evalPerList_SMrV(list_arif2)
        self.me_gen_byteCode_SIrV(ILT)
    elif mas_I_Or_Str[0]=='=':# сравнить на равенство
        (_,list_arif1,list_arif2)=mas_I_Or_Str
        self.me_recurs_evalPerList_SMrV(list_arif1)
        self.me_recurs_evalPerList_SMrV(list_arif2)
        self.me_gen_byteCode_SIrV(IEQ)        
    elif mas_I_Or_Str[0]=='if':# если
        (_,list_test,list_trueEpr,list_falseExpr)=mas_I_Or_Str
        self.me_recurs_evalPerList_SMrV(list_test)
        self.me_gen_byteCode_SIrV(BRF)
        int_addr1=len(self.fi_mas_I_byteCode)
        self.me_gen_byteCode_SIrV(0)
        self.me_recurs_evalPerList_SMrV(list_trueEpr)
        self.me_gen_byteCode_SIrV(BR)
        int_adr2=len(self.fi_mas_I_byteCode)
        self.me_gen_byteCode_SIrV(0)
        self.fi_mas_I_byteCode[int_addr1]=len(self.fi_mas_I_byteCode)
        self.me_recurs_evalPerList_SMrV(list_falseExpr)
        self.fi_mas_I_byteCode[int_adr2]=len(self.fi_mas_I_byteCode)
    elif mas_I_Or_Str[0]=='while': # пока
        (_,list_test,list_whileBody)=mas_I_Or_Str
        int_addr1=len(self.fi_mas_I_byteCode)
        self.me_recurs_evalPerList_SMrV(list_test)
        self.me_gen_byteCode_SIrV(BRF)
        int_addr2=len(self.fi_mas_I_byteCode)
        self.me_gen_byteCode_SIrV(0)
        self.me_recurs_evalPerList_SMrV(list_whileBody)
        self.me_gen_byteCode_SIrV(BR)
        self.me_gen_byteCode_SIrV(int_addr1)
        self.fi_mas_I_byteCode[int_addr2]=len(self.fi_mas_I_byteCode)
        
    elif mas_I_Or_Str[0] == 'params': # параметры функции
        j=0
        for i in mas_I_Or_Str[1:]:
            self.me_gen_byteCode_SIrV(LOAD)
            self.me_gen_byteCode_SIrV(j)
            self.me_gen_byteCode_SIrV(STORE)
            self.me_gen_byteCode_SIrV(ord(i)-ord('a'))
            j+=1
    elif mas_I_Or_Str[0] == 'args': # аргументы функции
        j=0
        for i in mas_I_Or_Str[1:]:
            if  isa(i,float): 
                self.me_gen_byteCode_SIrV(ICONST)
                for i1 in floatToBytes_SfloatRbytes(i):
                    self.me_gen_byteCode_SIrV(i1)                
            elif isa(i,str):
                self.me_gen_byteCode_SIrV(LOAD)
                self.me_gen_byteCode_SIrV(int(ord(i)-ord("a")))
            j+=1
        self.fi_int_nargs=j
    elif mas_I_Or_Str[0]=='callUserCos': # вызвать нативную функцию
        self.me_gen_byteCode_SIrV(26)
    elif mas_I_Or_Str[0]=='callUserSin': # вызвать нативную функцию
        self.me_gen_byteCode_SIrV(27)    
    elif mas_I_Or_Str[0]=='pass': # ничего не делать
        self.me_gen_byteCode_SIrV(NOOP)
    else:
        raise Exception("Unknown keyword %s"%mas_I_Or_Str[0])
            
   
        
 def me_ret_byteCode_SVrL(self):
    """
         Возвращает результирующий байт код для ВМ 
    """      
    return self.fi_mas_I_byteCode
 def __str__(self):
     """
          Возвращает строковое представление обьекта компилятора
     """     
     return "func_table:"+str(self.fi_dict_str_int_funcTable)+"\nmas_I_Or_Str:"+\
      "\nvector<int>_b_c:"+str(self.fi_mas_I_byteCode)+"\nstart_ip:"+str(self.fi_int_startIp)    
     
        
def read(s):
    """
        Читает lisp подобное выражение из строки и лексемазирует его 
    """     
    return read_from(tokenize(s))
 
def tokenize(s):
    """
         Ковертирует строку в питон список токенов
    """    
    return s.replace('(',' ( ').replace(')',' ) ').split()
 
def read_from(tokens):
    """
        Читает выражение,создает 'атомы' - float или строки
    """    
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)
 
def atom(token):
    """
       Числа становятся числами float , остальное символами,строками 
    """    
    try: return float(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)


 

str_fileName=sys.argv[1]
#str_fileName='./code_Arifm.lisp' 
fileDescr=open(str_fileName,"r")
obj_LispMach=LispMach()
str_textProgram=fileDescr.read()
print(str_textProgram)
obj_LispMach.me_recurs_evalPerList_SMrV(read(str_textProgram))
vectorKintK_opCode=obj_LispMach.me_ret_byteCode_SVrL()
vectorKintK_opCode.append(HALT)
print(obj_LispMach)
#obj_vm=Vm(vectorKintK_opCode,10,trace=True)
#obj_vm.exec_(obj_LispMach.pole_int_startIp)
float_retVal=vt.eval(vectorKintK_opCode,obj_LispMach.fi_int_startIp,0) 
print(float_retVal)