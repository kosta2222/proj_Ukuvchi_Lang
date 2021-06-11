from enums import INT, FLOAT, STR, BOOLEAN, NONE, CODE, FRAME, LIST, FUNC, NATIVE_CLASS, EXIT_SUCCESS, EXIT_FAIL

class Object:
  def __init__(self, type_, ref_count_): 
    self.ref_count = ref_count_ 
    self.type = type_

# -----------------------------------
#  Objects
# -----------------------------------

# ---------------------------------------------
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
        self.methods = {'_str_': self._str_, '_add_': self._add_}

    def _add_(self, lst):
        w = lst[0]
        return ObjectFloat(self.v + w.v, FLOAT)
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
    def __init__(self, type_):  # Initialize object by none value
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
        co_const_vals = ''
        co_names_vals = ''

        for i in range(len_co_consts_vals):
            co_const_vals += str(self.co_consts[i].v) + ' '

        for i in range(len_co_names_vals):
            co_names_vals += str(self.co_names[i].v) + ' '
        s = "\n<code_obj>\nco_name: {}\nco_arcount: {}\nco_consts: {}\nco_names: {}\nco_varnames: {}\nco_code: {}</code_obj>\n".format(
            self.co_name, self.co_arcount, co_const_vals, co_names_vals, self.co_varnames, self.co_code)
        return s

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


  
