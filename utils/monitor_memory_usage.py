import matplotlib.pyplot as plt
from matplotlib import style
import time
import sys

# get the cgroup name from command line 
arguments = sys.argv

if len(arguments) > 1:
    cgroup_name = arguments[1]
else:
    print("No input value provided.")
    exit()

times = []
swap_mem_usage = []
ram_mem_usage = []
memory_high = []

ram_mem_file_path = f'/sys/fs/cgroup/{cgroup_name}/memory.current'
swap_mem_file_path = f'/sys/fs/cgroup/{cgroup_name}/memory.swap.current'
memory_high_file_path = f'/sys/fs/cgroup/{cgroup_name}/memory.high'


plt.style.use('bmh')
fig, ax1 = plt.subplots()
line1 , = ax1.plot(times,swap_mem_usage,color='green', label='Swap Usage Memory')
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Memory Usage (MB)')

line2 , = ax1.plot(times,ram_mem_usage,color='blue', label='RAM Usage Memory')

line3 , = ax1.plot(times, memory_high, color = 'tomato', label='Memory.high')
ax1.set_title('Memory usage within a cgroup')
lines = [line1, line2, line3]
#ax1.legend(times,[l.get_label() for l in lines])
labels = [line.get_label() for line in lines]
ax1.legend(lines,labels)
cur_time = 0
swap_active = False
start_time = time.time()

with open(memory_high_file_path,'r') as f:
    memory_high = int(f.read().strip()) / 1024 /1024


while True:
    with open(swap_mem_file_path,'r') as f:
        try:
            usage_raw = int(f.read().strip())            
            if not swap_active:
                if (usage_raw > 50000):
                    swap_active = True
                    print("swap active since" + str(cur_time))
            usage = usage_raw / 1024 /1024
            #print(usage)
            swap_mem_usage.append(usage)
        except ValueError:
            pass

    with open(ram_mem_file_path,'r') as f:
        try:
            usage = int(f.read().strip()) / 1024 /1024
            #print(usage)
            ram_mem_usage.append(usage)
        except ValueError:
            pass

    
    times.append(round((time.time() - start_time),1))


    line1.set_xdata(times)
    line1.set_ydata(swap_mem_usage)
    line2.set_xdata(times)
    line2.set_ydata(ram_mem_usage)
    line3.set_xdata(times)
    line3.set_ydata(memory_high)

    ax1.relim()
    ax1.autoscale_view()
    
    plt.pause(0.05)
    fig.canvas.draw()
    fig.canvas.flush_events()    
    time.sleep(0.5)
    cur_time = cur_time + 0.5

