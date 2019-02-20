#include <stdlib.h>
#include <string.h>

#include "map.h"

#define MAP_BY_VAL 0 ///< мапировано значением
#define MAP_BY_REF 1 ///< мапировано ссылкой

/**
 * одна запись карты
 */
typedef struct mapitem
{
	char* key;  ///< строка,ключ
	void* val;  ///< значение
	int type;   ///< тип
} MI;
/**
 * Карта
 */
typedef struct map
{
	int size; ///< размер карты
	MI* items;///< блок записей карты
} M;

/*! Создать карту
 *\return Handle на карту
 */
M* mapNew()
{
	M* map;

	map = malloc(sizeof(M));
	map->size = 0;//< создается 0 ой длины
	map->items = NULL;

	return map;
}

/*!Добавление ключа и значения в карту
 *\param key строка-ключ
 *\param val значение, любой тип
 *\param map данная карта
 */
void mapAdd(char* key, void* val, M* map)
{
        // определение ключа
	char* newkey;

	newkey = malloc(strlen(key) + 1);
	strcpy(newkey, key);
        // выделение памяти для записей карты
	if (map->size == 0)
	{
		map->items = malloc(sizeof(MI));
	}
	else
	{
		map->items = realloc(map->items, sizeof(MI) * (map->size + 1));
	}

	(map->items + map->size)->key = newkey;
	(map->items + map->size)->val = val;
	(map->items + map->size++)->type = MAP_BY_VAL;
}



void mapDynAdd(char* key, void* val, M* map)
{
	mapAdd(key, val, map);
	(map->items + map->size - 1)->type = MAP_BY_REF;
}

/*!Получить значение по ключу из данной карты
 *\param  key ключ-строка
 *\param  map данная карты
 *\return значение
 */
void* mapGet(char* key, M* map)
{
	int i;

	for (i = 0; i < map->size; i++)
	{       // сравниваем ключи
		if (strcmp((map->items + i)->key, key) == 0)
		{
			return (map->items + i)->val;
		}
	}

	return NULL;
}

/*!Закрыть карту
 *\param map - Handle данной карты
 */
void mapClose(M* map)
{
	int i = 0;

	for(; i < map->size; i++)
	{
		free((map->items + i)->key);

		if ((map->items + i)->type == MAP_BY_REF)
		{
			free((map->items + i)->val);
		}
	}

	free(map->items);
	free(map);
}
