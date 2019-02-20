
/*
 * File:   types.h
 * Author: papa
 *
 * Created on 10 февраля 2019 г., 9:21
 */

#ifndef TYPES_H
#define TYPES_H
#ifdef __cplusplus
extern "C"{
#endif
/** Переопределение типов */
typedef unsigned int u4;
typedef unsigned short u2;
typedef unsigned char u1;



typedef int i4;
typedef short i2;

typedef float f4;
typedef double f8;

typedef long LONG_PTR;
/**
Кое что из исходников одной Jvm
Изначально порядок байт - Big-endian
 */
#define LOINT64(I8)(u4)(I8 &0xFFFFFFFF)///< выделение старших и младших u4 из I8 -  сужение до u4

#define HINT64(I8)(u4)(I8>> 32)        ///< выделение старших и младших u4 из I8
#define getu4(p) (u4)  ( (u4)( (p)[0] )<<24 & 0xFF00000|(u4) ((p)[1])<<16 & 0x00FF0000 |(u4) ((p)[2])<<8 & 0x0000FF00 ((p)[3]) & 0x000000FF)

#define getu2(p)(u2)((p)[0]<<8 & 0x0000FF00 | (p)[1])

#define MAKEI8 (i4high , i4low) ( ((i8)i4high) << 32 | (i8) i4low)

#define geti4(p) (u2) (i2)  ((u4) ((p)[0])<<24 | (u4) ((p)[2])<<8 | (u4)  ( (p)[3] ) )
#define geti2(p) (i2)(((p)[0]<<8)|(p)[1])

f4 getf4(char *p);

#define castu4(p) *((u4 *)p)
#define castu2(p) *((u2 *)p)

#define casti4(p) *((i4 *)p)
#define casti2(p) *((i2 *)p)





/** Основные структуры и структура для одного элемента стека */
typedef struct {
    LONG_PTR heapPtr;
    int type;
} Object;

/** Cтруктура для одного элемента стека
  элементы union разделяют один и тоже адрес ram */
typedef union {
    u1 charValue;
    u2 shortValue;
    f4 floatValue;
    u4 intValue;
    LONG_PTR ptrValue;
    Object object;
} Variable;
#ifdef __cplusplus
}
#endif

#endif /* TYPES_H */

