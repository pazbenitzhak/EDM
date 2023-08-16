import sys
import os
import matplotlib.pyplot as plt

def extract_memory_sequences(blk_trace_file):
    sequences = []

    with open(blk_trace_file, 'r') as file:
        lines = file.readlines()

    start_offset = None
    end_offset = None
    operation_type = None
    last_interval = 0

    for line in lines:
        fields = line.split()
        if len(fields) == 11 and fields[6] in ['R', 'W'] and fields[5] in ['D']:
            offset = int(fields[7])
            if start_offset is None:
                start_offset = offset
                end_offset = offset
                operation_type = fields[6]
                last_interval = int(fields[9])
            elif offset == end_offset + last_interval:
                end_offset = offset
                last_interval = int(fields[9])
            else:
                sequences.append((start_offset, end_offset + last_interval, operation_type))
                start_offset = None
                end_offset = None
                operation_type = fields[6]

    if start_offset is not None:
        sequences.append((start_offset, end_offset, operation_type))

    return sequences


arguments = sys.argv
if len(arguments) > 1:
    blk_trace_path = arguments[1]
memory_sequences = extract_memory_sequences(blk_trace_path)

# Print the memory sequences
for sequence in memory_sequences:
    start_offset, end_offset, operation_type = sequence
    operation = 'Read' if operation_type == 'R' else 'Write'
    print(f"{operation} - {start_offset} to {end_offset}. total pages: {int((end_offset-start_offset)/8)}")

interval_sequences = []
for sequence in memory_sequences: 
    interval = int((sequence[1] - sequence[0]) / 8)
    operation_type = sequence[2]
    interval_sequences.append((interval, operation_type))

# Separate the sequences by operation type
read_sequences = [sequence for sequence in interval_sequences if sequence[1] == 'R']
write_sequences = [sequence for sequence in interval_sequences if sequence[1] == 'W']

# Extract the intervals for each operation type
read_intervals = [sequence[0] for sequence in read_sequences]
write_intervals = [sequence[0] for sequence in write_sequences]

# Group intervals into different page ranges
def group_page_ranges(intervals):
    ranges = {
        '0-16': 0,
        '16-128': 0,
        '128+': 0
    }

    for interval in intervals:
        if interval <= 26:
            ranges['0-16'] += 1
        elif interval <= 128:
            ranges['16-128'] += 1
        else:
            ranges['128+'] += 1

    return ranges

# Count the intervals in different page ranges for read and write operations
read_ranges = group_page_ranges(read_intervals)
write_ranges = group_page_ranges(write_intervals)

# Prepare data for the histogram
labels = list(read_ranges.keys())
read_counts = list(read_ranges.values())
write_counts = list(write_ranges.values())

# Plot the histogram
plt.subplot(2, 1, 1)
plt.bar(labels, read_counts, color='red', alpha=0.7)
plt.xlabel('Page Ranges')
plt.ylabel('Count')
plt.title('Read Operations')

plt.subplot(2, 1, 2)
plt.bar(labels, write_counts, color='green', alpha=0.7)
plt.xlabel('Page Ranges')
plt.ylabel('Count')
plt.title('Write Operations')

# Adjust the spacing between subplots
plt.tight_layout()

# Display the histograms
plt.show()
