/**
 * Место где я собираюсь хранить 'определение' класса (пока только функции т.е это vtable)
 */

#include "map.h"
#include "types.h"
#include "vm.h"
#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include "map.h"
#ifdef __cplusplus
extern "C"
{
#endif


  struct map * vTable; ///< карта
  static u2 method_count; ///< количество методов
  static u1 * p; ///< указатель по байт-коду

  /**
   * Разобрать байт-код полученный из файла - подготовить для карты
   * \param bytecode данный байт-код
   * \return получилось ли?
   */
  bool
  parseByteCodeForMap (u1 * bytecode)
  {

    p = bytecode;
    method_count = getu2 (p);
    p += 2;
    printf ("method count:%d\n", method_count);
    if (method_count > 0)
      {
        parseMethods ();

      }


    return true;

  }

  /**
   * Парсит методы и ложит в карту ИМЯ_ФУНКЦИИ=>БАЙТ_КОД
   * \return получилось ли
   */
  bool
  parseMethods ()
  {
    vTable = mapNew (); // создаем карту
    int i;
    for (i = 0; i < method_count; i++)
      {
        // длина имени функции
        u1 strLen = *((u1*) p);
        p += 1;
        // определяем имя функции
        char* strFuncName = (char*) malloc (strLen);
        strcpy (strFuncName, p);
        p += strLen;
        // длина байт-кода
        u2 len = getu2 (p);
        p += 2;
        // выделение памяти под байт-код
        u1 * byteCodeForMap = (u1*) malloc (len);
        memcpy (byteCodeForMap, p, len);

        p += len;

        mapAdd (strFuncName, byteCodeForMap, vTable);



      }
    return true;
  }


#ifdef __cplusplus
}
#endif
