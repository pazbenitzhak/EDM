#include <sw/redis++/redis++.h>
#include <stdio.h>


int main(int argc, char** argv) {
    printf("start run\n");
    /* create a connection to the Redis Cluster*/
    sw::redis::RedisCluster* redis = nullptr;
    const char* redis_addr = NULL;
    redis_addr = "tcp://10.201.133.29:4600";
	redis = new sw::redis::RedisCluster(redis_addr);
    printf("Connected to Redis Cluster \n");
    redis->set("First", "Call");
    {
    /* create the pipeline with a certain hash {1}*/
    auto pipe1 = redis->pipeline("1");
    printf("created pipeline {1}\n");
    /* make a few set commands and execute the pipeline*/
    pipe1.set("{1}:one", "there").set("{1}:whats", "up?").set("{1}:Okee","Dokee");
    printf("before pipe1 execution\n");
    pipe1.exec();
    }
    {
    /* create a new pipeline with a certain hash {2}*/
    auto pipe2 = redis->pipeline("{rqoufniueranfln}");
    printf("created pipeline {2}\n");
    /* make a few get commands to the key above*/
    pipe2.set("{rqoufniueranfln}:hey","you").set("{rqoufniueranfln}:oh","gee").set("{rqoufniueranfln}:good","bye");
    pipe2.exec();
    }
    printf("finished run\n");
}
