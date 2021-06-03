from compil import Compiller, Object, read, ObjectInt, ObjectFloat, ObjectNone, ObjectBoolean, ObjectStr, CodeObject
from opcodes import WE_LOAD_CONSTS, WE_LOAD_NAME, WE_LOAD_NAME2, WE_LOAD_NAME3, WE_STORE_NAME
from enums import INT, FLOAT, STR, BOOLEAN, NONE, CODE, FRAME, LIST, FUNC, NATIVE_CLASS, EXIT_SUCCESS, EXIT_FAIL

import sys
import traceback


def convert_float2objfloat(v):  # boxing: float_val->obj
    return ObjectFloat(v, FLOAT)


def convert_str2objstr(v):  # boxing: float_val->obj
    return ObjectStr(v, STR)


def convert_objfloat2float(ob):  # unboxing
    return ob.v


def convert_objstr2str(ob):  # unboxing
    return ob.v


def incref(ob):  # увеличивает счетчик ссылок обьекта
    ob.ref_count += 1


def decref(ob):  # уменьшает счетчик ссылок обьекта
    ob.ref_count -= 1


def ukFloat_add(v, w):  # takes to references, works with them - unbox them, gives object
    v = convert_objfloat2float(v)
    w = convert_objfloat2float(w)
    v = v+w
    return convert_float2objfloat(v)


def ukStr_add(v, w):  # takes to references, works with them - unbox them, gives object
    v = convert_objstr2str(v)
    w = convert_objstr2str(w)
    v = v+w
    return convert_str2objstr(v)


def ukStr_mult(n, w):
    w = convert_objstr2str(w)
    v = w * n
    return convert_str2objstr(v)


def ukFloat_sub(v, w):  # takes to references, works with them - unbox them, gives object
    v = convert_objfloat2float(v)
    w = convert_objfloat2float(w)
    v = v-w
    return convert_float2objfloat(v)


def ukFloat_mult(v, w):  # takes to references, works with them - unbox them, gives object
    v = convert_objfloat2float(v)
    w = convert_objfloat2float(w)
    v = v*w
    return convert_float2objfloat(v)


def ukFloat_div(v, w):  # takes to references, works with them - unbox them, gives object
    v = convert_objfloat2float(v)
    w = convert_objfloat2float(w)
    v = v/w
    return convert_float2objfloat(v)


# -----------------------------
#  ВМ
#  Vm
# -----------------------------


# ----------------------------------
# Runtime objs
# ----------------------------------

DEFAULT_STACK_SIZE = 10
DEFAULT_FRAME_STACK_SIZE = 10


class ObjectList(Object):
    def __init__(self, size_, type_):  # Initialize object by size for list
        super().__init__(type_, 0)
        self.size = size_
        self.list_ = [None]*self.size
        self.methods = {'append': self._append_, '_str_': self._str_}
        self.v = self

    def _append_(self, list_):
        val = list_[0]
        self.list_.append(val)

    def _str_(self):
        res = ''
        for i in self.list_:
            res += str(i) + ' '
        return ObjectStr(res, STR)


class FrameObject(Object):
    def __init__(self, frame_code_object, frame_globals, frame_locals, type_):
        super().__init__(type_, 0)
        self.f_code = frame_code_object
        self.sp = -1  # pointer to frameS stack top
        self.stack = [None] * DEFAULT_STACK_SIZE
        self.f_globals = frame_globals
        self.f_locals = frame_locals
        self.pc = 0
        self.return_value = None
        self.v = self

    def __str__(self):
        s = 'Frame str sp: {0} f_globals: {1} f_locals: {2} pc: {3} ret val {4}'.format(
            self.sp, self.f_globals, self.f_locals, self.pc, self.return_value)

        return s


class FuncObject(Object):
    # globals inherit from main fraim(builtin functions)
    def __init__(self, func_code_object, globals_, default, vm, type_):
        super().__init__(type_, 0)
        self._vm = vm  # pointer to class Vm to deal wit eval_frame method
        self.func_globals = globals_
        self.func_locals = default
        self.func_code = func_code_object
        self.v = self

    def _call_(self, args):
        func_frame = FrameObject(
            self.func_code, self.func_globals, args, FRAME)  # NEW Frame object
        return self._vm.eval_frame(func_frame)


# --------------------------------
# Runtime Vm
# --------------------------------


# ///// bytecode realizations as funcs
def Iload_const(vm):
    vm.frame.pc += 1
    # we determe index for loading on self.frame.stack
    arg_ind = vm.b_c[vm.frame.pc]
    ob = vm.consts[arg_ind]
    vm.push_stack(ob)


def Istop(vm):
    vm.vm_is_running = False


def Iadd(vm):
    right = vm.pop_stack()
    left = vm.pop_stack()
    ob = None
    if right.type == FLOAT and left.type == FLOAT:
        ob = ukFloat_add(left, right)  # work with references
    elif right.type == STR and left.type == STR:
        ob = ukStr_add(left, right)  # work with references
    decref(right)  # work with references
    decref(left)   # work with references
    vm.push_stack(ob)


def Isub(vm):
    right = vm.pop_stack()
    left = vm.pop_stack()
    ob = ukFloat_sub(left, right)
    decref(right)  
    decref(left)   
    vm.push_stack(ob)


def Imult(vm):
    ob = None
    right = vm.pop_stack()
    left = vm.pop_stack()
    if (right.type == FLOAT and left.type == FLOAT) or (left.type == FLOAT and right.type == FLOAT)(vm):
        ob = ukFloat_mult(left, right)  
    elif (right.type == STR and left.type == FLOAT)(vm):
        n = convert_objfloat2float(left)
        n = int(n)
        ob = ukStr_mult(n, right)
    elif (right.type == FLOAT and left.type == STR)(vm):
        n = convert_objfloat2float(right)
        n = int(n)
        ob = ukStr_mult(n, left)
    decref(right) 
    decref(left)   
    vm.push_stack(ob)


def Idiv(vm):
    right = vm.pop_stack()
    left = vm.pop_stack()
    ob = ukFloat_div(left, right) 
    decref(right)  
    decref(left)   
    vm.push_stack(ob)


def Istore_name(vm):
    vm.frame.pc += 1
    arg_ind = vm.b_c[vm.frame.pc]
    # assign to var id (in locals) to object(from the top of vm.stack)
    vm.locals_[vm.names[arg_ind].v] = vm.pop_stack()


def Iload_name(vm):
    vm.frame.pc += 1
    arg_ind = vm.b_c[vm.frame.pc]
    var = vm.names[arg_ind]
    ob = None
    var_v = var.v
    if var_v not in vm.locals_:
        raise Exception("Var {0} referenced before assigment".format(var_v))
    else:
        ob = vm.locals_.get(var.v)
    vm.push_stack(ob)


def Iloadfield(vm):
    vm.frame.pc += 1
    arg_ind = vm.b_c[vm.frame.pc]
    var = vm.names[arg_ind]
    # obj on vm.stack
    ob = vm.pop_stack()

    ob_field = ob.fields[var.v]  # field (ukObject) from our obj by name
    if ob_field == None:
        raise Exception('field {0} did not faind of obj {1}'.format(var.v, ob))
    else:
        vm.push_stack(ob_field)


def Iinvokenative(vm):
    vm.frame.pc += 1
    arg_ind = vm.b_c[vm.frame.pc]
    var = vm.names[arg_ind]
    # obj on vm.stack
    ob = vm.pop_stack()

    # faind meth (pointers to func) from our obj by name
    ob_meth = ob.methods[var.v]
    if ob_meth == None:
        raise Exception(
            'method {0} did not faind of obj {1}'.format(var.v, ob))
    num_meth_args = vm.pop_stack().v  # here we got float val
    num_meth_args = int(num_meth_args)
    # print('num_meth_args', num_meth_args)
    if num_meth_args == 0:

        # call custom method
        result = ob_meth()

        if result == None:
            result = ObjectNone(None, NONE)

    else:
        # create args list with determed size
        arg_list = [0] * num_meth_args
        for i in range(num_meth_args):  # copy args from vm.stack to args tuple
            arg_list[num_meth_args-i-1] = vm.pop_stack()

        # call custom method
        result = ob_meth(arg_list)

        if result == None:
            result = ObjectNone(None, NONE)

    vm.push_stack(result)


def Iimport_module_bname(vm):
    var, mod_name = vm.popn_stack(2)

    mod = __import__(mod_name.v)
    cl = getattr(mod, mod_name.v)

    cl_obj = cl(NATIVE_CLASS)

    vm.frame.f_locals[var.v] = cl_obj


def Ibuild_list(vm):
    num_lists_args = vm.pop_stack().v  # here we got float val
    num_lists_args = int(num_lists_args)
    list_ = ObjectList(num_lists_args, LIST)
    for i in range(num_lists_args):
        list_.list_[num_lists_args-i-1] = vm.pop_stack()

    vm.push_stack(list_)


def Ioastore(vm):
    obj_array = vm.pop_stack().list_
    index = int(vm.pop_stack().v)
    val = vm.pop_stack()

    obj_array[index] = val


def Ioaload(vm):
    obj_array = vm.pop_stack().list_
    index = int(vm.pop_stack().v)

    vm.push_stack(ObjectFloat(obj_array[index], FLOAT))


def Iprint(vm):
    if vm.frame.stack:
        ob = vm.pop_stack()
        if ob.type != LIST:
            print('PRINT ob: {0}'.format(ob.v))
        else:
            for i in ob.list_(vm):
                print(i.v, end=' ')
            print()


def Imake_function(vm):
    num_func_pars = int(vm.pop_stack().v)
    func_default = {}
    globals_ = vm.globals_
    for i in range(num_func_pars):
        func_default[vm.pop_stack().v] = None

    code_object = vm.pop_stack()

    func_object = FuncObject(code_object, globals_, func_default, vm, FUNC)
    vm.push_stack(func_object)


def Icall_function(vm):
    num_func_args = vm.pop_stack().v  # get num of args - here we got float val
    num_func_args = int(num_func_args)
    result = ObjectNone(None, NONE)
    if num_func_args == 0:

        result = vm.push_stack(vm.pop_stack())._call_(None)  # call custom func
    else:
        arg_list = [0] * num_func_args  # create args list with determed size

        for i in range(num_func_args):  # copy args from vm.stack to args tuple
            arg_list[num_func_args-i-1] = vm.pop_stack()

        func_obj:FuncObject=None    

        func_obj = vm.pop_stack()

        func_objs_local_dict = func_obj.func_locals

        i = 0
        for key, _ in func_objs_local_dict.items():  # create args
            func_objs_local_dict[key] = arg_list[i]
            i += 1

        result = func_obj._call_(func_objs_local_dict)

        vm.push_stack(result)
        vm.vm_is_running = True


def Ireturn_value(vm):
    # transport value from current frame stack to vm return value
    vm.return_value = vm.pop_stack()
    vm.vm_is_running = False


def Inop(vm):
    pass

# ///// /bytecode realizations as funcs


class Vm:
    def __init__(self):
        # ///// pointers to function in order as bytecode goes - fast fetch

        self.func_bytecode_ptr = (Istore_name,
                                  Iload_const,
                                  Iadd,
                                  Imult,
                                  Idiv,
                                  Isub,
                                  Inop,
                                  Istop,
                                  Iload_name,
                                  Iloadfield,
                                  Iprint,
                                  Iinvokenative,
                                  Ibuild_list,
                                  Ioaload,
                                  Ioastore,
                                  Imake_function,
                                  Ireturn_value,
                                  Icall_function,
                                  Iimport_module_bname)

        # /////  /pointers to function in order as bytecode goes - fast fetch

        #  //// bytecode str to print

        self.vm_instructions = ("Istore_name",
                                "Iload_const",
                                "Iadd",
                                "Imult",
                                "Idiv",
                                "Isub",
                                "Inop",
                                "Istop",
                                "Iload_name",
                                "Iloadfield",
                                "Iprint",
                                "Iinvokenative",
                                "Ibuild_list",
                                "Ioaload",
                                "Ioastore",
                                "Imake_function",
                                "Ireturn_value",
                                "Icall_function",
                                "Iimport_module_bname")

        #  ////  /bytecode str to print

        self.fsp = -1  # pointer to frame stack
        self.frames = [None] * DEFAULT_FRAME_STACK_SIZE  # stack frame

        # current frame (to deal with it-the frame that is the first on stack frame)
        self.frame = None

    def push_frame(self, frame: FrameObject):
        self.fsp += 1
        self.frames[DEFAULT_FRAME_STACK_SIZE - 1 -
                    self.fsp] = frame  # realize frame stack
        # here we set current frame (to deal with it-the frame that is the first on stack frame)
        self.frame = frame

    def pop_frame(self):
        if self.fsp > 0:  # one or more
            self.fsp -= 1
            frame = self.frames[DEFAULT_FRAME_STACK_SIZE - 1 - self.fsp]
            return frame

    # ///// deals with current frame stack

    def pop_stack(self) -> Object:
        ret_st_val = self.stack[DEFAULT_STACK_SIZE - 1 - self.frame.sp]
        self.frame.sp -= 1
        return ret_st_val

    def push_stack(self, val: Object):
        self.frame.sp += 1
        self.stack[DEFAULT_STACK_SIZE - 1 - self.frame.sp] = val

    def popn_stack(self, n):
        ret_list = [0] * n

        for i in range(n):
            ret_list[n - i - 1] = self.pop_stack()

        return ret_list

    # ////// /deals with current frame stack

    def print_instruction(self):
        op = self.b_c[self.frame.pc]
        consts = self.frame.f_code.co_consts
        names = self.frame.f_code.co_names

        inst_name = self.vm_instructions[op]
        if op == WE_LOAD_CONSTS:
            print("{0} {1} {2}".format(
                self.frame.pc, inst_name, consts[self.b_c[self.frame.pc + 1]].v))
        elif op == WE_LOAD_NAME or op == WE_LOAD_NAME2 or op == WE_LOAD_NAME3 or op == WE_STORE_NAME:
            print("{0} {1} {2}".format(self.frame.pc, inst_name,
                                       names[self.b_c[self.frame.pc + 1]].v))
        else:
            print("{0} {1}".format(self.frame.pc, inst_name))

    # here we can print ex co_names or co_consts
    def print_objs_arrs(self, objs_arr, label):
        print(label, end=' ')
        for i in objs_arr:
            print(i.v, end=' ')
        print()

    def print_locals(self, locals_dict):
        print('locals->', end=' ')
        for pair in locals_dict.items():
            print(pair[0], ':', pair[1].v, end=', ')
        print('.')

    def print_stack(self, stack):
        if len(stack) != 0:
            print('stack->')
            for i in stack:
                if i != None:
                    print('[ %s ]' % i.v)
                    # print()

    def top(self):
        return self.frame.stack[-1]

    def peek(self, pos):
        return self.frame.stack[-pos]

    def eval_frame(self, frame,  trace=True):
        self.return_value = None

        self.push_frame(frame)

        if trace:
            if self.fsp == 0:
                print('<First frame executing>', self.frame)
            else:
                print('<New frame executing>', self.frame)

        self.pc = self.frame.pc
        self.b_c = self.frame.f_code.co_code
        self.stack = self.frame.stack

        self.locals_ = self.frame.f_locals
        self.globals_ = self.frame.f_globals

        self.consts = self.frame.f_code.co_consts
        self.names = self.frame.f_code.co_names
        self.vm_is_running = True
        try:
            while self.vm_is_running:

                op = self.b_c[self.frame.pc]

                if trace:
                    self.print_instruction()

                func_ptr = self.func_bytecode_ptr[op]
                func_ptr(self)  # pass vm object
                # self.pc += 1
                self.frame.pc += 1

                if trace:
                    self.print_stack(self.stack)
                    # print('pc', self.frame.pc)
                    # print('frame', self.frame)

            if trace:
                print('</frame executing>')

            self.frame = self.pop_frame()  # set previous frame as current current frame
            if self.frame != None:
                self.pc = self.frame.pc
                self.b_c = self.frame.f_code.co_code
                self.stack = self.frame.stack
                self.locals_ = self.frame.f_locals
                self.globals_ = self.frame.f_globals

                self.consts = self.frame.f_code.co_consts
                self.names = self.frame.f_code.co_names
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            traceback.print_exc()

        return self.return_value


# *******************************************************
# Program
# Программа
# *******************************************************
c = None
with open('src.lisp', 'r', encoding='utf8') as f:
    s = f.read()
    c = read(s)

compiller = Compiller(
    # trace=False
)
vm = Vm()
object_co = CodeObject(CODE)
object_co.co_name = '<module>'
compiller.compille(c, object_co)
module_co_obj = compiller.get_module_co_obj()

# First NEW Frame object
main_fraim = FrameObject(module_co_obj, {}, {}, FRAME)
print('mod info', module_co_obj)

vm.eval_frame(main_fraim
              # , trace=False
              )
