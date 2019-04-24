

#include "vm.h"

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
  { "iadd", 0},
  { "isub", 0},
  { "fmul", 0},
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
  {"invoke_in_vm", 0},
  {"createstring", 0},
  {"newarray", 0},
  {"iastore", 0},
  {"iaload", 0},
  {"dup", 0},
  {"astore", 0},
  {"aload", 0},
  {"invoke", 0},
  { "stop", 0},

  {"blink_red_led", 0}
};

typedef struct
{
  i2 ip, sp;

  i2 stack[50];
  i2 globals[26];

  i2 (*call_user) (u1 funcid, i2 argc, i2 *argv);

  i2 z;
} vm_s;

u1  program[50];


void
vm_print_instr (u1 *code, i2 ip)
{

  u1 opcode = code[ip];
  VM_INSTRUCTION *inst = &vm_instructions[opcode];
  switch (inst->nargs)
  {
    case 0:
      {
        SerialPrintf ("%04d:  %s ", ip, inst->name);
      }
      break;
    case 1:
      {
        if (opcode == ICONST | opcode == BR | opcode == BRF)
        {

          SerialPrintf ("%04d: %s %d ", ip, inst->name, geti2 (&(code[ip + 1])));
        }
        else
        {
          SerialPrintf ("%04d: %s %d ", ip, inst->name, code[ip + 1]);
        }
      }
      break;

  }

}

void
vm_print_stack (i2 *stack, i2 count)
{
  SerialPrintf ("stack=[");
  for (i2 i = 0; i <= count; i++)
  {

    SerialPrintf (" %d", stack[i]);
  }
  SerialPrintf (" ]\n");
}

/** вызвать пользовательскую функцию
  \param [in] funcid индификатор функции
  \param [in] argc количество аргументов
  \param [in] массив целых аргументов
  \return значение
*/
i2
call_user (u1 funcid, i2 argc, i2 *argv)
{
  #define ledVoltPlusPush 10
    pinMode (ledVoltPlusPush, OUTPUT);
  #define relayVoltPlusPush 2 
    pinMode(relayVoltPlusPush, OUTPUT); 
  i2 ret = 0;
  i2 i;

  if (funcid == 0)
  {
    SerialPrintf ("Called user function 0 => stop.\n");
    return ret;
  }
  if (funcid == 1)
  {
    SerialPrintf ("Led!\n");


    digitalWrite (ledVoltPlusPush, HIGH);
    delay (argv[0]);
    digitalWrite (ledVoltPlusPush, LOW);
    

  }
  if (funcid == 2)
  {
    SerialPrintf("Relay!\n");

    SerialPrintf("argv[0]: %d\n",argv[0]);
    
    digitalWrite(relayVoltPlusPush, LOW);
    delay(argv[0]);
    digitalWrite(relayVoltPlusPush, HIGH);
    
  }
  SerialPrintf ("Called user function %d with %d args:", funcid, argc);
  for (i = 0; i < argc; i++)
  {
    SerialPrintf (" %d", argv[i]);

  }
  SerialPrintf ("\n");
  return ret;

}

void
setup ()
{

  Serial.begin (9600);
  SerialPrintf("Begin\n");
  exec_my ();


}

void
vm_exec (vm_s *vm, bool trace)
{
  
  i2 a = 0, b = 0;
  u1 addr;
  u1 opcode = program[vm->ip];
  while (true)
  {

    if (trace)
    {
      vm_print_instr (program, vm->ip);

    }


    //SerialPrintf ("opcode: %d\n", opcode);
    SerialPrintf ("sp:%d \n", vm->sp);
    ++vm->ip;
    switch (opcode)
    {
      case STOP_VM:
        {
          SerialPrintf ("STOP VM\n");
          return;
        }
      case NOOP:
        {

        }
        break;
      case IADD:
        {
          b = vm->stack[vm->sp--];
          a = vm->stack[vm->sp--];
          vm->stack[++vm->sp] = a + b;
        }
        break;
      case ISUB:
        {
          b = vm->stack[vm->sp--];
          a = vm->stack[vm->sp--];
          vm->stack[++vm->sp] = a - b;
        }
        break;
      case IMUL:
        {
          b = vm->stack[vm->sp--];
          a = vm->stack[vm->sp--];
          vm->stack[++vm->sp] = a * b;
        }
        break;
      case IDIV:
        {
          b = vm->stack[vm->sp--];
          a = vm->stack[vm->sp--];
          vm->stack[++vm->sp] = a / b;
        }
        break;

      case IREM:
        {
          b = vm->stack[vm->sp--];
          a = vm->stack[vm->sp--];
          vm->stack[++vm->sp] = a % b;
        }
        break;

      case IPOW:
        {
          b = vm->stack[vm->sp--];
          a = vm->stack[vm->sp--];
          vm->stack[++vm->sp] = pow (a, b);
        }
        break;
      case ILT:
        {
          b = vm->stack[vm->sp--];
          a = vm->stack[vm->sp--];
          vm->stack[++vm->sp] = (a < b) ? true : false;

        }
        break;
      case IEQ:
        {
          b = vm->stack[vm->sp--];
          a = vm->stack[vm->sp--];
          vm->stack[++vm->sp] = (a == b) ? true : false;
        }
        break;
      case BR:
        {
          vm->ip += geti2 (&program[vm->ip]);

        }
        break;
      case BRT:
        {
          addr = geti2 (&program[vm->ip]);
          if (vm->stack[vm->sp--] == true) vm->ip = addr;

        }
        break;
      case BRF:
        {
          addr = geti2 (&program[vm->ip]);
          if (vm->stack[vm->sp--] == false)
            vm->ip += addr;
          vm->ip += 2;
        }
        break;
      case ICONST:
        {
          vm->stack[++vm->sp] = geti2 (&program[vm->ip]) ;

          vm->ip += 2;

        }
        break;
      case GSTORE:
        {
          addr = program[vm->ip++];
          vm->globals[addr] = vm->stack[vm->sp--];
        }
        break;
      case GLOAD:
        {
          addr = program[vm->ip++];
          vm->stack[++vm->sp] = vm->globals[addr];
        }
        break;


      case POP:
        {
          --vm->sp;
          SerialPrintf ("Pop!\n");

        }
        break;
      case blink_red_led:
      case turn_on_relay:
        {

          u1 argc = vm->stack[vm->sp--];
          i2* argv = (i2 *)malloc( argc * sizeof(i2));
          for (i2 i = 0; i < argc; i++)
          {
            argv[i] = vm->stack[vm->sp--];

          }
          vm->call_user (opcode - 32, argc, argv);

        }
        break;

      default:
        {
          SerialPrintf ("invalid opcode: %d at vm->ip=%d\n", opcode, (vm->ip - 1));
          exit (1);


        }

    }

    if (trace) vm_print_stack (vm->stack, vm->sp);
    opcode = program[vm->ip];

  }

}

void
exec_my ()
{
  /*u1 ser_arr[] = {12, 40, 35, 16, 0, 12, 0, 0, 16, 1, 14, 1, 14, 0, 7,
    11, 17, 0, 14, 0, 12, 1, 0, 33, 14, 0, 12, 232, 3, 2, 16, 0, 9, 233, 255, 32};
    EmulSerial Serial (ser_arr, sizeof (ser_arr) / sizeof (ser_arr[0]));*/

  SerialPrintf("Entered exec_my\n");

  vm_s *vm = (vm_s*) malloc (sizeof (vm_s));
  vm->ip = 0;
  vm->sp = -1;
  vm->call_user = &call_user;

  u1 by;
  int i = 0;
  while (true)
  {
    if (Serial.available () > 0)
    {
      SerialPrintf("Entered ser loop\n");

      by = Serial.read ();
      SerialPrintf("byte: %d\n", by);

      program[i] = by;
      SerialPrintf("program [%d]:%d\n", i, program[i]);
      i++;
      if (by == STOP_VM) // got(catch) stop Bytecode
      {
        vm_exec (vm, true);



      }

    }

  }
}
void loop()
{}
/*int
  main ()
  {
  setup ();

  return 0;
  }
*/
