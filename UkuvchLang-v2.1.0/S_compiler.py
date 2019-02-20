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
                          Замечание о системе.
                          При опкоде RET восстанавливается ip и затирается индекс callsp.
                          Можно состояние стека сохранить в регистр и когда например в арифметическом выражении встречается
                          буква z, это означает команду ВМ загрузить на стек регистр для возращающего значения.
"""
#import libTestPydModuleFloat as vt
#*****************************Compiller********************************
from struct import pack,unpack
(   NOOP    ,
    FADD    , 
    FSUB    ,
    FMUL    ,
    FDIV    ,
    IREM    ,
    FPOW    ,
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
    INVOKE_BY_ORDINAL,
    CREATE_STRING,
    NEWARRAY,
    IASTORE,
    IALOAD,
    DUP,
    ASTORE,
    ALOAD,
    INVOKE,
    STOP    
)=range(33)
#import pdb
#pdb.set_trace()
import sys
import re
import math
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
    return pack('<f',float_val)

def shortToBytes_SintRbytes(int_val):
    """
        запаковать число как набор байт
    """    
    return pack('>H',int_val)

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
  self.nCountMethods=0
  self.me_gen_byteCode_SIrV(0)
  self.me_gen_byteCode_SIrV(0)
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
    #print(mas_I_Or_Str)
    if isa(mas_I_Or_Str, Symbol) : 
        pack(mas_I_Or_Str,'s')
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
    elif mas_I_Or_Str[0] == 'setResult!':  # сохранить с вершины стека в регистр 
        (_,var)=mas_I_Or_Str
        self.me_gen_byteCode_SIrV(STORE_RESULT) 
        int_ordLocToStore=ord(var)-ord("a") # определим индекс буквы
        self.me_gen_byteCode_SIrV(int_ordLocToStore)        
    elif mas_I_Or_Str[0] == 'defun': #определить функцию 
        self.nCountMethods+=1
        (_,str_nameFunc, list_arg,body_expr) = mas_I_Or_Str
        argStrLen=len(str_nameFunc) + 1 # + 1 для 0-завершителя строки
        self.me_gen_byteCode_SIrV(argStrLen)
        byteArrStr=bytearray(str_nameFunc,'cp1251')
        for i in byteArrStr:
            self.me_gen_byteCode_SIrV(i)
            
        self.me_gen_byteCode_SIrV(0) # 0 - завершитель строки
        
        self.me_gen_byteCode_SIrV(0)
        self.me_gen_byteCode_SIrV(0)
        nAddr1=len(self.fi_mas_I_byteCode)
        self.me_recurs_evalPerList_SMrV(list_arg)    
        self.me_recurs_evalPerList_SMrV(body_expr) 
        if str_nameFunc=='main':
            self.me_gen_byteCode_SIrV(STOP)
        nByteCodeMethodLen=len(self.fi_mas_I_byteCode)-(nAddr1)
        
        self.fi_mas_I_byteCode[nAddr1-2]=shortToBytes_SintRbytes(nByteCodeMethodLen)[0]
        self.fi_mas_I_byteCode[nAddr1-1]=shortToBytes_SintRbytes(nByteCodeMethodLen)[1]        
       
        
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
                    self.me_gen_byteCode_SIrV(FADD)
                if i=="-":
                    self.me_gen_byteCode_SIrV(FSUB)
                if i=="*":
                    self.me_gen_byteCode_SIrV(FMUL)
                if i=="/": 
                    self.me_gen_byteCode_SIrV(FDIV)  
                if i=="%":
                    self.me_gen_byteCode_SIrV(IREM)
                if i=="^": 
                    self.me_gen_byteCode_SIrV(FPOW)     
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
    elif mas_I_Or_Str[0]=='invoke_by_ordinal': # вызвать нативную функцию
        (_,funcid)=mas_I_Or_Str
        self.me_recurs_evalPerList_SMrV(funcid)
        self.me_gen_byteCode_SIrV(INVOKE_BY_ORDINAL)
    elif  mas_I_Or_Str[0]=='invoke':
        print('invoke')
        (_,func_name,list_args)=mas_I_Or_Str  
        self.me_recurs_evalPerList_SMrV(list_args)
        self.me_gen_byteCode_SIrV(INVOKE)
        argStrLen=len(func_name) + 1 # + 1 для 0 - завершителя строки
        self.me_gen_byteCode_SIrV(argStrLen)
        byteArrStr=bytearray(func_name,'cp1251')
         
        for i in byteArrStr:
            self.me_gen_byteCode_SIrV(i)
            
        self.me_gen_byteCode_SIrV(0) # 0 - завершитель строки    
        self.me_gen_byteCode_SIrV(self.fi_int_nargs)    
        
    elif mas_I_Or_Str[0]=='create_string': # создаем строку 
        (_,argStr)= mas_I_Or_Str
        self.me_gen_byteCode_SIrV(CREATE_STRING)
        self.me_gen_byteCode_SIrV(argStr)
    elif mas_I_Or_Str[0]=='newarray': # создаем массив в куче некоторой длины
        (_,arrLen)=mas_I_Or_Str
        self.me_recurs_evalPerList_SMrV(arrLen)
        self.me_gen_byteCode_SIrV(NEWARRAY)
    elif mas_I_Or_Str[0]=='iastore': # записываем значение элемента массива
        (_,index,val)=mas_I_Or_Str
        self.me_recurs_evalPerList_SMrV(index)
        self.me_recurs_evalPerList_SMrV(val)
        self.me_gen_byteCode_SIrV(IASTORE)
    elif mas_I_Or_Str[0]=='iaload': # грузит значение элемента из массива 
        self.me_gen_byteCode_SIrV(IALOAD)
    elif mas_I_Or_Str[0]=='dup': # дублируем вершину стека
        self.me_gen_byteCode_SIrV(DUP)
    elif mas_I_Or_Str[0]=='setObj!':
        """
        setObj! выражает ASTORE байт-код, который сохраняет обьект(массив например) в переменную
        """
        (_,indf,arrayObj)=mas_I_Or_Str
        self.me_recurs_evalPerList_SMrV(arrayObj)
        self.me_gen_byteCode_SIrV(ASTORE)
        self.me_gen_byteCode_SIrV(ord(indf)-ord("a"))
    elif mas_I_Or_Str[0]=='getObj!': # грузит обьект-массив на стек
        """
        getObj! выражает ALOAD байт-код, который грузит ссылку обьекта(массив например) на стек
        """
        (_,indf)=mas_I_Or_Str
        self.me_gen_byteCode_SIrV(ALOAD)
        self.me_gen_byteCode_SIrV(ord(indf)-ord("a"))        
        
    elif mas_I_Or_Str[0]=='pass': # ничего не делать
        self.me_gen_byteCode_SIrV(NOOP)
        
    else: # ошибка компиляции
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

#******************Py Vm**********************************************
#"""
#Информация о байт-кодов для трассы
#"""
#listKstrK_opcodes=[
            #["NOOP",0]    ,
                    #["FADD",0]    ,
                    #["FSUB",0]    ,
                    #["FMUL",0]    ,
                    #["FDIV",0]    ,
                    #["IREM",0]    ,
                    #["FPOW",0]    ,
                    #["ILT",0]     ,   
                    #["IEQ",0]     ,   
                    #["BR",1]      ,   
                    #["BRT",1]     ,   
                    #["BRF",1]     ,  
                    #["ICONST",1]  ,   
                    #["LOAD",1]    , 
                    #["GLOAD",1]   ,  
                    #["STORE",1]   ,  
                    #["GSTORE",1]  ,  
                    #["PRINT",1]   ,  
                    #["POP",0]     ,  
                    #["CALL",2]    ,  
                    #["RET",0]     ,  
                    #["STORE_RESULT",0],
                    #["LOAD_RESULT",0],
                    #["INVOKE_BY_ORDINAL",0],
                    #["CREATE_STRING",0],
                    #["NEWARRAY",0], # создать массив по длине
                    #["IASTORE",0],  # записать число в массив
                    #["IASTORE",0],  # загрузить целое из массива целых
                    #["DUP",0],      # дублировать вершину стека
                    #["ASTORE",0],   # сохранить обьект
                    #["ALOAD",0],    # загрузить обьект(ссылку) на стек
                    #["HALT",0]        
        #] 
#def func_vmPrintStack_SvectorKfloatKI(par_vectorKfloatK_stack, par_I_count) :
            #"""
            #Отпечатываем стек
            #"""
            #print("stack=[");
            #for  i in range(0,par_I_count):
                #print(" {0}".format(par_vectorKfloatK_stack[i]));
        
            #print(" ]\n");
        
        
#def func_vmPrintInstr_SvectorKintKIrV(vectorKintK_opCode, int_ip) :
            #"""
            #Отпечатывает байт-код с аргументами для трассы
            #"""
            #int_opcode =vectorKintK_opCode[int_ip];
            #listKstrYintK_instr = listKstrK_opcodes[int_opcode];
            #int_nargs=listKstrYintK_instr[1]
            #if (int_nargs==0) :
        
                #print("%d:  %s\n"%( int_ip,listKstrYintK_instr[0] ));
        
            #elif (int_nargs==1 and int_opcode!=ICONST) :
                #print("%d:  %s %d\n" %(int_ip, listKstrYintK_instr[0],vectorKintK_opCode[int_ip+1]) )
            #elif (int_nargs==1 and int_opcode==ICONST):
                #bytearray_bAr=bytearray([vectorKintK_opCode[int_ip+1],vectorKintK_opCode[int_ip+2],vectorKintK_opCode[int_ip+3],vectorKintK_opCode[int_ip+4]])
                #print("ICONST",unpack('>f',bytearray_bAr)[0])       
        
        
            #elif (int_nargs==2) :
                #print("%d:  %s %d %d\n"%(int_ip, listKstrYintK_instr[0],vectorKintK_opCode[int_ip+1],vectorKintK_opCode[int_ip+2] ) )
        
            #elif (int_nargs==3) :
                #print("%d:  %s %d %d %d\n"%(int_ip, listKstrYintK_instr[0],vectorKintK_opCode[int_ip+1],vectorKintK_opCode[int_ip+2],vectorKintK_opCode[int_ip+3] ))
        
#class Context:
            #"""
            #Контекст(как фрейм) для функций
            #"""
            #classIvokingContext_invokingContext=None
            #metadata=None
            #returnIp=0
            #locals_=[]
        
            #def __init__(self,int_returnip):
                #self.int_returnip=int_returnip
                #self.locals_=[0]*(26)
            #def __str__(self):
                #return "locals:" + str(self.locals_)
        
#def  call_user(funcid,argc,argv):
            #"""
            #Вызывает пользвательскую функцию
            #\param funcid:int индификатор
            #\param argc:int количество параметров
            #\param argv:list аргументы со стека
            #\return соответствующее значение
            #"""
        
            #ret = 0;      
        
            #if (funcid == 0): 
                #print("Called user function 0 => stop.\n");
        
        
            #if (funcid == 1):
                #ret = math.cos(argv[-1]);
        
            #if (funcid == 2): 
                #ret = math.sin(argv[-1]);
        
            #print("Called user function %d with %d args:"%( funcid, argc));
            #for i in range(0,argc):
                #print(" %f"%argv[i]);
        
        
            #print("\n");
            #return ret;
        
        
        
#class Vm:
            #code=[]
            #a=0
            #b=0
            #steck=[]
            #ip=0
            #sp=-1
            #pole_float_registrThatRetFunc=0.0
            #trace=False
            #globals_=[]
        
        
            #def __init__(self,code,trace=False):
                #self.code=code
                #self.globals_=[0]*26
                #self.steck=[0]*100
                #self.pole_vectorKclassContextK_funcCont=[Context(0)]*40
                #print("vector<Context>:",self.pole_vectorKclassContextK_funcCont[0])
                #self.trace=trace
                #self.pole_float_registrThatRetFunc=0.0
                ## элементы heap
                #self.heap=[]
                #self.heap_next_id=0
            #def add_to_heap(self,heapObj):
                #"""
                #Метод принимает обьект например список и добавляет в список и возвращает ключ
                #"""
                #ref=self.heap_next_id
                #self.heap.append(heapObj)
                #self.heap_next_id+=1
                #return ref
            #def createStringObj(self,strPar_S):
                #"""
                #Создать строковый обьект в Python heap и вернуть ссылку на него, чтобы положить ее на стек
                #"""
                #newStrObj=str(strPar_S)
                #ref=self.add_to_heap(newStrObj)
                #return ref  
            #def createArray(self,arrLen_I):
                #"""
                #Создать массив в Python heap и вернуть ссылку на него, чтобы положить ее на стек
                #"""
                #newArr=[0]*int(arrLen_I)
                ## ложим обьект в кучу
                #ref=self.add_to_heap(newArr)
                #return ref    
        
            #def exec_(self,startip):
                #self.ip=startip
                #self.cpu() 
        
            #def cpu(self):
                #opcode=-1
                #I_callSp=-1
        
                #while (self.ip<len(self.code) and opcode!=HALT):
                    #opcode=self.code[self.ip] # выборка байт-кода 
        
                    #if self.trace: # вывод трассы если нужно
                        #print("number opcode:",opcode)
                        #func_vmPrintInstr_SvectorKintKIrV(self.code,self.ip)
        
                    #if (opcode==ICONST):# декодируем
                        #self.sp+=1
                        #bytearray_bAr=bytearray([self.code[self.ip+1],self.code[self.ip+2],self.code[self.ip+3],self.code[self.ip+4]])
                        #self.steck[self.sp]=unpack('>f',bytearray_bAr)[0]
                        #self.ip+=4
                    #elif opcode==GSTORE:# работаем с глобальными переменными - сохраням их
                        #v=self.steck[self.sp]
                        #self.sp-=1
                        #self.ip+=1
                        #addr=self.code[self.ip]
                        #self.globals_[addr]=v 
        
                    #elif opcode==GLOAD:# работаем с глобальными переменными - грузим их
                        #self.ip+=1
                        #addr=self.code[self.ip]
                        #v=self.globals_[addr]
                        #self.sp+=1
                        #self.steck[self.sp]=v 
                    #elif opcode==NOOP: # ничего не делаем
                        #pass
        
                    #elif opcode==HALT: # остановка ВМ
                        #break
                    #elif opcode==BR: # безусловный переход
                        #self.ip+=1
                        #self.ip=self.code[self.ip]
                        #continue
                    #elif opcode==BRT:
                        #self.ip+=1
                        #addr=self.code[self.ip]
                        #if self.steck[self.sp]==1: # если True
                            #self.ip=addr
                            #self.sp-=1 
                            #continue  
                    #elif opcode==BRF:
                        #self.ip+=1
                        #addr=self.code[self.ip]
                        #if self.steck[self.sp]==0: # если False
                            #self.ip=addr
                            #self.sp-=1 
                            #continue
                    #elif opcode==FADD:
                        #b=self.steck[self.sp]
                        #self.sp-=1
                        #a=self.steck[self.sp]
                        #self.sp-=1
                        #self.sp+=1
                        #self.steck[self.sp]=a+b
                    #elif opcode==FSUB:
                        #b=self.steck[self.sp]
                        #self.sp-=1
                        #a=self.steck[self.sp]
                        #self.sp-=1
                        #self.sp+=1
                        #self.steck[self.sp]=a-b 
                    #elif opcode==FMUL:
                        #b=self.steck[self.sp]
                        #self.sp-=1
                        #a=self.steck[self.sp]
                        #self.sp-=1
                        #self.sp+=1
                        #self.steck[self.sp]=a*b 
                    #elif opcode==FDIV:
                        #b=self.steck[self.sp]
                        #self.sp-=1
                        #a=self.steck[self.sp]
                        #self.sp-=1
                        #self.sp+=1
                        #self.steck[self.sp]=a/b  
                    #elif opcode==ILT:
                        #b=self.steck[self.sp]
                        #self.sp-=1
                        #a=self.steck[self.sp]
                        #self.sp-=1
                        #if a<b:
                            #self.sp+=1 
                            #self.steck[self.sp]=1#True 
                        #else:
                            #self.sp+=1
                            #self.steck[self.sp]=0#False 
                    #elif opcode==IEQ:
                        #b=self.steck[self.sp]
                        #self.sp-=1
                        #a=self.steck[self.sp]
                        #self.sp-=1
                        #if a==b:
                            #self.sp+=1 
                            #self.steck[self.sp]=1#True 
                        #else:
                            #self.sp+=1
                            #self.steck[self.sp]=0#False              
                    #elif opcode==PRINT:   
                        #self.ip+=1
                        #int_chisloIzLocalnihKakParametr=self.code[self.ip]
                        #if int_chisloIzLocalnihKakParametr!=25:
                            #print("print loc:",self.pole_vectorKclassContextK_funcCont[I_callSp].locals_[int_chisloIzLocalnihKakParametr])
                        #else:
                            #print("print ret reg:%f"%self.pole_float_registrThatRetFunc)         
                    #elif opcode==LOAD:
                        #self.ip+=1
                        #regnum=self.code[self.ip]
                        #self.sp+=1
                        #self.steck[self.sp]=self.pole_vectorKclassContextK_funcCont[I_callSp].locals_[regnum] 
                    #elif opcode==STORE:
                        #self.ip+=1
                        #regnum=self.code[self.ip]
                        #self.pole_vectorKclassContextK_funcCont[I_callSp].locals_[regnum]=self.steck[self.sp]
                        #self.sp-=1 
                    #elif opcode==STORE_RESULT: # сохраняем с вершины стека в регистр
                        #self.pole_float_registrThatRetFunc=self.steck[self.sp]
                        #self.sp-=1   
                    #elif opcode==LOAD_RESULT: # сохранить с регистра в стек, буква z будет
                        #self.sp+=1
                        #self.steck[self.sp]=self.pole_float_registrThatRetFunc                                
                    #elif opcode==CALL:
                        #self.ip+=1
                        #I_findex=self.code[self.ip]
                        #self.ip+=1
                        #I_nargs=self.code[self.ip]
                        #I_callSp+=1
                        #classContext_curContext=self.pole_vectorKclassContextK_funcCont[I_callSp]
                        #classContext_curContext.returnIp=self.ip+1
                        #I_firstarg=self.sp-I_nargs+1
                        #for i in range(0,I_nargs):
                            #classContext_curContext.locals_[i]=self.steck[I_firstarg+i]
                            #self.sp-=I_nargs
                            #self.ip=I_findex
                        #continue
                    #elif opcode==RET:
                        #self.ip=self.pole_vectorKclassContextK_funcCont[I_callSp].returnIp
                        #I_callSp-=1
                        #continue
                    #elif opcode==INVOKE_BY_ORDINAL: # вызов по ординалу
                        ## берем id функции из стека
                        #arg=int(self.steck[self.sp]) 
                        #self.sp-=1
                        ## берем количество аргументов
                        #argc=int(self.steck[self.sp])
                        #self.sp-=1
                        ## список параметров, чтобы передать
                        #argv=[] 
                        ## заполняем список параметро
                        #for i in range(0,argc):
                            #argv.append(self.steck[self.sp])
                            #self.sp-=1       
                        ## вызываем функцию
                        #a=call_user(arg,argc,argv)
                        ## если число параметров не равно 0, то записываем в регистр 
                        #if (argc!=0):
                            #self.pole_float_registrThatRetFunc=a
                    ## ВМ создает строку 
                    #elif opcode==CREATE_STRING:
                        #self.ip+=1
                        #arg=self.code[self.ip]
                        #strRef=self.createStringObj(arg)
                        #self.sp+=1
                        #self.steck[self.sp]=strRef
                    ## ВМ создает массив беря его длину из своего стека
                    #elif opcode==NEWARRAY:
                        #arrLenFromStack=self.steck[self.sp]
                        #self.sp-=1
                        #arrRef=self.createArray(arrLenFromStack)
                        #self.sp+=1
                        #self.steck[self.sp]=arrRef
                    ## ВМ берет со своего стека индекс для записи в обьект массив, затем значение, и в 
                    ## индификатор heap записывает данные
                    #elif opcode==IASTORE:
                        #heapKey=self.steck[self.sp-2]
                        #print('in Vm:iastore heapKey ->',heapKey)
                        #self.heap[heapKey][int(self.steck[self.sp-1])]=self.steck[self.sp]
        
                        #self.sp-=3 
                    #elif opcode==IALOAD:
                        ## arrayref в стеке - обеспечивается текстом программы getObject!
                        #heapKey=self.steck[self.sp-1]
                        ## берем нужный индекс со стека - обеспечивается тем что после getObject! ложится число как нужный индекс
                        #needIndex=self.steck[self.sp]
        
                        ## на место arrayref в стеке записываем элемент-значение массива из кучи
                        #self.steck[int(self.sp-1)]=self.heap[int(heapKey)][int(needIndex)]
        
                        #print('in Vm:iaload value from array ->',self.steck[self.sp-1])
        
                        #self.sp-=1
        
                    ## дублирование верхушки стека
                    #elif opcode==DUP:
                        #self.steck[self.sp+1]=self.steck[self.sp]
                        #self.sp+=1
                    ## сохраним обьект(например массив) в локальной переменной
                    #elif opcode==ASTORE:
                        #self.ip+=1
                        #varnum=self.code[self.ip]
                        #self.pole_vectorKclassContextK_funcCont[I_callSp].locals_[varnum]=self.steck[self.sp]
                        #self.sp-=1
                    ## грузит ссылку обьекта(например массива) на стек    
                    #elif opcode==ALOAD: 
                        #self.ip+=1
                        #varnum=self.code[self.ip] 
                        #self.sp+=1
                        #self.steck[self.sp]=self.pole_vectorKclassContextK_funcCont[I_callSp].locals_[varnum]        
                    #else:
                        #raise Exception("invalid opcode:",opcode," at ip=",(self.ip))
                    #print('sp:%d top:%f'%(self.sp,self.steck[self.sp])) 
                    #func_vmPrintStack_SvectorKfloatKI(self.steck,10) 
                    #self.ip+=1                    
        
                    ##elif opcode==INC:
                        ##v=self.steck[self.sp]
                        ##v+=1
                        ##self.steck[self.sp]=v
                        ##elif opcode==DEC: 
                        ##v=self.steck[self.sp]
                        ##v-=1
                        ##self.steck[self.sp]=v
                    ##elif opcode==MOD:
                        ##b=self.steck[self.sp]
                        ##self.sp-=1
                        ##a=self.steck[self.sp]
                        ##self.sp-=1
                        ##self.sp+=1
                        ##self.steck[self.sp]=a%b 
                        ##elif opcode==ABI:
                        ##v=self.steck[self.sp]
                        ##self.steck[self.sp]=abs(v)
                    ##elif opcode==NEQ:#a != b ?
                        ##b=self.steck[self.sp]
                        ##self.sp-=1
                        ##a=self.steck[self.sp]
                        ##self.sp-=1
                        ##if a!=b:
                        ##self.sp+=1 
                        ##self.steck[self.sp]=TRUE#True 
                        ##else:
                        ##self.sp+=1
                        ##self.steck[self.sp]=FALSE#False   
                    ##elif opcode==LEQ:#a <= b ?
                        ##b=self.steck[self.sp]
                        ##self.sp-=1
                        ##a=self.steck[self.sp]
                        ##self.sp-=1
                        ##if a<=b:
                        ##self.sp+=1 
                        ##self.steck[self.sp]=TRUE#True 
                        ##else:
                        ##self.sp+=1
                        ##self.steck[self.sp]=FALSE#False    
                    ##elif opcode==EQU:#a == b ?
                        ##b=self.steck[self.sp]
                        ##self.sp-=1
                        ##a=self.steck[self.sp]
                        ##self.sp-=1
                        ##if a==b:
                        ##self.sp+=1 
                        ##self.steck[self.sp]=TRUE#True 
                        ##else:
                        ##self.sp+=1
                        ##self.steck[self.sp]=FALSE#False  
                    ##elif opcode==GEQ:#a == b ?
                        ##b=self.steck[self.sp]
                        ##self.sp-=1
                        ##a=self.steck[self.sp]
                        ##self.sp-=1
                        ##if a>=b:
                        ##self.sp+=1 
                        ##self.steck[self.sp]=TRUE#True 
                        ##else:
                        ##self.sp+=1
                        ##self.steck[self.sp]=FALSE#False 
#**********************End Py Vm********************************* 
def  writeObjectFile_sLrV(l_byteCode):
    """
    Функция записи из списка байт-кода в файл обьектной программы
    writeObjectFile_sLrV
    """ 
    objectProgramName='code.bin'
    with open(objectProgramName,'wb') as fileObj:
        for i in l_byteCode:
            oneBinData=pack('B',i)
            fileObj.write(oneBinData)
#**********************Программа********************************   
#import libproj_testVmWithSimpleHeap as vm 

obj_LispMach=LispMach() # заводим обьект компилятора

str_sourceFileName=sys.argv[1] # считываем в файловый обьект исходный текст программы из коммандной строки
fileDescr=open(str_sourceFileName,"r") # получаем файловый дескриптор для чтения исходной программы
str_textProgram=fileDescr.read() # получаем конкретную строку исходной программы 
obj_LispMach.me_recurs_evalPerList_SMrV(read(str_textProgram)) # анализируем исходный код программы в компиляторе
l_retBytecode=obj_LispMach.me_ret_byteCode_SVrL()
l_retBytecode[0]=shortToBytes_SintRbytes(obj_LispMach.nCountMethods)[0]
l_retBytecode[1]=shortToBytes_SintRbytes(obj_LispMach.nCountMethods)[1]
#l_retBytecode.append(HALT)
writeObjectFile_sLrV(l_retBytecode)
#vm.eval(l_retBytecode,obj_LispMach.fi_int_startIp,1)
#vectorKintK_opCode=obj_LispMach.me_ret_byteCode_SVrL()
#vectorKintK_opCode.append(HALT)
#obj_vm=Vm(vectorKintK_opCode,trace=True)
#obj_vm.exec_(obj_LispMach.fi_int_startIp)
## отпечатаем состояние Heap
#print('Heap: %s'%str(obj_vm.heap))
#***********************End Программа****************************


