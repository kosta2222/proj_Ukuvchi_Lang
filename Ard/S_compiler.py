"""
   Считываем из консоли программу,
   компилируем ее, и после ввода буквы "E" отправляем 
   программу на устройство  
"""

#*****************************Compiller********************************
"""
   Представлены больше байт-кодов, чем реализованы
"""
from struct import pack,unpack
(   NOOP    ,#0
    IADD    ,#1
    ISUB    ,#2
    IMUL    ,#3
    IDIV    ,#4
    IREM    ,#5
    IPOW    ,#6
    ILT     ,#7
    IEQ     ,#8
    BR      ,#9
    BRT     ,#10
    BRF     ,#11
    ICONST  ,#12
    LOAD    ,#13
    GLOAD   ,#14
    STORE   ,#15
    GSTORE  ,#16
    PRINT   ,#17
    POP     ,#18
    CALL    ,#19
    RET     ,#20
    STORE_RESULT,#21
    LOAD_RESULT,#22
    INVOKE_BY_ORDINAL,#23
    CREATE_STRING,#24
    NEWARRAY,#25
    IASTORE,#26
    IALOAD,#27
    DUP,#28
    ASTORE,#29
    ALOAD,#30
    INVOKE,#31
    STOP,#32

    blink_red_led, #33
    turn_on_relay #34
)=range(35)

import re

isa = isinstance
Symbol = str

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
        Перевод в обратную польскую запись
        @param str_code строка инфиксного выражения 
        @return список  постфиксного выражения
    """

    item_i=0
    # Операндовый стек
    OperatStack=[]
    # Выходной список
    resOpn=[]

    while (item_i<len(str_code)):

        # получить следующий член выражения  
        v=str_code[item_i]
        item_i+=1
        # определить тип члена
        if isa(v,int):

            resOpn.append(v)
        elif re.match("[A-Za-z]+",str(v)):

            resOpn.append(v)
        elif isOp(v):

                while(len(OperatStack)>0 and
                OperatStack[-1]!="[" and
                op_prior(v)<=op_prior(OperatStack[-1]) ):
                    resOpn.append(OperatStack.pop())

                OperatStack.append(v)
        elif v==']':

            while len(OperatStack)>0:

                x=OperatStack.pop()
                if x=='[':

                    break
                resOpn.append(x)
        elif v=="[":
            OperatStack.append(v)
    while len(OperatStack)>0 :

           resOpn.append(OperatStack.pop())

    return resOpn

def shortToBytes(int_val):
    """
        запаковать число как набор байт
    """

    return pack('h',int_val)

class Compiller:
 """
       Компилятор
 """

 def __init__(self):
 
      self.byteCode=[]
      self.startIp=0

      """
           Для формирования индекса переменной
      """
      self.nglobals=0

      """
          карта name => index
      """
      self.globals={}
 
 def generate(self,int_command):
     """"
          генерация байткода
          @param int_command добавляем число в список
     """

     self.byteCode.append(int_command)

 def varIndexByName(self,_name):
   """
       Находит индекс переменной в глобальной карте
       @param _name имя переменной
       @return кортеж индекс и лейбл карты
   """
   """
       Просматриваем карту
   """
   for pair in self.globals.items():

      if pair[0]==_name:

          return (pair[1],'G') 
      else:

          print("Undefined var:%s"%_name)
          exit(1)
         
           
 def compille(self,SExp):
    """
         рекурсивный разбор S-выражения SExp -список с числами и строками
         @param SExp список S-выражения
                  
    """
    """
         S-выражение(Symbolyc expression) выражение вида:
         (<имя функции> <параметр-число> <параметр число> ... <другое S-выражение>:=(<имя функции>  <параметр-число> <параметр число> ...) )
    """
    """
       Всегда узнаем первый член выражения
    """
    """
       Распаковываем список.
       Генерируем соответствующий байт-код.
    """  
    if  isa(SExp[0], int):# Это число

        self.generate(ICONST)
        self.byteCode.extend(shortToBytes(SExp[0]))

    elif SExp[0] == '//': # Это комментарии

        pass

    elif SExp[0] == 'set!': # создаем глобальную переменную

        (_, var, exp) = SExp

        self.compille(exp)
        self.generate(GSTORE)
       
        """
          Глобальная переменная не определена, поэтому создаем ее
        """
        if self.globals.get(var)==None:

          index=self.nglobals 
          self.generate(index)
          
          self.globals[var]=index
          self.nlobals+=1

        else:
           """
              Глобальная переменная определена, поэтому извлекаем ее (индекс)
           """

           self.generate(self.globals.get(var))
             
   
    elif SExp[0] == '$': # выполнить выражения слева направо

        for exp in SExp[1:]:

            val = self.compille(exp)
          
    elif SExp[0] == 'arif': # Это арифметическое выражение

        resOpn=opn(SExp[1:]) # из инфиксной записи в ОПЗ
        """
          Заменяем в списке операции и индификаторы переменных(на индексы)
        """
        for i in resOpn:

            if isOp(i):

                if i=="+":

                    self.generate(IADD)
                if i=="-":

                    self.generate(ISUB)
                if i=="*":

                    self.generate(IMUL)
                if i=="/":

                    self.generate(IDIV)
                if i=="%":

                    self.generate(IREM)
                if i=="^":

                    self.generate(IPOW)
            elif re.match("[a-z]+",str(i)):# Если это строковый индификатор 

                  indexAndLocation=self.varIndexByName(i)

                  if indexAndLocation[1]=='G':

                    self.generate(GLOAD)
                 
                  # Индекс 
                  self.generate(indexAndLocation[0])                   
   
    elif SExp[0]=='<':# сравнить на меньше

        (_,list_arif1,list_arif2)=SExp

        self.compille(list_arif1)
        self.compille(list_arif2)
        self.generate(ILT)

    elif SExp[0]=='=':# сравнить на равенство

        (_,list_arif1,list_arif2)=SExp

        self.compille(list_arif1)
        self.compille(list_arif2)
        self.generate(IEQ)

    elif SExp[0]=='if':# если

        (_,list_test,list_trueEpr,list_falseExpr)=SExp

        self.compille(list_test)
        self.generate(BRF)
        self.generate(0)
        self.generate(0)
        nAddr0_1=len(self.byteCode)
        self.compille(list_trueEpr)
        self.generate(BR)
        self.generate(0)
        self.generate(0)
        nAddr1_2=len(self.byteCode)
        delta1=nAddr1_2-nAddr0_1
        self.byteCode[nAddr0_1-2]=shortToBytes(delta1)[0]
        self.byteCode[nAddr0_1-1]=shortToBytes(delta1)[1]
        self.compille(list_falseExpr)
        nAddr3_4=len(self.byteCode)
        delta2=(nAddr3_4-nAddr1_2)+2
        self.byteCode[nAddr1_2-2]=shortToBytes(delta2)[0]
        self.byteCode[nAddr1_2-1]=shortToBytes(delta2)[1]

    elif SExp[0]=='while': # пока

        (_,list_test,list_whileBody)=SExp

        nAddr1_2=len(self.byteCode)
        self.compille(list_test)
        self.generate(BRF)
        self.generate(0)
        self.generate(0)
        nAddr0_1=len(self.byteCode)
        self.compille(list_whileBody)
        self.generate(BR)
        self.generate(0)
        self.generate(0)
        nAddr2_3=len(self.byteCode)
        delta1=nAddr2_3-nAddr0_1
        delta2=(nAddr2_3-nAddr1_2)-2
        self.byteCode[nAddr0_1-2]=shortToBytes(delta1)[0]
        self.byteCode[nAddr0_1-1]=shortToBytes(delta1)[1]
        self.byteCode[nAddr2_3-2]=shortToBytes(-delta2)[0]
        self.byteCode[nAddr2_3-1]=shortToBytes(-delta2)[1]

    elif SExp[0]=='pass': # ничего не делать

        self.generate(NOOP)

    else: # ошибка компиляции

        raise Exception("Unknown function name:%s"%SExp[0])


 def bytecode(self):
    """
         Возвращает результирующий байт код для ВМ
    """

    return self.byteCode

#*****************************End Compiller********************************

#*****************************Вспомогательные функции**********************
def read(s):
    """
        Читает lisp подобное выражение из строки и лексемазирует его
    """

    return read_from(tokenize(s))

def tokenize(s):
    """
         Ковертирует строку в питон список, токены
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
       Числа становятся числами int , остальное символами,строками
    """

    try: return int(token)
    except ValueError:
        try: return int(token)
        except ValueError:
            return Symbol(token)

#*****************************Вспомогательные функции**********************

#**********************Программа******************************************

from serial import Serial,SerialException,EIGHTBITS,PARITY_NONE

import time

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='cmplr.log', filemode='w',
                        level=logging.DEBUG)

SERIAL_PORT='COM7'
SERIAL_SPEED=9600
ser=Serial()
ser.port=SERIAL_PORT
ser.baudrate=SERIAL_SPEED
ser.bytesize = EIGHTBITS   #number of bits per bytes
ser.timeout = 1            #non-block read
ser.writeTimeout = 2       #timeout for write
ser.xonxoff = False        #disable software flow control
ser.rtscts = False         #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False         #disable hardware (DSR/DTR) flow control

try:
      """
         Пытаемся открыть серийный порт
      """
      ser.open()

except SerialException as e:

      logger.debug("error open serial port: " + str(e))

      exit()

Compiller=Compiller()

def inpt_program():
  """
    Считываем строку пользователя и отправляем бат-код в устройство
  """ 

  str_textProgram=''

  while True:

      us_input=input('Ukuvchi>>>') # получаем конкретную строку исходной программы

      if us_input=='Quit':

         break
       
      if us_input!='E':
         """
            Текст программы
         """
         str_textProgram+=us_input

      else:
           """
                Компиляция и отправка программы на устройство
           """ 
           Compiller.compille(read(str_textProgram)) # анализируем исходный код программы в компиляторе
           bytecode=Compiller.bytecode()
           bytecode+=[STOP]

           logger.debug("by-co list:%s"%(str(bytecode)))
           logger.debug("glob map:%s"%str(Compiller.globals))
           r=ser.write(bytes(bytecode))
           logger.debug("ser r:%d",r) 
           time.sleep(0.5) 

           while True:
             """ 
                  Считываем то что вернуло устройство
             """
             exit_out=ser.readline()
             logger.debug(exit_out)

             if exit_out==b'STOP VM\n':

                break
      
  ser.close()

import sys

if __name__=='__main__':
   
   inpt_program()

#***********************End Программа****************************


