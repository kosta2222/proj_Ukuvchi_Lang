#include <stdint.h>
#include <stdbool.h>

#include <math.h>
#include <stdlib.h>


//#include <stdio.h>
const size_t SerialPrintf (const char *szFormat, ...);
//#include <stdio.h>
//#define  SerialPrintf(...)  printf(__VA_ARGS__ )

typedef uint8_t u1;
typedef int16_t i2;
/**
  опкоды операций
 */

#define    NOOP     0
#define    IADD      1
#define    ISUB     2
#define    IMUL      3
#define    IDIV      4
#define    IREM     5
#define    IPOW      6
#define    ILT       7
#define    IEQ       8
#define    BR        9
#define    BRT       10
#define    BRF       11
#define    ICONST    12
#define    LOAD      13
#define    GLOAD     14
#define    STORE     15
#define    GSTORE    16
#define    PRINT     17
#define    POP       18
#define    CALL      19
#define    RET       20
#define    STORE_RESULT       21
#define    LOAD_RESULT         22
#define    INVOKE_BY_ORDINAL  23
#define    CREATE_STRING      24
#define    NEWARRAY  25
#define    IASTORE  26
#define    IALOAD   27
#define    DUP       28
#define    ASTORE    29
#define    ALOAD    30
#define    INVOKE    31
#define    STOP_VM   32

#define   blink_red_led 33
#define   turn_on_relay 34



void
exec_my ();
#define geti2(p) (i2)(((p)[1]<<8)|(p)[0])
/*class EmulSerial {
private:
    u1* ser_arr; // буфер
private:
    int by_ptr; // указатель байтов,при чтении(read)-инкремент
    int len; // длина буфера

public:
    EmulSerial(u1 * _ser_arr, int _len);
    u1
    peek();
    u1
    read();
    int
    available();
    void
    flush();

};
*/
