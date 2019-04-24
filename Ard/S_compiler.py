#-*-coding: cp1251-*-
"""
   ��������� �� ������� ���������,
   ����������� ��, � ����� ����� ����� "E" ���������� 
   ��������� �� ����������  
"""

#*****************************Compiller********************************
"""
   ������������ ������ ����-�����, ��� �����������
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
        ��������� �������������� ��������
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
        ��� �������������� ��������?
    """

    if c=="-" or c=="+" or c=="*" or c=="/" or c=="%"or c=="^" :return True
    return False

def opn(str_code):
    """
        ������� � �������� �������� ������
        @param str_code ������ ���������� ��������� 
        @return ������  ������������ ���������
    """

    int_ptr=0
    # ����������� ����
    OperatStack=[]
    # �������� ������
    resOpn=[]

    while (int_ptr<len(str_code)):

        # �������� ��������� ���� ���������  
        v=str_code[int_ptr]
        int_ptr+=1
        # ���������� ��� �����
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
        ���������� ����� ��� ����� ����
    """

    return pack('h',int_val)

class Compiller:
 """
       ����������
 """

 def __init__(self):
 
      self.byteCode=[]
      self.startIp=0

      """
           ��� ������������ ������� ����������
      """
      self.nglobals=0

      """
          ����� name => index
      """
      self.globals={}
 
 def generate(self,int_command):
     """"
          ��������� ��������
          @param int_command ��������� ����� � ������
     """

     self.byteCode.append(int_command)

 def varIndexByName(self,_name):
   """
       ������� ������ ���������� � ���������� �����
       @param _name ��� ����������
       @return ������ ������ � ����� �����
   """
   """
       ������������� �����
   """
   for pair in self.globals.items():

      if pair[0]==_name:

          return (pair[1],'G') 
      else:

          print("Undefined var:%s"%_name)
          exit(1)
         
           
 def compille(self,SExp):
    """
         ����������� ������ S-��������� SExp -������ � ������� � ��������
         @param SExp ������ S-���������
                  
    """
    """
         S-���������(Symbolyc expression) ��������� ����:
         (<��� �������> <��������-�����> <�������� �����> ... <������ S-���������>:=(<��� �������>  <��������-�����> <�������� �����> ...) )
    """
    """
       ������ ������ ������ ���� ���������
    """
    """
       ������������� ������.
       ���������� ��������������� ����-���.
    """  
    if  isa(SExp[0], int):# ��� �����

        self.generate(ICONST)
        self.byteCode.extend(shortToBytes(SExp[0]))

    elif SExp[0] == '//': # ��� �����������

        pass

    elif SExp[0] == 'set!': # ������� ���������� ����������

        (_, var, exp) = SExp

        self.compille(exp)
        self.generate(GSTORE)
       
        """
          ���������� ���������� �� ����������, ������� ������� ��
        """
        if self.globals.get(var)==None:

          index=self.nglobals 
          self.generate(index)
          
          self.globals[var]=index
          self.nlobals+=1

        else:
           """
              ���������� ���������� ����������, ������� ��������� �� (������)
           """

           self.generate(self.globals.get(var))
             
   
    elif SExp[0] == '$': # ��������� ��������� ����� �������

        for exp in SExp[1:]:

            val = self.compille(exp)
          
    elif SExp[0] == 'arif': # ��� �������������� ���������

        resOpn=opn(SExp[1:]) # �� ��������� ������ � ���
        """
          �������� � ������ �������� � ������������ ����������(�� �������)
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
            elif re.match("[a-z]+",str(i)):# ���� ��� ��������� ����������� 

                  indexAndLocation=self.varIndexByName(i)

                  if indexAndLocation[1]=='G':

                    self.generate(GLOAD)
                 
                  # ������ 
                  self.generate(indexAndLocation[0])                   
   
    elif SExp[0]=='<':# �������� �� ������

        (_,list_arif1,list_arif2)=SExp

        self.compille(list_arif1)
        self.compille(list_arif2)
        self.generate(ILT)

    elif SExp[0]=='=':# �������� �� ���������

        (_,list_arif1,list_arif2)=SExp

        self.compille(list_arif1)
        self.compille(list_arif2)
        self.generate(IEQ)

    elif SExp[0]=='if':# ����

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

    elif SExp[0]=='while': # ����

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

    elif SExp[0]=='pass': # ������ �� ������

        self.generate(NOOP)

    else: # ������ ����������

        raise Exception("Unknown function name:%s"%SExp[0])


 def bytecode(self):
    """
         ���������� �������������� ���� ��� ��� ��
    """

    return self.byteCode

#*****************************End Compiller********************************

#*****************************��������������� �������**********************
def read(s):
    """
        ������ lisp �������� ��������� �� ������ � ������������� ���
    """

    return read_from(tokenize(s))

def tokenize(s):
    """
         ����������� ������ � ����� ������, ������
    """

    return s.replace('(',' ( ').replace(')',' ) ').split()

def read_from(tokens):
    """
        ������ ���������,������� '�����' - float ��� ������
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
       ����� ���������� ������� int , ��������� ���������,��������
    """

    try: return int(token)
    except ValueError:
        try: return int(token)
        except ValueError:
            return Symbol(token)

#*****************************��������������� �������**********************

#**********************���������******************************************

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
         �������� ������� �������� ����
      """
      ser.open()

except SerialException as e:

      logger.debug("error open serial port: " + str(e))

      exit()

Compiller=Compiller()

def inpt_program():
  """
    ��������� ������ ������������ � ���������� ���-��� � ����������
  """ 

  str_textProgram=''

  while True:

      us_input=input('Ukuvchi>>>') # �������� ���������� ������ �������� ���������

      if us_input=='Quit':

         break
       
      if us_input!='E':
         """
            ����� ���������
         """
         str_textProgram+=us_input

      else:
           """
                ���������� � �������� ��������� �� ����������
           """ 
           Compiller.compille(read(str_textProgram)) # ����������� �������� ��� ��������� � �����������
           bytecode=Compiller.bytecode()
           bytecode+=[STOP]

           logger.debug("by-co list:%s"%(str(bytecode)))
           logger.debug("glob map:%s"%str(Compiller.globals))
           r=ser.write(bytes(bytecode))
           logger.debug("ser r:%d",r) 
           time.sleep(0.5) 

           while True:
             """ 
                  ��������� �� ��� ������� ����������
             """
             exit_out=ser.readline()
             logger.debug(exit_out)

             if exit_out==b'STOP VM\n':

                break
      
  ser.close()

import sys

if __name__=='__main__':
   
   inpt_program()

#***********************End ���������****************************


