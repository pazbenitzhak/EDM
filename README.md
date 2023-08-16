# Ublk-as-a-Swap

Ublk as a Swap is a PoC aimed at implementing userspace remote in-memory swap areas using ublk.
The main concept is to utilize ublk devices as high-speed swap areas, leveraging the scalability of the ublk framework to control swap-in and swap-out requests.

This project incorporates cgroup V2 to limit memory consumption and enforce processes within the cgroup to utilize the swap area. In the readme file, we explain step-by-step how to get this behavior, while we are providing utils programs for inspecting, debugging, and visualizing what happens behind the scenes. 

While diving into the project, it is advantageous for readers to familiarize themselves with ubdsrv and ublk-driver. Notably, our implementation builds upon ubdsrv, serving as an academic extension dedicated solely to demonstrating the proof of concept.

### High-Level Architecture
<img width="632" alt="image" src="https://github.com/EDM-Project/EDM-Ublk-as-a-Swap/assets/62066172/54248bb0-c772-44eb-a981-de771edb5f35">


Our solution adopts a straightforward architecture and leverages the theoretical understanding of kernel swapping mechanism and ublk usage.
To manage kernel requests efficiently, we divide them into individual pages (consisting of 8 sectors) and transfer them to Redis. This approach enables us to distribute application memory effectively within a cloud environment.

### Why is there no flush handler?

The absence of a flush handler in our solution might raise questions. The rationale behind this omission lies in the behavior of the Linux kernel when a block device is used as a swap file. In such cases, the kernel does not automatically flush the data from the block device when the associated pages are no longer in use. For instance, this occurs when a process terminates or when a memory area is unmapped. Instead, the kernel simply marks the page slot as available within its internal data structure.
The page slot that is marked as available within the kernel's internal data structure may potentially be reused to serve another page in the future.



## Prerequisites

- Linux kernel v6+ 
- ublk-drv module loaded
- Cgroup V2 
- Redis server&client configured
- ublk server prerequisites

## How To Use Ublk-as-a-Swap (UaaS)

1. Create a cgroup with the desired memory limits
    
        cgcreate -g memory:/<cgroup_name>
        cgset -r memory.high=<memory_limit> <cgroup_name>

2. Allocate the file with the swap size 
    
        fallocate -l <swap_size> <file_path>

3. load the ublk module 
    
        modprobe ublk-drv
4. Add ublk device 

        ./ublk add -t loop -d <queue_depth>-q <num_of_hardware_queues> -f <file_path> -r <redis_connection_address>

    for example 
    
        ./ublk add -t loop -d 2048 -q 2 -f /home/swap_file_1.img -r tcp://192.168.188.129:6385

In our implementation, the Redis connection address is a mandatory parameter.

5. Activate ublk swap 

        mkswap /dev/ublkbX
        swapon /dev/ublkbX -p <priority>
    where X is the ublk id. 
    Make sure the swap area was added, for example:
    
   
       [root@fedora ubdsrv]# swapon --show
     	NAME        TYPE       SIZE USED PRIO
     	/dev/zram0  partition  7.7G   0B  100
     	/dev/ublkb0 partition 1024M   0B  101
     	/dev/ublkb1 partition 1024M   0B  101


    In this example, the ublk swap areas have the highest priority. In this case, the kernel will round robin between the ublk devices, when they are filled, the kernel will use the first (zram0) area. 
 
    
6. Run the application in the cgroup

        cgexec -g "memory:/<cgroup_name>" <app> <arguments>
        
 7. To Remove the swap area and delete the ublk device
     
        swapoff /dev/ublkX
        ./ublk del -n X
where X is the device id.

## EDM Debugging & Visibility Tools

We provide some tools designed to facilitate the inspection of swap areas and monitor memory usage. By utilizing these tools, users gain insights into the implementation details and underlying processes, enabling them to enhance system performance.

### Monitor Memory Usage
A straightforward monitoring program to show real-time memory usage in RAM and swap areas within a cgroup.
usage 

    python monitor_memory_usage.py <cgroup_name>

example



<img width="400" alt="Screenshot 2023-07-01 123659" src="https://github.com/EDM-Project/EDM-Ublk-as-a-Swap/assets/62066172/fa47f061-42a5-451a-b8fb-20a207e8eb96">


### Swapped Page Table

We provide a parser for page table, where we can inspect the swapped pages. 

usage 
compile pagemap_swap_mappings.c with gcc.

  `./compiled_program <pid>`

     +------------------+------------------+------------------+------------------+
     |       vaddr      |      PTE-offset  |     PTE-type     |    Redis-key     |
     +------------------+------------------+------------------+------------------+
     | 0x55d8176f9000   | 16495            | 2                | 131960           |
     | 0x55d818917000   | 16431            | 2                | 131448           |
     | 0x55d818918000   | 16436            | 2                | 131488           |
     | 0x55d81891c000   | 32837            | 1                | 262696           |
     | 0x55d81891d000   | 32838            | 1                | 262704           |
     | 0x55d81891e000   | 32839            | 1                | 262712           |
     | 0x55d81891f000   | 32840            | 1                | 262720           |
     | 0x55d818920000   | 32827            | 1                | 262616           | 

Note that:
- PTE-offset and PTE-type are the raw data from the page table.
- PTE-type is the swap area number, in the example above there are 3 (starting with zero).
- Redis key calculated according to the way we store the pages in Redis:  $𝑜𝑓𝑓𝑠𝑒𝑡∗(𝑝𝑎𝑔𝑒 𝑠𝑖𝑧𝑒)/(𝑏𝑙𝑜𝑐𝑘 𝑠𝑖𝑧𝑒)$
- The bits are extracted according to https://docs.kernel.org/admin-guide/mm/pagemap.html


### Monitor blk Trace 

Python program that parses blktrace output, and provides insights about the IO operations in the block device.

usage: 

`blktrace -d /dev/ublkb0 -o - | blkparse -i - > blk_trace_path.txt`

`python monitor_blk_trace.py blk_trace_path.txt`

output example: 

<img width="593" alt="image" src="https://github.com/EDM-Project/EDM-Ublk-as-a-Swap/assets/62066172/46edc5ad-a095-4d10-8dbe-00efee0620e6">
