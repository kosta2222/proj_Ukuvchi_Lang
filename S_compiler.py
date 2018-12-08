#-*-coding: utf-8-*-
import libTestPydModuleFloatRegister as vt #libTestPydModuleFloatRegister-байт-интерпритатор как расширение C для Python
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


def func_vmPrintStack_SvectorKfloatKI(par_vectorKfloatK_stack, par_I_count) :
    print("stack=[");
    for  i in range(0,par_I_count):
        print(" {0}".format(par_vectorKfloatK_stack[i]));
    
    print(" ]\n");

def func_vmPrintInstr_SvectorKintKIrV(vectorKintK_opCode) :
    print("Compiller")
    int_ip=0
    for _ in range(0,len(vectorKintK_opCode)):
      int_opcode =vectorKintK_opCode[int_ip]
      print(int_opcode)
      listKstrYintK_instr = listKstrK_opcodes[int_opcode];
      int_nargs=listKstrYintK_instr[1]
      int_ip+=1 
      print("int_ip:",int_ip)      
      if (int_nargs==0) :
        
            print("%d:  %s\n"%( int_ip,listKstrYintK_instr[0] ));

      elif (int_nargs==1) :
            if (int_opcode==ICONST):
                print ("%d:  ICONST <double>\n"%int_ip)
                int_ip+=4
                continue
            else:    
                print("%d:  %s %d\n" %(int_ip, listKstrYintK_instr[0],vectorKintK_opCode[int_ip+1]))
                int_ip=+1
                break
            
      elif (int_nargs==2) :
        print("%d:  %s %d %d\n"%(int_ip, listKstrYintK_instr[0],vectorKintK_opCode[int_ip+1],vectorKintK_opCode[int_ip+2] ))
        break
            
      elif (int_nargs==3) :
        print("%d:  %s %d %d %d\n"%(int_ip, listKstrYintK_instr[0],vectorKintK_opCode[int_ip+1],vectorKintK_opCode[int_ip+2],vectorKintK_opCode[int_ip+3] ))
        break
      
            
    

#import pdb
#pdb.set_trace()
import sys
import re
isa = isinstance
Symbol = str
def load_file(fName):
    fContent=open(fName).read()
    return fContent
def op_prior(str_char_op):
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
    if c=="-" or c=="+" or c=="*" or c=="/" or c=="%"or c=="^" :return True
    return False
def opn(str_code): 
    int_ptr=0
    listKstrK_OpStack=[]
    listKintOrStr_resOpnZapis=[]
    while (int_ptr<len(str_code)): 
        v=str_code[int_ptr]
        int_ptr+=1
        if isa(v,float):
            listKintOrStr_resOpnZapis.append(v)
        elif re.match("[A-Za-z]+",str(v)): 
            listKintOrStr_resOpnZapis.append(v)            
        elif isOp(v):
                while(len(listKstrK_OpStack)>0 and 
                listKstrK_OpStack[-1]!="[" and 
                op_prior(v)<=op_prior(listKstrK_OpStack[-1]) ):
                    listKintOrStr_resOpnZapis.append(listKstrK_OpStack.pop())
                 
                listKstrK_OpStack.append(v)       
        elif v==']':
            while len(listKstrK_OpStack)>0:
                x=listKstrK_OpStack.pop()
                if x=='[':
                    break
                listKintOrStr_resOpnZapis.append(x)
        elif v=="[":
            listKstrK_OpStack.append(v)                                                          
    while len(listKstrK_OpStack)>0 :
           listKintOrStr_resOpnZapis.append(listKstrK_OpStack.pop())
    return listKintOrStr_resOpnZapis 
def floatToBytes_SfloatRbytes(float_val):
    return pack('>f',float_val)
class LispMach:
 def __init__(self):   
  self.pole_dictKstrYintK_funcTable={}
  self.pole_vectorKintK_b_c=[]
  self.pole_int_startIp=0
  self.pole_int_nargs=0
 def method_genB_C_IrV(self,int_command):
     self.pole_vectorKintK_b_c.append(int_command)
 def method_recurs_evalPerList_LrV(self,vectorKintOrStrK):
    #print(vectorKintOrStrK)
    if isa(vectorKintOrStrK, Symbol) : 
        return vectorKintOrStrK
    elif not isa(vectorKintOrStrK, list):
        self.method_genB_C_IrV(ICONST)
        self.method_genB_C_IrV(vectorKintOrStrK)
        return vectorKintOrStrK 
    elif vectorKintOrStrK[0] == '//':
        pass
    elif vectorKintOrStrK[0] == 'set!':           # (set! var exp)
        (_, var, exp) = vectorKintOrStrK
        self.method_recurs_evalPerList_LrV(exp)
        self.method_genB_C_IrV(STORE)
        int_ordLocToStore=ord(var)-ord("a")
        self.method_genB_C_IrV(int_ordLocToStore)
    elif vectorKintOrStrK[0] == 'setResult!':           # (set! var exp)
        (_, var) = vectorKintOrStrK
        self.method_genB_C_IrV(STORE_RESULT)
        int_ordLocToStoreRegistr=ord(var)-ord("a")
        self.method_genB_C_IrV(int_ordLocToStoreRegistr)        
    elif vectorKintOrStrK[0] == 'define':         # (define var exp)
        (_, var, exp) = vectorKintOrStrK
        env[var] = method_recurs_evalPerList_LrV(exp)         
    elif vectorKintOrStrK[0] == 'defun':         # (lambda (var*) exp)
        (_,str_nameFunc, list_arg,list_expr) = vectorKintOrStrK
        if str_nameFunc=='main':
            self.pole_int_startIp=len(self.pole_vectorKintK_b_c)
        else:  
            self.pole_dictKstrYintK_funcTable[str_nameFunc]=len(self.pole_vectorKintK_b_c)
        self.method_recurs_evalPerList_LrV(list_arg)    
        self.method_recurs_evalPerList_LrV(list_expr)
        
           
    elif vectorKintOrStrK[0] == '$':          # (begin exp*)
        for exp in vectorKintOrStrK[1:]:
            val = self.method_recurs_evalPerList_LrV(exp)
        return val
    elif vectorKintOrStrK[0]=='return':
        self.method_genB_C_IrV(RET)        
        
    elif vectorKintOrStrK[0] == 'arif':
        listKintOrStr_resOpnZapis=opn(vectorKintOrStrK[1:])
        for i in listKintOrStr_resOpnZapis:
            if isOp(i):
                if i=="+": 
                    self.method_genB_C_IrV(IADD)
                if i=="-":
                    self.method_genB_C_IrV(ISUB)
                if i=="*":
                    self.method_genB_C_IrV(IMUL)
                if i=="/": 
                    self.method_genB_C_IrV(IDIV)  
                if i=="%":
                    self.method_genB_C_IrV(IREM)
                if i=="^": 
                    self.method_genB_C_IrV(IPOW)     
            elif re.match("[A-Za-z]+",str(i)):
                if str(i)!='z':
                  self.method_genB_C_IrV(LOAD)
                  self.method_genB_C_IrV(ord(i)-ord("a"))
                else:
                    self.method_genB_C_IrV(LOAD_RESULT)
            elif isa(i,float):
                self.method_genB_C_IrV(ICONST)
                for i1 in floatToBytes_SfloatRbytes(i):
                    self.method_genB_C_IrV(i1)
    elif vectorKintOrStrK[0] == 'print':
        for str_temp_BukvaKakChislo in vectorKintOrStrK[1:]:  
          self.method_genB_C_IrV(PRINT)
          self.method_genB_C_IrV(ord(str_temp_BukvaKakChislo)-ord('a'))
    elif vectorKintOrStrK[0] == 'call':
        (_,str_nameFunctionToCallFromMainFunction,list_args)=vectorKintOrStrK
        int_nameFunctionToCallFromMainFunction=self.pole_dictKstrYintK_funcTable[str_nameFunctionToCallFromMainFunction]
        print(int_nameFunctionToCallFromMainFunction)
        self.method_recurs_evalPerList_LrV(list_args)
        self.method_genB_C_IrV(CALL)
        self.method_genB_C_IrV(int_nameFunctionToCallFromMainFunction)
        self.method_genB_C_IrV(self.pole_int_nargs)
    elif vectorKintOrStrK[0]=='<':
        (_,list_arif1,list_arif2)=vectorKintOrStrK
        self.method_recurs_evalPerList_LrV(list_arif1)
        self.method_recurs_evalPerList_LrV(list_arif2)
        self.method_genB_C_IrV(ILT)
    elif vectorKintOrStrK[0]=='=':
        (_,list_arif1,list_arif2)=vectorKintOrStrK
        self.method_recurs_evalPerList_LrV(list_arif1)
        self.method_recurs_evalPerList_LrV(list_arif2)
        self.method_genB_C_IrV(IEQ)        
    elif vectorKintOrStrK[0]=='if':
        (_,list_test,list_trueEpr,list_falseExpr)=vectorKintOrStrK
        self.method_recurs_evalPerList_LrV(list_test)
        self.method_genB_C_IrV(BRF)
        int_addr1=len(self.pole_vectorKintK_b_c)
        self.method_genB_C_IrV(0)
        self.method_recurs_evalPerList_LrV(list_trueEpr)
        self.method_genB_C_IrV(BR)
        int_adr2=len(self.pole_vectorKintK_b_c)
        self.method_genB_C_IrV(0)
        self.pole_vectorKintK_b_c[int_addr1]=len(self.pole_vectorKintK_b_c)
        self.method_recurs_evalPerList_LrV(list_falseExpr)
        self.pole_vectorKintK_b_c[int_adr2]=len(self.pole_vectorKintK_b_c)
    elif vectorKintOrStrK[0]=='while':
        (_,list_test,list_whileBody)=vectorKintOrStrK
        int_addr1=len(self.pole_vectorKintK_b_c)
        self.method_recurs_evalPerList_LrV(list_test)
        self.method_genB_C_IrV(BRF)
        int_addr2=len(self.pole_vectorKintK_b_c)
        self.method_genB_C_IrV(0)
        self.method_recurs_evalPerList_LrV(list_whileBody)
        self.method_genB_C_IrV(BR)
        self.method_genB_C_IrV(int_addr1)
        self.pole_vectorKintK_b_c[int_addr2]=len(self.pole_vectorKintK_b_c)
        
    elif vectorKintOrStrK[0] == 'params':
        j=0
        for i in vectorKintOrStrK[1:]:
            self.method_genB_C_IrV(LOAD)
            self.method_genB_C_IrV(j)
            self.method_genB_C_IrV(STORE)
            self.method_genB_C_IrV(ord(i)-ord('a'))
            j+=1
    elif vectorKintOrStrK[0] == 'args':
        j=0
        for i in vectorKintOrStrK[1:]:
            if  isa(i,float): 
                self.method_genB_C_IrV(ICONST)
                for i1 in floatToBytes_SfloatRbytes(i):
                    self.method_genB_C_IrV(i1)                
            elif isa(i,str):
                self.method_genB_C_IrV(LOAD)
                self.method_genB_C_IrV(int(ord(i)-ord("a")))
            j+=1
        self.pole_int_nargs=j
    elif vectorKintOrStrK[0]=='pass':
        self.method_genB_C_IrV(NOOP)
            
   
        
 def method_retB_C_VrL(self):   
    return self.pole_vectorKintK_b_c
 def __str__(self):
     return "func_table:"+str(self.pole_dictKstrYintK_funcTable)+"\nvectorKintOrStrK:"+\
      "\nvector<int>_b_c:"+str(self.pole_vectorKintK_b_c)+"\nstart_ip:"+str(self.pole_int_startIp)    
     
        
def read(s):
    #"Read a Scheme expression from a string."
    return read_from(tokenize(s))
 
def tokenize(s):
    #"Convert a string into a list of tokens."
    return s.replace('(',' ( ').replace(')',' ) ').split()
 
def read_from(tokens):
    #"Read an expression from a sequence of tokens."
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
    #"Numbers become numbers; every other token is a symbol."
    try: return float(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)
 
def to_string(exp):
    #"Convert a Python object back into a Lisp-readable string."
    return '('+' '.join(map(to_string, exp))+')' if isa(exp, list) else str(exp)
 
def repl(prompt='lis.py> '):
    #"A prompt-read-method_recurs_evalPerList_LrV-print loop."
    obj_LispMach=LispMach()
    while True:
        val = obj_LispMach.method_recurs_evalPerList_LrV(parse(input(prompt)))
        if val is not None: print (to_string(val))
        print(obj_LispMach)    
parse=read        
def from_file(coContent):
  obj_LispMach=LispMach()  
  obj_LispMach.method_recurs_evalPerList_LrV(parse(coContent))
  return obj_LispMach.method_retB_C_VrL()
class Context:
    classIvokingContext_invokingContext=None
    metadata=None
    returnIp=0
    locals_=[]
    
    def __init__(self,
        int_returnip):
        self.int_returnip=int_returnip
        self.locals_=[0]*(26)
    def __str__(self):
        return "locals:" + str(self.locals_)
        
  

str_fileName=sys.argv[1] 
obj_fileDescr=open(str_fileName,"r")
obj_LispMach=LispMach()
str_textProgram=obj_fileDescr.read()
obj_LispMach.method_recurs_evalPerList_LrV(parse(str_textProgram))
vectorKintK_opCode=obj_LispMach.method_retB_C_VrL()
vectorKintK_opCode.append(HALT)
print(obj_LispMach)
func_vmPrintInstr_SvectorKintKIrV(vectorKintK_opCode)
float_retVal=vt.eval(vectorKintK_opCode,obj_LispMach.pole_int_startIp,0) 
print(float_retVal)
