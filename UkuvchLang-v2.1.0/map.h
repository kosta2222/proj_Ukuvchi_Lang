#ifndef MAP_H
#define MAP_H
#ifdef __cplusplus
extern "C"{
#endif
struct map;

struct map* mapNew();
void mapAdd(char* key, void* val, struct map* map);
void mapDynAdd(char* key, void* val, struct map* map);
void* mapGet(char* key, struct map* map);
void mapClose(struct map* map);
#ifdef __cplusplus
}
#endif
#endif
