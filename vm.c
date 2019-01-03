#include "vm.h"
/**
Распаковать как C float
 */
#define unpack754_32(i) (unpack754((i),32,8))
/**
Распаковать как С double
 */
#define unpack754_64(i) (unpack754((i),64,11))

/**
Распаковать как вещественное число
\param[in] i float число как целое
\param[in] bits мантисса
\param[in] expbits експонента
\return распакованное вещественное число
 */

long double unpack754(uint64_t i, unsigned bits, unsigned expbits) {
    long double result;
    long long shift;
    unsigned bias;
    unsigned significandbits = bits - expbits - 1; // -1 для бита знака
    // вычисляем биты от мантиссы,значимые биты,для 32val M_biti=23,для
    //64val это M_biti=52

    if (i == 0) return 0.0;

    // устанавливаем "знаковость"
    result = (i & ((1LL << significandbits) - 1)); // маска

    result /= (1LL << significandbits); // Конвертируем обратно во float
    result += 1.0f; // прибавляем обратно
    // разбираемся с экспонентой
    bias = (1 << (expbits - 1)) - 1;
    shift = ((i >> significandbits)&((1LL << expbits) - 1)) - bias;
    while (shift > 0) {
        result *= 2.0;
        shift--;
    }
    while (shift < 0) {
        result /= 2.0;
        shift++;
    }
    // получаем результат
    result *= (i >> (bits - 1))&1 ? -1.0 : 1.0;

    return result;


}

/** вызвать пользовательскую функцию 
 \param [in] funcid индификатор функции
 \param [in] argc количество аргументов
 \param [in] массив целых аргументов
 \return значение
 */
float call_user(int funcid, int argc, float *argv) {
    float ret = 0;
    int i;

    if (funcid == 0) {
        printf("Called user function 0 => stop.\n");
        return ret;
    }
    if (funcid == 1) {
        ret = cos(argv[-1]);
    }
    if (funcid == 2) {
        ret = sin(argv[-1]);
    }
    printf("Called user function %d with %d args:", funcid, argc);
    for (i = 0; i < argc; i++) {
        printf(" %f", argv[i]);

    }
    printf("\n");
    return ret;

}

/**
Отпечатка инструкции
 */
typedef struct {
    /** имя инструкции*/
    char name[8];
    /** количество аргументов*/
    int nargs;
} VM_INSTRUCTION;

/**Массив данных о каждой инструкции */

static VM_INSTRUCTION vm_instructions[] = {
    { "noop", 0},
    { "iadd", 0},
    { "isub", 0},
    { "imul", 0},
    {"idiv", 0},
    {"irem", 0},
    {"ipow", 0},
    { "ilt", 0},
    { "ieq", 0},
    { "br", 1},
    { "brt", 1},
    { "brf", 1},
    { "iconst", 1},
    { "load", 1},
    { "gload", 1},
    { "store", 1},
    { "gstore", 1},
    { "print", 0},
    { "pop", 0},
    { "call", 2},
    { "ret", 0},
    {"store_result", 1},
    {"load_result", 0},
    { "halt", 0}
};
/**Инициализация контекста */
static void vm_context_init(Context *ctx, int ip, int nlocals);

void vm_init(VM *vm, unsigned char *code, int code_size, int nglobals) {
    vm->code = code;
    vm->code_size = code_size;
    vm->globals = (int*) calloc(nglobals, sizeof (int));
    vm->nglobals = nglobals;
}

void vm_free(VM *vm) {
    free(vm->globals);
    free(vm);
}

VM *vm_create(unsigned char *code, int code_size, int nglobals) {
    VM *vm = (VM*) calloc(1, sizeof (VM));
    vm_init(vm, code, code_size, nglobals);
    return vm;
}
typedef uint32_t u4;

/**
Выпоолняе байт-коды
\param[in] vm  экземпляр Vm
\param[in] startip с какого байта выполнять опкоды
\param[in] trace если трассировка?
\param[in] numberFromLocalsAsPar использовать ли число из локальных переменных
\return число из локальных переменных
 */
float vm_exec(VM *vm, int startip, bool trace, int returnPrintOpFromLocals_flag) {


    int ip;
    int sp;
    int callsp;

    float a = 0;
    float b = 0;
    int addr = 0;
    int offset = 0;

    ip = startip;
    sp = -1;
    callsp = -1;
    /**
    следующая операция
     */
#define NEXTOP() vm->code[ip] 
    /**
    следующий аргумент как 'собирание' 4х байтов
     */
#define NEXTARGASI4() (ip+=4 ,(u4) ( (u4) (vm-> code[ip-4]<<24 ) | (u4) ( vm->code[ip-3]<<16 ) | (u4) (vm-> code[ip-2]<<8 ) | (u4) (vm-> code[ip-1] ) ) )
    u4 opcode = vm->code[ip];
    while (opcode != HALT) {
        if (trace) {
            vm_print_instr(vm->code, ip);

        }
        ip++;
        switch (opcode) {
            case NOOP:
                break;
            case IADD:
                b = vm->stack[sp--]; 
                a = vm->stack[sp--]; 
                vm->stack[++sp] = a + b; 
                break;
            case ISUB:
                b = vm->stack[sp--];
                a = vm->stack[sp--];
                vm->stack[++sp] = a - b;
                break;
            case IMUL:
                b = vm->stack[sp--];
                a = vm->stack[sp--];
                vm->stack[++sp] = a * b;
                break;
            case IDIV:
                b = vm->stack[sp--];
                a = vm->stack[sp--];
                vm->stack[++sp] = a / b;
                break;

            case IREM:
                b =  vm->stack[sp--];
                a =  vm->stack[sp--];
                vm->stack[++sp] =(int) a % (int)b;
                break;

            case IPOW:
                b = vm->stack[sp--];
                a = vm->stack[sp--];
                vm->stack[++sp] = pow(a, b);
                break;
            case ILT:
                b = vm->stack[sp--];
                a = vm->stack[sp--];
                vm->stack[++sp] = (a < b) ? true : false;
                break;
            case IEQ:
                b = vm->stack[sp--];
                a = vm->stack[sp--];
                vm->stack[++sp] = (a == b) ? true : false;
                break;
            case BR:
                ip = vm->code[ip];
                break;
            case BRT:
                addr = vm->code[ip++];
                if (vm->stack[sp--] == true) ip = addr;
                break;
            case BRF:
                addr = vm->code[ip++];
                if (vm->stack[sp--] == false) ip = addr;
                break;
            case ICONST:
                vm->stack[++sp] = unpack754_32(NEXTARGASI4());
                break;
            case LOAD:
                offset = vm->code[ip++];
                vm->stack[++sp] = vm->call_stack[callsp].locals[offset];
                break;
            case GLOAD:
                addr = vm->code[ip++];
                vm->stack[++sp] = vm->globals[addr];
                break;
            case STORE:
                offset = vm->code[ip++];
                vm->call_stack[callsp].locals[offset] = vm->stack[sp--];
                break;
            case GSTORE:
                addr = vm->code[ip++];
                vm->globals[addr] = vm->stack[sp--];
                break;
            case PRINT:
            {
                int numberFromLocalsAsPar = vm->code[ip++];
                float numberFromLocals = vm->call_stack[callsp].locals[numberFromLocalsAsPar];
                printf("print: %f\n", numberFromLocals);
                if (returnPrintOpFromLocals_flag) {
                    return numberFromLocals;
                }

                break;
            }
            case POP:
                --sp;
                break;
            case 25 ... 25 + 15:
            {
                int argc = (int) vm->stack[sp--];
                float argv[argc];
                for (int i = 0; i < argc; i++) {
                    argv[i] = vm->stack[sp--];

                }
                a = call_user(opcode - 25, argc, argv);
                if (argc != 0) {
                    vm->float_registrThatRetFunc = a;

                }



                break;

            }
            case CALL:
            {

                addr = vm->code[ip++];
                int nargs = vm->code[ip++];
                int I_firstarg = sp - nargs + 1;
                ++callsp;

                vm_context_init(&vm->call_stack[callsp], ip, 26);

                for (int i = 0; i < nargs; i++) {
                    vm->call_stack[callsp].locals[i] = vm->stack[I_firstarg + i];
                }
                sp -= nargs;
                ip = addr;
                break;
            }
            case RET:
            {
                ip = vm->call_stack[callsp].returnip;
                callsp--;
                break;
            }
            case STORE_RESULT:
            {
                int int_locNum = vm->code[ip++];
                vm->float_registrThatRetFunc = vm->call_stack[callsp].locals[int_locNum];
                break;
            }
            case LOAD_RESULT:
            {
                vm->stack[++sp] = vm->float_registrThatRetFunc;
                break;
            }

            default:
            {
                printf("invalid opcode: %d at ip=%d\n", opcode, (ip - 1));
                exit(1);
            }

        }

        if (trace) vm_print_stack(vm->stack, sp);
        opcode = vm->code[ip];



    }
    if (trace) {
        vm_print_data(vm->globals, vm->nglobals);
    }
}

static void vm_context_init(Context *ctx, int ip, int nlocals) {
    if (nlocals > DEFAULT_NUM_LOCALS) {
        fprintf(stderr, "too many locals requested: %d\n", nlocals);
    }
    ctx->returnip = ip;
}

void vm_print_instr(unsigned char *code, int ip) {

    int opcode = code[ip];
    VM_INSTRUCTION *inst = &vm_instructions[opcode];
    switch (inst->nargs) {
        case 0:
            printf("%04d:  %-20s", ip, inst->name);
            break;
        case 1:
            if (opcode == ICONST) {

                printf("%04d: ICONST %f", ip, (float) unpack754_32((u4) (code[ip + 1 ] << 24) | (u4) (code[ip + 2] << 16) | (u4) (code[ip + 3] << 8) | (u4) (code[ip + 4])));
            } else {
                printf("%04d:  %-10s%-10d", ip, inst->name, code[ip + 1]);
            }


            break;
        case 2:
            printf("%04d:  %-10s%d,%10d", ip, inst->name, code[ip + 1], code[ip + 2]);
            break;
        case 3:
            printf("%04d:  %-10s%d,%d,%-6d", ip, inst->name, code[ip + 1], code[ip + 2], code[ip + 3]);

            break;
    }
}

void vm_print_stack(float *stack, int count) {
    printf("stack=[");
    for (int i = 0; i <= count; i++) {

        printf(" %f", stack[i]);
    }
    printf(" ]\n");
}

void vm_print_data(float *globals, int count) {
    printf("Data memory:\n");
    for (int i = 0; i < count; i++) {

        printf("%04d: %f\n", i, globals[i]);
    }
}

void vm_print_locals(float *locals, int count) {
    printf("Locals memory:\n");
    for (int i = 0; i < count; i++) {

        printf("%04d: %f\n", i, locals[i]);
    }
}

/** Выполнить Вм для Python расширения
 */
static PyObject* evalVm_poPoRpo(PyObject *self, PyObject * args) {
    PyObject * po_listObj;
    int int_startIp;
    int returnPrintOpFromLocals_flag = 0;

    if (!PyArg_ParseTuple(args, "Oii", &po_listObj, &int_startIp, &returnPrintOpFromLocals_flag)) {
        return NULL;
    }

    int int_length_PyList = (int) PyList_Size(po_listObj);
    unsigned char * ucharPtr_vectorKcharK_ProgramsOpcodes = (unsigned char*) calloc(int_length_PyList, sizeof (char));

    for (int i = 0; i < int_length_PyList; i++) {

        PyObject* po_ItemPyList = PyList_GetItem(po_listObj, i);


        long long_CElem = PyLong_AsLong(po_ItemPyList);
        ucharPtr_vectorKcharK_ProgramsOpcodes[i] = (unsigned char) long_CElem;
    }
    VM* vm = vm_create(ucharPtr_vectorKcharK_ProgramsOpcodes, int_length_PyList, 9);
    float float_returnedFromPrintOp = 0.0;
    float_returnedFromPrintOp = vm_exec(vm, int_startIp, true, returnPrintOpFromLocals_flag);
    vm_print_data(vm->globals, vm->nglobals);
    vm_free(vm);
    return Py_BuildValue("f", float_returnedFromPrintOp);


    free(ucharPtr_vectorKcharK_ProgramsOpcodes);

    return Py_None;


}
/**Какие функции задействуем для Python расширения */
static PyMethodDef funcs[] = {
    {"eval", (PyCFunction) evalVm_poPoRpo, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL}
};
/** Структура Python модуля */
static struct PyModuleDef cModPyDem = {
    PyModuleDef_HEAD_INIT,

    "VmTestPy",

    "",
    -1,

    funcs
};

/** Экспорт в python */
PyMODINIT_FUNC PyInit_libTestPydModuleFloat(void) {
    return PyModule_Create(&cModPyDem);


}