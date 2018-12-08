#ifndef VM_H_
#define VM_H_
#include <Python.h>
#ifdef __cplusplus
extern "C" {
#endif

#define DEFAULT_STACK_SIZE      1000
#define DEFAULT_CALL_STACK_SIZE 100
#define DEFAULT_NUM_LOCALS      26

typedef enum {
    NOOP   ,
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
} VM_CODE;

typedef struct {
    int returnip;
    float locals[DEFAULT_NUM_LOCALS];
} Context;

typedef struct {
    unsigned char *code;
    int code_size;

    // global variable space
    float *globals;
    int nglobals;

    // Operand stack, grows upwards
    float stack[DEFAULT_STACK_SIZE];
    float float_registrThatRetFunc;
    Context call_stack[DEFAULT_CALL_STACK_SIZE];
} VM;

VM *vm_create(unsigned char *code, int code_size, int nglobals);
void vm_free(VM *vm);
void vm_init(VM *vm, unsigned char *code, int code_size, int nglobals);
float vm_exec(VM *vm, int startip, bool trace,int returnPrintOp_flag);
void vm_print_instr(unsigned char *code, int ip);
void vm_print_stack(float *stack, int count);
void vm_print_data(float *globals, int count);
static PyObject* evalVm_poPoRpo(PyObject *self, PyObject * args);
PyMODINIT_FUNC PyInit_libTestPydModuleFloatRegister(void);

#ifdef __cplusplus
}
#endif

#endif

