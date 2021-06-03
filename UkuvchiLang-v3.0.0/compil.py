# --------------------------------------------------
#   Компилятор
# --------------------------------------------------
"""
   Представлены больше байт-кодов, чем реализованы
"""
from object_ import Object
import re
from struct import pack, unpack
from help_parse_funcs import read, isa
# from pyobj import Frame
from opcodes import *
import logging
import datetime
from enums import INT, FLOAT, STR, BOOLEAN, NONE, CODE, FRAME, LIST, FUNC, NATIVE_CLASS, EXIT_SUCCESS, EXIT_FAIL

# import pdb
# pdb.set_trace()

# -----------------------------------
#  Обьекты
#  Objects
# -----------------------------------

# ---------------------------------------------
#  Обьекты для компилятора и виртуальной машины.
#  Это бьекты типов.
#  Objects for compillet and virtual machine.
#  This is objects of data types.
# ---------------------------------------------


class ObjectInt(Object):
    def __init__(self, v, type_):  # Initialize object by int value
        super().__init__(type_, 0)
        self.v = v
        self.methods = {'_str_': self._str_}

    def _str_(self):
        return ObjectStr(self.v, STR)


class ObjectFloat(Object):
    def __init__(self, v, type_):  # Initialize object by float value
        super().__init__(type_, 0)
        self.v = v
        self.methods = {'_str_': self._str_}
    # //// stack deals with Object base class

    def _str_(self):
        return ObjectStr(str(self.v), STR)
    # //// /stack deals with Object base class


class ObjectStr(Object):
    def __init__(self, v, type_):  # Initialize object by string value
        super().__init__(type_, 0)
        self.v = v
        self.methods = {'_str_': self._str_}

    def _str_(self):
        return self


class ObjectNone(Object):
    def __init__(self, v, type_):  # Initialize object by none value
        super().__init__(type_, 0)
        self.v = self
        self.methods = {'_str_': self._str_}

    def _str_(self):
        return ObjectStr('None', STR)


class ObjectBoolean(Object):
    def __init__(self, v, type_):  # Initialize object by int value 1 or 0(True or False)
        super().__init__(type_, 0)
        self.v = v
        self.methods = {'_str_': self._str_}

    def _str_(self):
        str_v = ''
        if self.v == 0:
            str_v = 'False'
        elif self.v == 1:
            str_v = 'True'
        return ObjectStr(str_v, STR)


# ------------------------------------------------------------------------------------------------------
#  Кодовый обьект содержит дата-кодовые-обьекты(для згрузки байткодом и например количество аргументов)
#  и другие такие же кодовые обьекты, обязательно содержит байт-код.Должен составлятся компилятором и
#  использован виртуальной машиной.
#  Code object have data-code-objects(for loading by byte-code and for example number of arguments)
#  and other same code objects, and also have byte-code.It must be made by compiller and unboxed by
#  Virtual machine.
# ------------------------------------------------------------------------------------------------------


class CodeObject(Object):
    """
      Minimum code object
    """

    def __init__(self, type_):
        super().__init__(type_, 0)

        self.co_name = ""  # name of function, for module it will be "<module>"
        self.co_arcount = 0  # number of func parameters
        self.co_consts = []  # diffrent types of consts to load on self.stack
        self.co_names = []  # gloabal string names
        self.co_varnames = []  # local string names
        self.co_code = []  # byte-code
        self.v = self

    def __str__(self):
        co_const_vals = ''
        len_co_consts_vals = len(self.co_consts)
        len_co_names_vals = len(self.co_names)
        co_const_vals=''
        co_names_vals=''
        
        for i in range(len_co_consts_vals):
            co_const_vals += str(self.co_consts[i].v) + ' '

        for i in range(len_co_names_vals):
            co_names_vals+=str(self.co_names[i].v) + ' '    
        s = "\n<code_obj>\nco_name: {}\nco_arcount: {}\nco_consts: {}\nco_names: {}\nco_varnames: {}\nco_code: {}</code_obj>\n".format(
            self.co_name, self.co_arcount, co_const_vals, co_names_vals, self.co_varnames, self.co_code)
        return s


# --------------------------
# Compiller
# --------------------------


def op_prior(str_char_op):
    """
        Приоритет арифметической операции
    """

    if str_char_op == "^":

        return 6
    elif str_char_op == "*":

        return 5
    elif str_char_op == "/":

        return 5
    elif str_char_op == "%":

        return 3
    elif str_char_op == "+":

        return 2
    elif str_char_op == "-":

        return 2


def isOp(c):
    """
        Это арифметическая операция?
    """

    if c == "-" or c == "+" or c == "*" or c == "/" or c == "%" or c == "^":
        return True
    return False


def opn(code_arif):
    """
        Перевод в обратную польскую запись
        @param code_arif список инфиксного выражения
        @return список  постфиксного выражения
    """
    """
       В списке должны быть числа типа float для работы с ними, вообще на этом построен компилятор
    """

    item_i = 0
    # Операндовый стек
    operat_stack = []
    # Выходной список
    resOpn = []

    len_code_arif = len(code_arif)
    while (item_i < len_code_arif):

        # получить следующий член выражения
        v = code_arif[item_i]
        item_i += 1
        # определить тип члена
        if isa(v, float):
            resOpn.append(v)
        elif re.match("[A-Za-z]+", v):
            resOpn.append(v)
        elif isa(v, str) and v[0] == '|':
            resOpn.append(v)
        elif isOp(v):

            while(len(operat_stack) > 0 and
                  operat_stack[-1] != "[" and
                  op_prior(v) <= op_prior(operat_stack[-1])):
                resOpn.append(operat_stack.pop())

            operat_stack.append(v)
        elif v == ']':

            while len(operat_stack) > 0:

                x = operat_stack.pop()
                if x == '[':

                    break
                resOpn.append(x)
        elif v == "[":
            operat_stack.append(v)
    while len(operat_stack) > 0:

        resOpn.append(operat_stack.pop())

    return resOpn


class Compiller:

    def __init__(self, trace=True):
        self.trace = trace

        self.byte_code = []
        self.startIp = 0
        self.object_co = None  # object for class Code for global scope
        self.co_consts_ind = 0  # pointer to co_consts for global scope
        self.co_names_ind = 0  # pointer to co_names
        self.co_consts_ind = 0  # pointer to co_consts for local scope
        self.co_names_ind = 0  # pointer to co_names for local scope
        self.args_count = 0  # args count(amount of args we pass)
        self.keywords = ("set!", "main", "loadfield", "print", "invokenative", "pass",
                         "args", "build_list", "getfield", "arif", "//", "say", "arifmetica",
                         "arr_take_index", "arr_assign_index", "defun", "params", "вызови_встроенный", "загрузи", "как")  # constructions of language, we need it
        # to interpret var id properly
        self.func_co = None
        self.we_in_function = False  # determes if we in global scope or in local function

    def generate(self, int_command):
        """"
          генерация байткода
          @param int_command добавляем число в список
        """

        self.byte_code.append(int_command)

    def compille(self, SExp, object_co):
        """
           Parse nested and sequensed(maybe nested) lists by first word for generating
           byte-code
        """
        self.object_co = object_co

        if self.trace:
            print('SExp', SExp)
        # ----------------------------
        # This are atoms of compiller
        # ----------------------------
        if isa(SExp, float):  # We got a float value
            self.object_co.co_code.append(Iload_const)
            self.object_co.co_code.append(self.co_consts_ind)
            self.object_co.co_consts.append(
                ObjectFloat(SExp, FLOAT))
            self.co_consts_ind += 1

        elif SExp == 'True':  # We got a True value
            self.object_co.co_code.append(Iload_const)
            self.object_co.co_code.append(self.co_consts_ind)
            self.object_co.co_consts.append(
                ObjectBoolean(1, BOOLEAN))
            self.co_consts_ind += 1

        elif SExp == 'False':  # We got a True value
            self.object_co.co_code.append(Iload_const)
            self.object_co.co_code.append(self.co_consts_ind)
            self.object_co.co_consts.append(
                ObjectBoolean(0, BOOLEAN))
            self.co_consts_ind += 1

        elif SExp == 'None':  # We got a None value
            self.object_co.co_code.append(Iload_const)
            self.object_co.co_code.append(self.co_consts_ind)
            self.object_co.co_consts.append(
                ObjectNone(None, NONE))
            self.co_consts_ind += 1

        elif isa(SExp, str) and SExp[0] != '|' and SExp not in self.keywords:# We got a string as var id
            # not string as var or language keyword
            self.object_co.co_code.append(Iload_name)
            self.object_co.co_code.append(self.co_names_ind)
            self.object_co.co_names.append(
                ObjectStr(SExp, STR))
            self.co_names_ind += 1

        elif isa(SExp, str) and SExp[0] == '|' and SExp not in self.keywords:# We got a string and not language keyword
            self.object_co.co_code.append(Iload_const)
            self.object_co.co_code.append(self.co_consts_ind)
            self.object_co.co_consts.append(
                ObjectStr(SExp, STR))
            self.co_consts_ind += 1

        elif SExp == 'как':
            pass

        # -----------------------------
        # /This are atoms of compiller
        # -----------------------------

        elif SExp[0] == 'args':

            for exp in SExp[1:]:
                self.compille(exp, object_co)
                self.args_count += 1

            self.object_co.co_code.append(Iload_const)
            self.object_co.co_code.append(self.co_consts_ind)
            self.object_co.co_consts.append(
                ObjectFloat(self.args_count, FLOAT))
            self.co_consts_ind += 1


            self.args_count = 0

        elif SExp[0] == 'params':
            for i in SExp[1:]:
                self.object_co.co_code.append(Iload_const)
                self.object_co.co_code.append(self.co_consts_ind)
                self.object_co.co_consts.append(ObjectStr(i, STR))
                self.co_consts_ind += 1


                self.args_count += 1

            self.object_co.co_code.append(Iload_const)
            self.object_co.co_code.append(self.co_consts_ind)
            self.object_co.co_consts.append(
                ObjectFloat(self.args_count, FLOAT))
            self.co_consts_ind += 1


            self.args_count = 0

        elif SExp[0] == '//':  # Это комментарии

            pass

        elif SExp[0] == 'set!':  # Create gloabal var name in module scope or local variable

            _, var_name, exp = SExp

            self.compille(exp, object_co)
            self.object_co.co_code.append(Istore_name)
            self.object_co.co_code.append(self.co_names_ind)
            self.object_co.co_names.append(ObjectStr(var_name, STR))
            self.co_names_ind += 1

        elif SExp[0] == 'import' or SExp[0] == 'загрузи':
            _, exp, _as, var_name = SExp

            self.compille(_as, object_co)

            self.object_co.co_code.append(Iload_const)
            self.object_co.co_code.append(self.co_consts_ind)
            self.object_co.co_consts.append(ObjectStr(var_name, STR))
            self.co_consts_ind += 1


            self.object_co.co_code.append(Iload_const)
            self.object_co.co_code.append(self.co_consts_ind)

            if exp == 'Система':
                exp = 'System'
            self.object_co.co_consts.append(ObjectStr(exp, STR))
            self.co_consts_ind += 1


            self.object_co.co_code.append(Iimport_module_bname)

        elif SExp[0] == '$':
            # Recursivly parse sequensed (maybe they contain nested lists) lists
            # In source text we always begin with this symbol and in the begining of
            # functions
            """
            ex($ (set! my_var 7) (print my_var) )
            """

            for exp in SExp[1:]:
                self.compille(exp, object_co)

        elif SExp[0] == 'defun':
            """
            (main (set! my_func(defun (params x) (<body>::=arif 1 + 3) ) ) (print my_func) )
            """
            """
            on self.stack it must be
            top(num params)->(param)(param)(param)(...)(code obj) --- Imake_function
            """

            _, params, body = SExp

            func_co = CodeObject(CODE)
            func_co.co_name = '<func>'

            save_main_co=self.object_co
            save_co_consts_ind=self.co_consts_ind
            save_co_names_ind=self.co_names_ind

            self.co_consts_ind=0
            self.co_names_ind=0

            for exp in body:  # parse body
                self.compille(exp, func_co)

            self.object_co=save_main_co

            self.co_consts_ind=save_co_consts_ind
            self.co_names_ind=save_co_names_ind

            self.object_co.co_code.append(Iload_const)
            self.object_co.co_code.append(self.co_consts_ind)
            self.object_co.co_consts.append(func_co)
            self.co_consts_ind += 1

            self.compille(params, self.object_co)  # parse params

            self.object_co.co_code.append(Imake_function)

        elif SExp[0] == 'arif' or SExp[0] == 'арифметика':  # It is arithmetic expression

            # convert from infix notation to back polish notation
            resOpn = opn(SExp[1:])
            """
              Заменяем в списке операции и индификаторы переменных(на индексы)
            """
            if self.trace:
                print('res opn', resOpn)
            for i in resOpn:

                if isOp(i):

                    if i == "+":

                        self.object_co.co_code.append(Iadd)
                    if i == "-":

                        self.object_co.co_code.append(Isub)
                    if i == "*":

                        self.object_co.co_code.append(Imult)
                    if i == "/":

                        self.object_co.co_code.append(Idiv)
                    """    
                    if i == "%":

                        self.object_co.co_code.append(Irem)
                    if i == "^":

                        self.object_co.co_code.append(Ipow)
                    """    

                elif isa(i, float):   # We got a float value
                    self.object_co.co_code.append(Iload_const)
                    self.object_co.co_code.append(self.co_consts_ind)
                    self.object_co.co_consts.append(
                        ObjectFloat(i, FLOAT))
                    self.co_consts_ind += 1

                elif isa(i, str) and i[0] == '|':  # We got a string
                    self.object_co.co_code.append(Iload_const)
                    self.object_co.co_code.append(self.co_consts_ind)
                    self.object_co.co_consts.append(
                        ObjectStr(i[1:], STR))
                    self.co_consts_ind += 1

                elif isa(i, str) and i[0] != '|':  # We got a string as var id
                    self.object_co.co_code.append(Iload_name)
                    self.object_co.co_code.append(self.co_names_ind)
                    self.object_co.co_names.append(
                        ObjectStr(i, STR))
                    self.co_names_ind += 1

        elif SExp[0] == 'getfield':
            _, obj_name, attr_name = SExp
            self.compille(obj_name, object_co)
            self.object_co.co_code.append(Iloadfield)
            self.object_co.co_code.append(self.co_names_ind)
            self.object_co.co_names.append(
                ObjectStr(attr_name, STR))
            self.co_names_ind += 1

        # on self.stack must be  top(obj_name)->(num_args)->(arg)(arg)(arg)(...)
        elif SExp[0] == 'invokenative' or SExp[0] == 'вызови_встроенный':
            if len(SExp) == 4:  # if we have arguments to the func
                _, obj_name, meth_name, args = SExp
                
                self.compille(args, object_co)
                self.compille(obj_name, object_co)

            elif len(SExp) == 3:  # if we have no arguments to the func
                _, obj_name, meth_name = SExp
                self.object_co.co_code.append(Iload_const)
                self.object_co.co_code.append(self.co_consts_ind)
                self.object_co.co_consts.append(ObjectFloat(0, FLOAT))
                self.compille(obj_name, object_co)

            self.object_co.co_code.append(Iinvokenative)
            self.object_co.co_code.append(self.co_names_ind)
            self.object_co.co_names.append(
                ObjectStr(meth_name, STR))
            self.co_names_ind += 1

        # on self.stack must be  top(num_args)->(arg)(arg)(arg)(...)
        elif SExp[0] == 'build_list':
            _, args = SExp
            self.compille(args, object_co)
            self.object_co.co_code.append(Ibuild_list)

        # on self.stack must be  top(arrayref)->(index)
        elif SExp[0] == 'arr_take_index':
            _, obj_array_name, index = SExp
            self.compille(index, object_co)
            self.compille(obj_array_name, object_co)
            self.object_co.co_code.append(Ioaload)
        
        # on self.stack must be  top(arrayref)->(index)->(val)
        elif SExp[0] == 'arr_assign_index':
            _, obj_array_name, index, val = SExp
            self.compille(val, object_co)
            self.compille(index, object_co)
            self.compille(obj_array_name, object_co)
            self.object_co.co_code.append(Ioastore)

        elif SExp[0] == 'return':
            _, val = SExp
            self.compille(val, object_co)
            self.object_co.co_code.append(Ireturn_value)

        elif SExp[0] == 'call':
            _, func_name, args = SExp

            self.compille(func_name, object_co)
            self.compille(args, object_co)
            self.object_co.co_code.append(Icall_function)

        elif SExp[0] == 'print' or SExp[0] == 'скажи':
            _, exp = SExp
            self.compille(exp, object_co)
            self.object_co.co_code.append(Iprint)

        elif SExp[0] == 'pass':  # ничего не делать

            self.generate(Inop)

        # //// Eq
        elif SExp[0] == '<':  # сравнить на меньше

            (_, list_arif1, list_arif2) = SExp

            self.compille(list_arif1, object_co)
            self.compille(list_arif2, object_co)
            """
            self.generate(Ilt)
            """

        elif SExp[0] == '=':  # сравнить на равенство

            (_, list_arif1, list_arif2) = SExp

            self.compille(list_arif1, object_co)
            self.compille(list_arif2, object_co)
            """
            self.generate(Ieq)
            """

        # //// /Eq

        # //// Control Flow
        elif SExp[0] == 'if':  # если

            (_, list_test, list_trueEpr, list_falseExpr) = SExp

            self.compille(list_test, object_co)
            self.generate(BRF)
            self.generate(0)
            self.generate(0)
            nAddr0_1 = len(self.byte_code)
            self.compille(list_trueEpr, object_co)
            self.generate(BR)
            self.generate(0)
            self.generate(0)
            nAddr1_2 = len(self.byte_code)
            delta1 = nAddr1_2-nAddr0_1
            self.byte_code[nAddr0_1-2] = self.short2bytes(delta1)[0]
            self.byte_code[nAddr0_1-1] = self.short2bytes(delta1)[1]
            self.compille(list_falseExpr, object_co)
            nAddr3_4 = len(self.byte_code)
            delta2 = (nAddr3_4-nAddr1_2)+2
            self.byte_code[nAddr1_2-2] = self.short2bytes(delta2)[0]
            self.byte_code[nAddr1_2-1] = self.short2bytes(delta2)[1]

        elif SExp[0] == 'while':  # пока

            (_, list_test, list_whileBody) = SExp

            nAddr1_2 = len(self.byte_code)
            self.compille(list_test, object_co)
            self.generate(BRF)
            self.generate(0)
            self.generate(0)
            nAddr0_1 = len(self.byte_code)
            self.compille(list_whileBody, object_co)
            self.generate(BR)
            self.generate(0)
            self.generate(0)
            nAddr2_3 = len(self.byte_code)
            delta1 = nAddr2_3-nAddr0_1
            delta2 = (nAddr2_3-nAddr1_2)-2
            self.byte_code[nAddr0_1-2] = self.short2bytes(delta1)[0]
            self.byte_code[nAddr0_1-1] = self.short2bytes(delta1)[1]
            self.byte_code[nAddr2_3-2] = self.short2bytes(-delta2)[0]
            self.byte_code[nAddr2_3-1] = self.short2bytes(-delta2)[1]

        # //// /Control Flow

        else:  # ошибка компиляции

            raise Exception("Unknown function name:%s" % SExp[0])

        return self.object_co

    def get_module_co_obj(self):
        """
             Возвращает результирующий байт код для ВМ
        """
        self.object_co.co_code.append(Istop)
        return self.object_co


# --------------------------
# /Compiller
# --------------------------

if __name__ == '__main__':
   c = None
   with open('src.lisp', 'r', encoding='utf8') as f:
      s = f.read()
      c = read(s)

   compiller = Compiller(
   # trace=False
   )
   object_co = CodeObject(CODE)
   object_co.co_name = '<module>'
   module_co_obj =compiller.compille(c, object_co)
   print('mod info', module_co_obj)

    
