# how to use it: 
# run $ blktrace -d /dev/ublkb0 -o - | blkparse -i - > blk_trace_path.txt
# then run the python script and pass the blk_trace_path as argument

from tabulate import tabulate
import matplotlib.pyplot as plt
import sys
import signal
import os

arguments = sys.argv
output_filename = 'temp_txt'

if len(arguments) > 1:
    blk_trace_path = arguments[1]
else:
    print("No input value provided.")
    exit()

def handle_interrupt(signal, frame):
    print("Ctrl+C detected. Exiting...")
    if os.path.exists(output_filename):
        os.remove(output_filename)
        print(f"File '{output_filename}' deleted successfully.")
    else:
        print(f"File '{output_filename}' does not exist.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_interrupt)

with open(blk_trace_path, 'r') as file, open(output_filename, 'w') as output_file:
    for line in file:
        fields = line.split()
        if len(fields) == 11:
            if fields[5] in ['D']:
                output_file.write(f"{fields[3]} {fields[6]} {fields[9]}\n")

# Initialize empty lists to store the data
timestamps = []
actions = []
offsets = []

# Open the file and read each line
with open(output_filename, 'r') as file:
    for line in file:
        line = line.strip().split()
        action = line[1]
        if action == 'W' or action == 'R':
            # weird issue, prevent big gap in timestamps
            if (len(timestamps) > 100 and float(line[0]) > 100 * timestamps[-1]):
                break
            timestamp = float(line[0])
            offset = int(line[2])
            timestamps.append(timestamp)
            actions.append(action)
            offsets.append(offset)

# Create separate scatter plots for 'R' and 'W' actions
plt.scatter([timestamps[i] for i in range(len(actions)) if actions[i] == 'R'], 
            [offsets[i] for i in range(len(actions)) if actions[i] == 'R'], 
            color='red', label='Swap in (Read)', marker='o')

plt.scatter([timestamps[i] for i in range(len(actions)) if actions[i] == 'W'], 
            [offsets[i] for i in range(len(actions)) if actions[i] == 'W'], 
            color='green', label='Swap out (Write)', marker='o')

# Set x-axis label
plt.xlabel('Timestamp')

# Set y-axis label
plt.ylabel('Number of Blocks')

# Set title of the graph
plt.title('Block Trace - Ublk as Swap')

# Add a legend
plt.legend()

plt.show()

# Initialize dictionaries to store the count of read and write operations for each offset value
read_counts = {}
write_counts = {}

# Iterate over the offsets and actions lists simultaneously
for offset, action in zip(offsets, actions):
    if action == 'R':
        # Increment the count of read operations for the corresponding offset value
        read_counts[offset] = read_counts.get(offset, 0) + 1
    elif action == 'W':
        # Increment the count of write operations for the corresponding offset value
        write_counts[offset] = write_counts.get(offset, 0) + 1

# Print the results sorted by offset in increasing order
print('Total read operations:', sum(read_counts.values()))

# Create a list of lists to hold the data for the table
read_table_data = []
for offset in sorted(read_counts.keys()):
    count = read_counts[offset]
    read_table_data.append([offset, count])

print('Total write operations:', sum(write_counts.values()))

write_table_data = []
for offset in sorted(write_counts.keys()):
    count = write_counts[offset]
    write_table_data.append([offset, count])


# Print the results as tables
print('Read operations:')
print(tabulate(read_table_data, headers=['Offset', 'Count'], tablefmt='grid'))
print()

print('Write operations:')
print(tabulate(write_table_data, headers=['Offset', 'Count'], tablefmt='grid'))


# Create separate bar graphs for read and write operations
plt.subplot(2, 1, 1)
plt.bar(read_counts.keys(), read_counts.values(), color='red')
plt.xlabel('Offset')
plt.ylabel('Count')
plt.title('Read Operations')

plt.subplot(2, 1, 2)
plt.bar(write_counts.keys(), write_counts.values(), color='green', width=2.5)
plt.xlabel('Offset')
plt.ylabel('Count')
plt.title('Write Operations')

# Adjust the spacing between subplots
plt.tight_layout()

# Display the graphs
#plt.show()



# Display the graph
#plt.show()

