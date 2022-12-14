/* init function - for setting up a server */
/* need to set up a server at initialization 
define the server's size, if we want replicas etc
need to choose port and use localhost address 127.0.0.1*/
void init() { /* for now it's without args and a void return value */
    FILE* configFile;
    char* filepath;
    int isExecErr;
    /* open a config file, inside it write all wanted lines. file needs to end with .conf */
    configFile = fopen("serverCon.config","w"); /* open file to write all configurations */
    /* TODO: is opening a file like this OK? YES! I've checked */
    if (configFile==NULL) { /* that's how I chose to handle errors in fopen */
        printf("Error in opening new file\n");
        exit(1);
    }
    /* TODO; decide what the right filepath for the config file is */
    /*#from config file: Note that in order to read the configuration file, Redis must be
# started with the file path as first argument:
#
# ./redis-server /path/to/redis.conf*/
    if ((isExecErr=execvp("redis-server",))==-1) {/* an error has occured with execvp */
        printf("Error in initiating Redis server\n");
        exit(1);
    }
    /* TODO: handle execvp errors */
}

    /* initiate server  - if needed. maybe distinguish if needed from user's input?*/
    if (!isInitialized) { /* need to initialize a new server */
        init();
        isInitialized = 1; /* as we've just initialized the new server */    
    }
    /* TODO: from what I understand, once initialized it might still need to be called again
    thus we should execute the command again here without config and with port number only */
    /* end of initiating server */
    /* anyway, now we've got our server initialized and are ready to move forward */