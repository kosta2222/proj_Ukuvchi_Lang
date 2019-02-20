#ifndef VM_H_
#define VM_H_
#include <stdio.h>
#include <stdbool.h>
#include <malloc.h>
#include <math.h>
#include  <string.h>
#include "types.h"
#ifdef __cplusplus
extern "C" {
#endif



#define DEFAULT_STACK_SIZE      10///<размер стека по умолчанию
#define DEFAULT_CALL_STACK_SIZE 100///<размер стека контекстов по умолчанию
#define DEFAULT_NUM_LOCALS      26 ///<количество локальных переменных  по умолчанию

    /**
       опкоды операций
     */ // десятичное число
#define    NOOP 0 ///<нет операций                                   0
#define    FADD 1 ///<сложение                                      1
#define    FSUB 2 ///<вычитание                                     2
#define    FMUL 3///<умножение                                      3
#define    FDIV 4 ///<деление                                       4
#define    IREM 5 ///<остаток от деления                            5
#define    FPOW 6 ///<возведение в степень                          6
#define    IEQ 7 ///<сравнить на менше                              7
#define    IEQ  8 ///<сравнить на равенство                         8
#define    BR 9 ///<прыжок                                          9
#define    BRT 0x0a ///<прыжок при правде                           10
#define    BRF 0x0b ///<прыжок при неправде                         11
#define    FCONST 0x0c ///<положить константу на стек               12
#define    FLOAD 0x0d ///<загрузить из таблицы локальных переменных на стек    13
#define    FGLOAD 0x0e ///<загрузить из таблицы глобальных переменнных на стек 14
#define    FSTORE 0x0f ///<сохранить со стека в лакальные переменные           15
#define    FGSTORE 0x10 ///<сохранить со стека в глобальные переменные         16
#define    PRINT 0x11 ///<печатает локальную переменную                        17
#define    POP 0x12 ///<убирает вершину стека 18
#define    CALL 0x13 ///<вызывает функцию с nargs-количество аргументов:int и сколько переменных-фактических параметров ожидать на стеке:int 19
#define    RET 0x14 ///<завершает функцию 20
#define    STORE_RESULT 0x15 ///<сохранить результат функции специальный регистр                     21
#define    LOAD_RESULT 0x16 ///<загрузить результат прошлой функции из специального регистра на стек 22
#define    INVOKE_IN_VM 0x17 //< вызвать функцию по номеру в виртуальной машине                \todo 23
#define    CREATESTRING 0x18 //< создать строку в куче                                         \todo 24
#define    NEWARRAY 0x19 //< создать массив в куче,взяв длину со стека                               25
#define    FASTORE 0x1a //<сохранить значение в массиве                                              26
#define    FALOAD 0x1b //< загрузить значение из массива на стек                                     27
#define    DUP 0x1c // < дублировать вершину стека                                                   28
#define    ASTORE 0x1d //< сохранить ссылку на объект в массив переменных(переменные)          \todo 29
#define    ALOAD 0x1e //< загрузить ссылку на обьект на стек                                   \todo 30
#define    INVOKE 0x1f                                                                            // 31
#define    STOP 0x20 ///<остановит виртуальную машину                                                32

    /**
    Контекст для функции
     */
    typedef struct {
        /*байт-код контекста*/
        u1 * bytecode;
        /** локальные переменные контекста функции */
        Variable locals[DEFAULT_NUM_LOCALS];
    } Context;

    /** Компонент виртуальной машины */
    typedef struct {
        /**  глобалные переменные */
        Variable *globals;
        /**  количество глобальных переменных */
        u1 nglobals;
        /**  Операндовый стек */
        Variable stack[DEFAULT_STACK_SIZE];
        /**  регистр для значения от функции */
        Variable registrThatRetFunc;
        /**  стек контекстов */
        Context call_stack[DEFAULT_CALL_STACK_SIZE];
    } VM;

    /**
     * создать виртуальную машину
     * @param nglobals количество глобальных переменных
     * @return компонент ВМ
     */
    VM *vm_create(u1 nglobals);
    /**
     * освободить память из под виртуальной машины
     * @param vm компонент ВМ
     */
    void vm_free(VM *vm);
    /**
     * инициализируем виртуальную машину
     * @param vm компонент ВМ
     * @param nglobals количество глобальных переменных
     */
    void vm_init(VM *vm, u1 nglobals);

    /**
     *выполнение инструкций
     * @param vm компонент ВМ
     * @param funcName имя функции чтобы взять ее байт-код из карты
     * @param nargs количество аргументов которые принимает функция
     * @param trace печатать ли трассу?
     */
    void vm_exec(VM *vm, char *funcName, u1 nargs, bool trace);
    /**
     * печатаем инструкцию
     * @param code данный байт-код
     * @param ip указатель инструкции
     */
    void vm_print_instr(unsigned char *code, u4 ip);
    /**
     * печатаем стек
     * @param stack стек программы
     * @param count количество элементов для отпечатки
     */
    void vm_print_stack(Variable *stack, u1 count);
    /** печатаем глобальные переменные
@param globals массив глобальных переменных
@param count сколько печатать элементов
*/
    void vm_print_data(Variable *globals, u1 count);
    /**
     * вызвать пользовательскую функцию
     * @param funcid индификатор функции
     * @param argc количество аргуменов
     * @param argv массив аргументов
     * @return вычесленное значение
     */
    Variable call_user(int funcid, int argc, Variable *argv);
    /**
      Создание массива в куче
      \param type тип обьекта
      \param count количество элементов со стека
      \return Object для стека там содержится информация где содержится массив
     */
    Object createNewArray(u1 type, u4 count);
    /**
     * Разобрать байт-код полученный из файла - подготовить для карты
     * @param bytecode данный байт-код
     * @return получилось ли?
     */
    bool parseByteCodeForMap(u1* bytecode);

    /**
     * Парсит методы и ложит в карту ИМЯ_ФУНКЦИИ=>БАЙТ_КОД
     * @return получилось ли
     */
    bool parseMethods();


    /**
      Просто отпечатать кучу
     */
    void dumpHeap();


#ifdef __cplusplus
}
#endif
#endif
