#include "types.h"
#include <malloc.h>
#include <string.h>
#include <stdio.h>
#ifdef __cplusplus
extern "C"
{
#endif
  ///< карта как массив указателей
  Variable * m_objectMap[100];
  ///< при создании обьекта (массива) ID +=1
  u4 m_nNextObjectID = 0;

  /**
    Создание массива в куче
    \param type тип обьекта
    \param count количество элементов со стека
    \return Object для стека там содержится информация где содержится массив
   */
  Object
  createNewArray (u1 type, u4 count)
  {

    Object object;
    object.heapPtr = NULL;
    object.type = 0;

    // Создаем массив
    Variable *obj = (Variable*) malloc (sizeof (Variable)*(count));

    // Добавляем обьект в "карту"
    if (obj)
      {
        memset (obj, 0, sizeof (Variable) * (count));

        object.heapPtr = m_nNextObjectID++;
        //  obj[0].intValue = type;
        m_objectMap[object.heapPtr] = obj;
      }
    return object;
  }

  /**
    Просто отпечатать кучу

   */
  void
  dumpHeap ()
  {
    // обработать "карту"
    for (int i = 0; i < 10; i++) // возьмем 10 указателей
      {
        printf ("key %d=>\n", i);


        Variable* ptrElemPointsToWholeObject = m_objectMap[i]; // получаем указатель на массив из "карты"



        if (m_objectMap[i] != NULL)
          {


            for (int i = 0; i < 10; i++) // Надо отпечатать этот массив
              {
                if (ptrElemPointsToWholeObject[i].floatValue != NULL)
                  {
                    printf ("%f:", ptrElemPointsToWholeObject[i].floatValue);

                  }
              }



          }
      }

  }
#ifdef __cplusplus
}
#endif