#include "vm.h"
#include "map.h"
#ifdef __cplusplus
extern "C"
{
#endif

  /**
  Замечания. В тексте N целые числа, R - вещественные
   */
  /**
   * Работаем с данными элементами из ObjectHeap.cpp
   */
  extern Variable* m_objectMap[]; ///< куча
  extern struct map * vTable; ///< карта методов

  /** вызвать пользовательскую функцию
   \param [in] argc количество аргументов
   \param [in] массив целых аргументов
   \return значение
   */
  //Variable
  //call_user (int funcid, int argc, float *argv)
  //{
  //  Variable ret;
  //  int i;
  //
  //  if (funcid == 0)
  //    {
  //      printf ("Called user function 0 => stop.\n");
  //      return ret;
  //    }
  //  if (funcid == 1)
  //    {
  //      ret = cos (argv[-1]);
  //    }
  //  if (funcid == 2)
  //    {
  //      ret = sin (argv[-1]);
  //    }
  //  printf ("Called user function %d with %d args:", funcid, argc);
  //  for (i = 0; i < argc; i++)
  //    {
  //      printf (" %f", argv[i]);
  //
  //    }
  //  printf ("\n");
  //  return ret;
  //
  //}

  /**
  Отпечатка инструкции
   */
  typedef struct
  {
    /** имя инструкции*/
    char name[20];
    /** количество аргументов*/
    u1 nargs;
  } VM_INSTRUCTION;

  /**Массив данных о каждой инструкции */

  static VM_INSTRUCTION vm_instructions[] = {
    { "noop", 0},
    { "fadd", 0},
    { "fsub", 0},
    { "fmul", 0},
    {"fdiv", 0},
    {"irem", 0},
    {"fpow", 0},
    { "ilt", 0},
    { "ieq", 0},
    { "br", 1},
    { "brt", 1},
    { "brf", 1},
    { "fconst", 1},
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
    {"invoke_in_vm", 0},
    {"createstring", 0},
    {"newarray", 0},
    {"fastore", 0},
    {"faload", 0},
    {"dup", 0},
    {"astore", 0},
    {"aload", 0},
    {"invoke", 0},
    { "stop", 0}
  };

  /**
   * инициализируем виртуальную машину
   * \param vm компонент ВМ
   * \param nglobals количество глобальных переменных
   */
  void
  vm_init (VM *vm, u1 nglobals)
  {

    vm->globals = (Variable*) calloc (nglobals, sizeof (Variable));
    vm->nglobals = nglobals;
  }

  /** освободить память из под виртуальной машины */
  void
  vm_free (VM *vm)
  {
    free (vm->globals);
    free (vm);
  }

  /**
   * создать виртуальную машину
   * \param nglobals количество глобальных переменных
   * \return компонент ВМ
   */
  VM *
  vm_create (u1 nglobals)
  {
    VM *vm = (VM*) calloc (1, sizeof (VM));
    vm_init (vm, nglobals);
    return vm;
  }
  static u4 callsp = -1; ///< указатель контекста
  static u4 sp = -1; ///< указатель стека

  /**
   *выполнение инструкций
   * \param vm компонент ВМ
   * \param funcName имя функции чтобы взять ее байт-код из карты
   * \param nargs количество аргументов которые принимает функция
   * \param trace печатать ли трассу?
   */
  void
  vm_exec (VM *vm, char *funcName, u1 nargs, bool trace)
  {

    /*
    Принимает имя функции и количество аргументов для функции (основное)
, содает контекст и присваеивает ему байт-код который нашла в карте по имени
функции(метода), выявляет байты опкода по указателю ip считая с нулевого.Этой
функцией рекурсионно пользуется опкод INVOKE.
     */


    f4 a = 0;
    f4 b = 0;



    i2 addr;
    u1 n_locNum;
    u1 offset;



    u4 ip = 0;

    ++callsp; // создаем контекст

    vm->call_stack[callsp].bytecode = (u1*) mapGet (funcName, vTable); // присваиваем байт-код контексту

    u1* code = vm->call_stack[callsp].bytecode; // переопределим имя байт-кода
    u1 opcode = code[ip]; // сам опкод
    if (nargs > 0)// если имеем некоторое количество аргументов
      {
        u1 nFirstarg = sp - nargs + 1; // где первый аргумент в програмном стеке?

        for (int i = 0; i < nargs; i++)// создаем фактические аргументы в таблице локальных
          // переменных со стека, перемещая их из глубины стека
          {
            vm->call_stack[callsp].locals[i].floatValue = vm->stack[nFirstarg + i].floatValue;

          }
        sp -= nargs; // уравниваем стек, так как взяли фактические аргументы

      }


    while (opcode != STOP)// основная петля интерпритатора,работает пока не встретит опкод STOP
      {
        if (trace)
          {
            vm_print_instr (vm->call_stack[callsp].bytecode, ip); // печатаем инструкции - трассу

          }

        ip++; // переходим на следующую инструкцию(!) или аргумент(!)
        switch (opcode)// выборка
          {
          case NOOP: ///<нет операций
            break;
          case FADD:///<сложение
            b = vm->stack[sp--].floatValue;
            a = vm->stack[sp--].floatValue;
            vm->stack[++sp].floatValue = a + b;
            break;
          case FSUB: ///<вычитание
            b = vm->stack[sp--].floatValue;
            a = vm->stack[sp--].floatValue;
            vm->stack[++sp].floatValue = a - b;
            break;
          case FMUL:///<умножение
            b = vm->stack[sp--].floatValue;
            a = vm->stack[sp--].floatValue;
            vm->stack[++sp].floatValue = a * b;
            break;
          case FDIV: ///<деление
            b = vm->stack[sp--].floatValue;
            a = vm->stack[sp--].floatValue;
            vm->stack[++sp].floatValue = a / b;
            break;

          case IREM:// получить остаток от деления
            b = vm->stack[sp--].floatValue;
            a = vm->stack[sp--].floatValue;
            vm->stack[++sp].floatValue = (int) a % (int) b;
            break;

          case FPOW:// возведение в степень
            b = vm->stack[sp--].floatValue;
            a = vm->stack[sp--].floatValue;
            vm->stack[++sp].floatValue = pow (a, b);
            break;
          case DUP:// дублирование вершины стека
            vm->stack[sp + 1] = vm->stack[sp];
            sp += 1;
            break;
            // создать массив по длине
          case NEWARRAY:
            {
              vm->stack[sp + 1].object = createNewArray (1, (int) vm->stack[sp].floatValue);
              sp += 1;
              break;
            }
          case FALOAD: // загрузить значение с массива на стек
            {
              // arrayref в стеке - обеспечивается текстом программы getObject!
              Object heapKey = vm->stack[sp - 2].object;
              // берем нужный индекс со стека
              u4 index = (u4) (vm->stack[sp].floatValue);
              //  записываем элемент в стек - значение массива из кучи
              vm->stack[(u4) (sp - 1)] = m_objectMap[(u4) heapKey.heapPtr][index];
              sp -= 1;
              break;
            }
          case FASTORE: // загрузить значение со стека в массив
            {
              // arrayref в стеке - обеспечивается текстом программы getObject!
              Object heapKey = vm->stack[sp - 2].object;
              // берем нужный индекс со стека
              u4 index = (u4) (vm->stack[sp].floatValue);
              // работаем с кучей - записываем элемент из стека в массив
              m_objectMap[heapKey.heapPtr][(u4) index] = vm->stack[sp];
              sp -= 3;
              break;

            }
            // операции сравнения
          case IEQ:
            {
              b = vm->stack[sp--].intValue;
              a = vm->stack[sp--].intValue;
              vm->stack[++sp].intValue = (a < b) ? true : false;
              break;
            }
            // операции управления потоком
          case BR:
            {
              ip = geti2 (&code[ip++]);
              break;
            }
          case BRT:
            {
              addr = geti2 (&code[ip++]);
              if ((u1) vm->stack[sp--].intValue == true) ip = addr;
              break;
            }
          case BRF:
            {
              addr = geti2 (&code[ip++]);
              if ((u1) vm->stack[sp--].intValue == false) ip = addr;
              break;
            case FCONST:///<положить константу на стек

              vm->stack[++sp].floatValue = *((float*) &code[ip]);

              ip += 3;
              ip++;
              break;

            case FLOAD:///<загрузить из таблицы локальных переменных на стек
              offset = code[ip++];
              vm->stack[++sp].floatValue = vm->call_stack[callsp].locals[offset].floatValue;
              break;
            case FGLOAD:///<загрузить из таблицы глобальных переменнных на стек 14
              addr = code[ip++];
              vm->stack[++sp].floatValue = vm->globals[addr].floatValue;
              break;
            case FSTORE: ///<сохранить со стека в лакальные переменные
              offset = code[ip++];
              vm->call_stack[callsp].locals[offset].floatValue = vm->stack[sp--].floatValue;
              break;
            case FGSTORE: ///<сохранить со стека в глобальные переменные
              addr = code[ip++];
              vm->globals[addr].floatValue = vm->stack[sp--].floatValue;
              break;
              // Отпечать R из локальых переменных
            case PRINT:
              {
                int numberFromLocals = code[ip++];
                Variable value = vm->call_stack[callsp].locals[numberFromLocals];
                printf ("print float Value: %f\n", value.floatValue);


                break;
              }
            case POP:
              --sp;
              break;

            case INVOKE:// динамическое связываеие по имени функции
              {
                u1 funcArgLen = *((u1*) (&code[ip])); // длина имени функции
                char *funcName = (char*) malloc (funcArgLen); // определяем имя функции
                strcpy (funcName, (char*) &code[ip + 1]);

                u1 nargs = code[ip + funcArgLen + 1 ]; // количество аргументов - N

                vm_exec (vm, funcName, nargs, true); // рекурсивный вызов - связывание

                ip += (funcArgLen + 1); // функция отработала - продолжаем выполнение предыдущей функции
                printf ("in invoke ip : %d\n", ip);
                ip++;
                break;


              }

            case RET: ///<завершает функцию
              {
                callsp--; // уменьшаем указатель контекстов на прошлый контекст
                return; // устанавливаем рекурсию

              }
            case STORE_RESULT:///<сохранить результат функции специальный регистр
              {
                n_locNum = code[ip++];
                vm->registrThatRetFunc = vm->call_stack[callsp].locals[n_locNum];
                break;
              }
            case LOAD_RESULT:///<загрузить результат прошлой функции из специального регистра на стек
              {
                vm->stack[++sp] = vm->registrThatRetFunc;
                break;
              }

              // Ошибка разбора байт-кода
            default:
              {
                printf ("invalid opcode: %d at ip=%d\n", opcode, (ip - 1));
                exit (1);
              }

            }






          }

        if (trace) vm_print_stack (vm->stack, 3); // печатаем стек
        printf ("top of stack: %f\n", vm->stack[sp].floatValue); // печатаем вершину стека
        opcode = code[ip]; // следующий опкод


      }
    if (trace)
      {
        vm_print_data (vm->globals, vm->nglobals); // печаем глобалные переменные
      }
    printf ("Heap:\n");
    dumpHeap (); // печатаем кучу
  }

    /**
   * печатаем инструкцию
   * \param code данный байт-код
   * \param ip указатель инструкции
   */
  void
  vm_print_instr (u1 *code, u4 ip)
  {

    u4 opcode = code[ip];
    VM_INSTRUCTION *inst = &vm_instructions[opcode];
    switch (inst->nargs)
      {
      case 0:
        printf ("%04d:  %-20s", ip, inst->name);
        break;
      case 1:
        if (opcode == FCONST)
          {

            printf ("%04d: %-10s %f", ip, "fconst", *((float*) &(code[ip + 1])));
          }
        else
          {
            printf ("%04d:  %-10s%-10d", ip, inst->name, code[ip + 1]);
          }


        break;
      case 2:
        printf ("%04d:  %-10s%d,%10d", ip, inst->name, code[ip + 1], code[ip + 2]);
        break;
      case 3:
        printf ("%04d:  %-10s%d,%d,%-6d", ip, inst->name, code[ip + 1], code[ip + 2], code[ip + 3]);

        break;
      }
  }

  /**
   * печатаем стек
   * \param stack стек программы
   * \param count количество элементов для отпечатки
   */
  void
  vm_print_stack (Variable *stack, u1 count)
  {

    printf ("stack=[");
    for (int i = 0; i < count; i++)
      {

        printf (" %f", stack[i].floatValue);
      }
    printf (" ]\n");




  }

  /** печатаем глобальные переменные
\param globals массив глобальных переменных
\param count сколько печатать элементов
   */
  void
  vm_print_data (Variable *globals, u1 count)
  {
    printf ("Data memory:\n");
    for (int i = 0; i < count; i++)
      {

        printf ("%04d: %f\n", i, globals[i]);
      }
  }
  // ПРОГРАММА

  int
  main ()
  {
    FILE * ptrFile = fopen ("code.bin", "rb");

    if (ptrFile == NULL)
      {
        fputs ("Ошибка файла", stderr);
        exit (1);
      }

    // определяем размер файла
    fseek (ptrFile, 0, SEEK_END); // устанавливаем позицию в конец файла
    long lSize = ftell (ptrFile); // получаем размер в байтах
    rewind (ptrFile); // устанавливаем указатель в конец файла

    u1 * opcodeCharBuffer = (u1*) malloc (sizeof (u1) * lSize); // выделить память для хранения содержимого файла
    if (opcodeCharBuffer == NULL)
      {
        fputs ("Ошибка памяти", stderr);
        exit (2);
      }

    size_t result = fread (opcodeCharBuffer, 1, lSize, ptrFile); // считываем файл в буфер
    if (result != lSize)
      {
        fputs ("Ошибка чтения", stderr);
        exit (3);
      }
    // завершение работы
    fclose (ptrFile);

    // разобрать байт-код в карту
    if (!parseByteCodeForMap (opcodeCharBuffer))
      {
        fputs ("Не разобрал файл в виртуальную таблицу", stderr);
      }

    // создаем ВМ
    VM *vm = vm_create (0);
    vm_exec (vm, "main", 0, true); // выполняем с функции main
    // освобождаем память и буферы
    vm_free (vm);
    free (opcodeCharBuffer);
    mapClose (vTable);

    return 0;
  }
#ifdef __cplusplus
}
#endif
