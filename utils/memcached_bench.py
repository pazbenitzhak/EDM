import time
import random
from pymemcache.client import base
import statistics
import argparse
import os
import sys

# Create the argument parser
parser = argparse.ArgumentParser(description='Simple benchmark for memcached')

# Add the arguments
parser.add_argument('--data_size', type=int, default=262144, help='Size of each value')
parser.add_argument('--num_of_requests', type=int, default=10000, help='Number of requests')
parser.add_argument('--get_ratio', type=float, default=0.45, help='Get requests ratio')
parser.add_argument('--delete_ratio', type=float, default=0.1, help='Delete requests ratio')
parser.add_argument('--max_total_data', type=int, default=1288490188, help='Total data that memcached stores')
parser.add_argument('--host', type=str, default='localhost', help='memcached host')
parser.add_argument('--port', type=int, default=11212, help='memcaced port')
parser.add_argument('--verbose_logging', type=bool, default=False, help='Is verbose logging')

# Parse the command-line arguments
args = parser.parse_args()

# Access the argument values
value_size = args.data_size
num_requests = args.num_of_requests
server_host = args.host
server_port = args.port
get_ratio = args.get_ratio
delete_ratio = args.delete_ratio
max_total_data = args.max_total_data
verbose = args.verbose_logging

if not verbose:
    sys.stdout = open(os.devnull, 'w')


# Connect to Memcached server
client = base.Client((server_host, server_port))

# Set to store the keys that have been set
set_keys = set()

# Lists to store latency values
latencies = []

# Function to generate a random key
def generate_key():
    return str(random.randint(0, num_requests - 1))

# Function to generate a random value of 0.5MB size
def generate_value():
    value = "X" * value_size  # 0.25MB value size
    return value

# Start benchmark
start_time = time.time()

for _ in range(num_requests):
    # Generate a random key
    key = generate_key()

    # Determine the operation type based on the ratio
    rand = random.random()
    if rand < get_ratio:
        # GET operation
        if key in set_keys:
            retrieved_value = client.get(key)
            if retrieved_value is None:
                print(f"Value not found for key: {key}")
            else:
                print(f"key {key} found!")
    elif rand < get_ratio + delete_ratio:
        # DELETE operation
        if key in set_keys:
            client.delete(key)
            set_keys.remove(key)
    else:
        # SET operation
        print(f"set key {key}")
        value = generate_value()
        client.set(key, value)
        set_keys.add(key)
    if len(set_keys) * value_size > max_total_data:
        num_to_delete = int(len(set_keys) / 2)
        for i in range(num_to_delete):
            k = set_keys.pop()
            print(f"delete {k}")
            client.delete(k)

    # Calculate and store latency for each request
    end_time = time.time()
    latency = (end_time - start_time) * 1000  # Convert to milliseconds
    latencies.append(latency)

# End benchmark
end_time = time.time()

# Calculate benchmark duration and throughput
duration = end_time - start_time
throughput = num_requests / duration

# Calculate latency statistics
latency_avg = statistics.mean(latencies)
latency_min = min(latencies)
latency_p50 = statistics.median(latencies)
latency_p95 = statistics.quantiles(latencies, n=20)[-1]
latency_p99 = statistics.quantiles(latencies, n=100)[-1]
latency_max = max(latencies)

if not verbose:
    sys.stdout = sys.__stdout__

print("Summary:")
print(f"Number of requests: {num_requests}")
print(f"Total time: {duration:.2f} seconds")
print(f"  throughput summary: {throughput:.2f} requests per second")
print("  latency summary (msec):")
print(f"        {'avg':<10} {'min':<10} {'p50':<10} {'p95':<10} {'p99':<10} {'max':<10}")
print(f"        {latency_avg:>10.3f} {latency_min:>10.3f} {latency_p50:>10.3f} {latency_p95:>10.3f} {latency_p99:>10.3f} {latency_max:>10.3f}")