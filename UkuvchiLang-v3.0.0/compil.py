# --------------------------------------------------
#   Компилятор
# --------------------------------------------------
"""
   Представлены больше байт-кодов, чем реализованы
"""
from object_ import Object, CodeObject, ObjectBoolean, ObjectFloat, ObjectNone, ObjectStr
import re
from parse_funcs import read, isa
from opcodes import *
from enums import INT, FLOAT, STR, BOOLEAN, NONE, CODE, FRAME, LIST, FUNC, NATIVE_CLASS, EXIT_SUCCESS, EXIT_FAIL

# --------------------------
# Compiller
# --------------------------

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
        self.keywords = ("set!", "loadfield", "print", "invokenative", "pass",
                         "args", "build_list", "getfield", "arif", "//", "say", "arifmetica",
                         "arr_take_index", "arr_assign_index", "defun", "params", "вызовивстроенный", "загрузи", "как", "определи",
                         "проценты")  # constructions of language, we need it
        # to interpret var id properly
        self.func_co = None
        self.we_in_function = False  # determes if we in global scope or in local function

    def op_prior(self, str_char_op):
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
        elif str_char_op == "проценты":
            return 2

    def isOp(self, c):
        """
          Это арифметическая операция?
        """
        if c == "-" or c == "+" or c == "*" or c == "/" or c == "%" or c == "^" or c == 'проценты':
            return True
        return False

    def opn(self, code_arif):
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
            if self.trace:
                print('v', v)
            item_i += 1
            # определить тип члена
            if isa(v, float):
                resOpn.append(v)
            elif re.match("[A-Za-z]+", v) or (re.match("[А-яа-я]+", v) and v not in self.keywords):
                resOpn.append(v)
            elif isa(v, str) and v[0] == '|' and v not in self.keywords:
                resOpn.append(v)
            elif self.isOp(v):
                while(len(operat_stack) > 0 and
                      operat_stack[-1] != "[" and
                      self.op_prior(v) <= self.op_prior(operat_stack[-1])):
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
            if self.trace:
                print('after proc')
                print('operat stack', operat_stack)
                print('res opn', resOpn)
        while len(operat_stack) > 0:
            resOpn.append(operat_stack.pop())
        return resOpn

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
        func_name = ''
        self.object_co = object_co
        if self.trace:
            print('SExp', SExp)
        if isinstance(SExp, list):
           func_name = SExp[0]
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
                ObjectNone(NONE))
            self.co_consts_ind += 1
        # We got a string as var id
        elif isa(SExp, str) and SExp[0] != '|' and SExp not in self.keywords:
            # not string as var or language keyword
            self.object_co.co_code.append(Iload_name)
            self.object_co.co_code.append(self.co_names_ind)
            self.object_co.co_names.append(
                ObjectStr(SExp, STR))
            self.co_names_ind += 1
        # We got a string and not language keyword
        elif isa(SExp, str) and SExp[0] == '|' and SExp not in self.keywords:
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
        elif func_name == 'args':
            for exp in SExp[1:]:
                self.compille(exp, object_co)
                self.args_count += 1
            self.object_co.co_code.append(Iload_const)
            self.object_co.co_code.append(self.co_consts_ind)
            self.object_co.co_consts.append(
                ObjectFloat(self.args_count, FLOAT))
            self.co_consts_ind += 1
            self.args_count = 0
        elif func_name == 'params':
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
        elif func_name == '//':  # Это комментарии
            pass
        # Create gloabal var name in module scope or local variable
        elif func_name == 'set!' or func_name == 'определи':
            _, var_name, exp = SExp
            self.compille(exp, object_co)
            self.object_co.co_code.append(Istore_name)
            self.object_co.co_code.append(self.co_names_ind)
            self.object_co.co_names.append(ObjectStr(var_name, STR))
            self.co_names_ind += 1
        elif func_name == 'eq':
            _, first, sec = SExp
            self.compille(first, object_co)
            self.compille(sec, object_co)
            self.object_co.co_code.append(Ieq)
        elif func_name == 'ne':
            _, first, sec = SExp
            self.compille(first, object_co)
            self.compille(sec, object_co)
            self.object_co.co_code.append(Ine)
        elif func_name == 'import' or func_name == 'загрузи':
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
        elif func_name == '$':
            # Recursivly parse sequensed (maybe they contain nested lists) lists
            # In source text we always begin with this symbol and in the begining of
            # functions
            """
            ex($ (set! my_var 7) (print my_var) )
            """
            for exp in SExp[1:]:
                self.compille(exp, object_co)
        elif func_name == 'defun':
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
            save_main_co = self.object_co
            save_co_consts_ind = self.co_consts_ind
            save_co_names_ind = self.co_names_ind
            self.co_consts_ind = 0
            self.co_names_ind = 0
            for exp in body:  # parse body
                self.compille(exp, func_co)
            func_co.co_code.append(Iload_const)
            func_co.co_code.append(self.co_consts_ind)
            self.co_consts_ind += 1
            func_co.co_consts.append(ObjectNone(NONE))
            func_co.co_code.append(Ireturn_value)
            self.object_co = save_main_co
            self.co_consts_ind = save_co_consts_ind
            self.co_names_ind = save_co_names_ind
            self.object_co.co_code.append(Iload_const)
            self.object_co.co_code.append(self.co_consts_ind)
            self.object_co.co_consts.append(func_co)
            self.co_consts_ind += 1
            self.compille(params, self.object_co)  # parse params
            self.object_co.co_code.append(Imake_function)
        elif func_name == 'arif' or func_name == 'арифметика':  # It is arithmetic expression
            # convert from infix notation to back polish notation
            resOpn = self.opn(SExp[1:])
            if self.trace:
                print('res opn', resOpn)
            for i in resOpn:
                if self.isOp(i):
                    if i == "+":
                        self.object_co.co_code.append(Iadd)
                    elif i == "-":
                        self.object_co.co_code.append(Isub)
                    elif i == "*":
                        self.object_co.co_code.append(Imult)
                    elif i == "/":
                        self.object_co.co_code.append(Idiv)
                    elif i == 'проценты':
                        self.object_co.co_code.append(Iprocent)
                    """    
                    elif i == "%":

                        self.object_co.co_code.append(Irem)
                    elif i == "^":

                        self.object_co.co_code.append(Ipow)
                    """
                elif isa(i, float):   # We got a float value
                    self.object_co.co_code.append(Iload_const)
                    self.object_co.co_code.append(self.co_consts_ind)
                    self.object_co.co_consts.append(
                        ObjectFloat(i, FLOAT))
                    self.co_consts_ind += 1
                # We got a string
                elif isa(i, str) and i[0] == '|' and i not in self.keywords:
                    self.object_co.co_code.append(Iload_const)
                    self.object_co.co_code.append(self.co_consts_ind)
                    self.object_co.co_consts.append(
                        ObjectStr(i[1:], STR))
                    self.co_consts_ind += 1
                # We got a string as var id
                elif isa(i, str) and i[0] != '|' and i not in self.keywords:
                    self.object_co.co_code.append(Iload_name)
                    self.object_co.co_code.append(self.co_names_ind)
                    self.object_co.co_names.append(
                        ObjectStr(i, STR))
                    self.co_names_ind += 1
        elif func_name == 'getfield':
            _, obj_name, attr_name = SExp
            self.compille(obj_name, object_co)
            self.object_co.co_code.append(Iloadfield)
            self.object_co.co_code.append(self.co_names_ind)
            self.object_co.co_names.append(
                ObjectStr(attr_name, STR))
            self.co_names_ind += 1
        # on self.stack must be  top(obj_name)->(num_args)->(arg)(arg)(arg)(...)
        elif func_name == 'invokenative' or func_name == 'вызовивстроенный':
            if len(SExp) == 4:  # if we have arguments to the func
                _, obj_name, meth_name, args = SExp
                self.compille(args, object_co)
                self.compille(obj_name, object_co)
            elif len(SExp) == 3:  # if we have no arguments to the func
                _, obj_name, meth_name = SExp
                self.object_co.co_code.append(Iload_const)  # 0 - num of args
                self.object_co.co_code.append(self.co_consts_ind)
                self.object_co.co_consts.append(ObjectFloat(0, FLOAT))
                self.co_consts_ind += 1
                self.compille(obj_name, object_co)
            self.object_co.co_code.append(Iinvokenative)
            self.object_co.co_code.append(self.co_names_ind)
            self.object_co.co_names.append(
                ObjectStr(meth_name, STR))
            self.co_names_ind += 1
        # on self.stack must be  top(num_args)->(arg)(arg)(arg)(...)
        elif func_name == 'build_list':
            _, args = SExp
            self.compille(args, object_co)
            self.object_co.co_code.append(Ibuild_list)
        # on self.stack must be  top(arrayref)->(index)
        elif func_name == 'arr_take_index':
            _, obj_array_name, index = SExp
            self.compille(index, object_co)
            self.compille(obj_array_name, object_co)
            self.object_co.co_code.append(Ioaload)
        # on self.stack must be  top(arrayref)->(index)->(val)
        elif func_name == 'arr_assign_index':
            _, obj_array_name, index, val = SExp
            self.compille(val, object_co)
            self.compille(index, object_co)
            self.compille(obj_array_name, object_co)
            self.object_co.co_code.append(Ioastore)
        elif func_name == 'return':
            _, val = SExp
            self.compille(val, object_co)
            self.object_co.co_code.append(Ireturn_value)
        elif func_name == 'call':
            _, func_name, args = SExp
            self.compille(func_name, object_co)
            self.compille(args, object_co)
            self.object_co.co_code.append(Icall_function)
        elif func_name == 'print' or func_name == 'скажи':
            _, exp = SExp
            self.compille(exp, object_co)
            self.object_co.co_code.append(Iprint)
        elif func_name == 'pass':  # ничего не делать
            self.object_co.co_code.append(Inop)
        # //// Eq
        elif func_name == '<':  # сравнить на меньше
            (_, list_arif1, list_arif2) = SExp
            self.compille(list_arif1, object_co)
            self.compille(list_arif2, object_co)
            """
            self.generate(Ilt)
            """
        elif func_name == '=':  # сравнить на равенство
            (_, list_arif1, list_arif2) = SExp
            self.compille(list_arif1, object_co)
            self.compille(list_arif2, object_co)
            """
            self.generate(Ieq)
            """
        # //// /Eq

        # //// Control Flow
        elif func_name == 'if':  # если
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
        elif func_name == 'while':  # пока
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
            raise Exception("Unknown function name:%s" % func_name)
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

def rus2uk(src_s: str) -> str:
    src = src_s.split()
    len_src = len(src)
    uk_lst = [None] * len_src
    for i in range(len_src):
        word = src[i]
        if word == 'ученик':
            uk_lst[i] = '$>'
        elif word == 'выполни':
            uk_lst[i] = '-!'
        elif word == 'сколько':
            uk_lst[i] = '('
        elif word == 'конецсколько':
            uk_lst[i] = ')'
        elif word == 'и':
            uk_lst[i] = '->'
        else:
            uk_lst[i] = word
    uk_s = ' '.join(uk_lst)
    return uk_s


if __name__ == '__main__':
    c = None
    with open('src.lisp', 'r', encoding='utf8') as f:
        s = f.read()
        t = rus2uk(s)
        c = read(t)

    compiller = Compiller(
        # trace=False
    )
    object_co = CodeObject(CODE)
    object_co.co_name = '<module>'
    module_co_obj = compiller.compille(c, object_co)
    print('mod info', module_co_obj)
