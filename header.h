#include "hiredis/hiredis.h"
#include <unistd.h>
#include <stdlib.h>

#define true 1

char* getValue(char* key, redisContext* redisContext);
redisContext* connectToServer(char* IP, int port);
void setValue(char* key, char* value, redisContext* redisContext);