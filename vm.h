//vm.h
#include <stdint.h>
#include <stdio.h>
#include <inttypes.h>
#include <stdbool.h>
#include <math.h>
#include<stdlib.h>
#include <Python.h>
#ifndef VM_H_
#define VM_H_

#ifdef __cplusplus
extern "C" {
#endif

#define DEFAULT_STACK_SIZE      1000///<размер стека по умолчанию
#define DEFAULT_CALL_STACK_SIZE 100///<размер стека контекстов по умолчанию
#define DEFAULT_NUM_LOCALS      26 ///<количество локальных по умолчанию

typedef enum {
    NOOP   , ///<нет операций
    IADD    ,///<сложение   
    ISUB    ,///<вычитание
    IMUL    ,///<умножение
    IDIV    ,///<деление
    IREM    ,///<остаток от деления
    IPOW    ,///<возведение в степень        
    ILT     ,///<сравнить на менше   
    IEQ     ,///<сравнить на равенство   
    BR      ,///<прыжок   
    BRT     ,///<прыжок при правде   
    BRF     ,///<прыжок при неправде   
    ICONST  ,///<положить константу на стек  
    LOAD    ,///<загрузить из таблицы локальных переменных на стек  
    GLOAD   ,///<загрузить из таблицы глобальных переменнных на стек  
    STORE   ,///<сохранить со стека в лакальные переменные  
    GSTORE  ,///<сохранить со стека в глобальные переменные
    PRINT   ,///<печатает локальную переменную  
    POP     ,///<убирает вершину стека  
    CALL    ,///<вызывает функцию с nargs-количество аргументов:int и сколько переменных-фактических параметров ожидать на стеке:int  
    RET     ,///<завершает функцию  
    STORE_RESULT,///<сохранить результат функции специальный регистр
    LOAD_RESULT,///<загрузить результат прошлой функции из специального регистра на стек        
    HALT ///<остановит виртуальную машину   
} VM_CODE;
/**
опкоды операций
*/
/** 
Контекст для функции
*/

typedef struct {
    /** адрес возврата */
    int returnip;
    /** локальные переменные контекста функции */
    float locals[DEFAULT_NUM_LOCALS];
} Context;
/** Компонент виртуальной машины */
typedef struct {
    /**  байт код */
    unsigned char *code;
    /**  размер байт кода */
    int code_size;

    /**  глобалные переменные */
    float *globals;
    /**  количество глобальных переменных */
    int nglobals;

    /**  Операндовый стек */
    float stack[DEFAULT_STACK_SIZE];
    /**  регистр для значения от функции */
    float float_registrThatRetFunc;
    /**  стек контекстов */ 
    Context call_stack[DEFAULT_CALL_STACK_SIZE];
} VM;
 
/** создать виртуальную машину */
VM *vm_create(unsigned char *code, int code_size, int nglobals);
/** освободить память из под виртуальной машины */
void vm_free(VM *vm);
/** инициализируем виртуальную машину */
void vm_init(VM *vm, unsigned char *code, int code_size, int nglobals);
/** выполнение инструкций */
float vm_exec(VM *vm, int startip, bool trace,int returnPrintOp_flag);
/** печатаем инструкцию */
void vm_print_instr(unsigned char *code, int ip);
/** печатаем стек */
void vm_print_stack(float *stack, int count);
/** печатаем глобальные переменные*/
void vm_print_data(float *globals, int count);
/** вызвать пользовательскую функцию */
float call_user(int funcid, int argc, float *argv);

#ifdef __cplusplus
}
#endif

#endif
