#include "header.h"

/* compilation command: need to compile all files at once:
gcc tests.c draft.c hiredis/hiredis.c hiredis/alloc.c hiredis/async.c hiredis/dict.c hiredis/net.c hiredis/read.c hiredis/sds.c hiredis/sockcompat.c hiredis/ssl.c -L/usr/local/ssl/lib -lssl -lcrypto -o tests
*/

int main(int argc, char** argv) {
    int port;
    redisContext* context;
    char* data;
    char* data2;
    char* data3;
    char* data4;
    port = 6400;
    context = connectToServer("127.0.0.1",port); /* connect to right port */
    if (context==NULL) { /* context = NULL: exit the program */
        exit(1); /* exit with error */
    }
    data = getValue("a",context);
    printf("data: %s\n",data);
    data2 = getValue("doremi",context);
    printf("data2: %s\n",data2);
    /* set new value */
    setValue("berlin","germany",context);
    data3 = getValue("berlin",context);
    printf("data3: %s\n",data3);
    /* change value */
    setValue("a","b",context);
    data4 = getValue("a",context);
    printf("data4: %s\n",data4);
}