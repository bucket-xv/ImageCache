import subprocess
from docker_image_cache import DockerImageCache, EvictionPolicy
import threading
import time
import argparse
import os
import math
import pandas as pd

global_lock = threading.Lock()
total_cache_miss = 0
total_pulling_time = 0
pandas_table = pd.DataFrame()

project_dir = os.path.dirname(os.path.abspath(__file__))

def thread_func(cache, folder_to_zip, image_name, container_name, iterations, verbose=False):
    cache_miss = 0
    pulling_time = 0
    execution_time = 0
    for i in range(iterations):
        if verbose:
            print(f"Iteration {i+1} of {iterations} with image {image_name}")
        
        message = cache.put_image(image_name, container_name)
        # When the image is not in the cache, it will be pulled, and the cache will be updated
        start_time = time.time()
        while message is None:
            if verbose: 
                print("Cache is full, we have to wait")
            time.sleep(0.1)
            message = cache.put_image(image_name, container_name)

        if message == "Already in cache":
            if verbose:
                print(f"Image {image_name} cache hit")
        elif message == "Directly put in cache":
            cache_miss += 1
            subprocess.run(f"docker pull {image_name}", shell=True,capture_output=not verbose, text=True)
            end_time = time.time()
            pulling_time += end_time - start_time
            if verbose:
                print(f"Cold miss so Image {image_name} pulled")
        else:
            image_to_evict = message
            if verbose:
                print(f"Evicting image: {image_to_evict}")
            subprocess.run(f"docker rmi {image_to_evict}", shell=True, capture_output=not verbose, text=True)            
            cache_miss += 1
            subprocess.run(f"docker pull {image_name}", shell=True,capture_output=not verbose, text=True)
            end_time = time.time()
            pulling_time += end_time - start_time
            if verbose:
                print(f"Capcity miss so Image {image_name} pulled")
        
        # Run the container
        start_time = time.time()
        subprocess.run(f"docker run -v {folder_to_zip}:/files/zip --rm --name {container_name} {image_name}", shell=True, capture_output=not verbose, text=True)
        end_time = time.time()
        execution_time += end_time - start_time
        cache.record_stop(image_name, container_name)
       
        time.sleep(math.sqrt(execution_time))

    with global_lock:
        global total_cache_miss
        total_cache_miss += cache_miss
        global total_pulling_time
        total_pulling_time += pulling_time
        global pandas_table
        pandas_table.loc[container_name] = [cache_miss/iterations, pulling_time/iterations, execution_time/iterations]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", "-i", type=str, default="master")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--time_window", "-t", type=int, required=False, default=60)
    args = parser.parse_args()
    registry_ip = args.ip
    iterations = [10, 8, 6, 3]
    num_apps = len(iterations)
    total_iterations = sum(iterations)
    policies = [EvictionPolicy.LEAST_FREQUENTLY_USED, EvictionPolicy.LEAST_TOTAL_TIME_USED]

    # Run the experiment for each policy
    
    for policy in policies:
        
        global total_cache_miss
        global total_pulling_time
        global pandas_table
        total_cache_miss = 0
        total_pulling_time = 0
        columns = ["Cache Miss Rate", "Startup Time (s)", "Execution Time (s)"]
        pandas_table = pd.DataFrame(columns=columns)
        # Clean up the images
        for i in range(num_apps):
            subprocess.run(f"docker rmi {registry_ip}:5000/image-cache-app{i+1}:latest", shell=True, capture_output=not args.verbose, text=True)

        # Initialize the cache
        cache = DockerImageCache(time_window=args.time_window, cache_size=num_apps-1, policy=policy)
        folders_to_zip = [
            os.path.join(project_dir, f'data/app{i+1}/zip') for i in range(num_apps)
        ]
        # Create one thread for each function
        threads = []
        for i, folder in enumerate(folders_to_zip):
            thread = threading.Thread(target=thread_func, args=(cache,folder, f'{registry_ip}:5000/image-cache-app{i+1}:latest', f'app{i+1}', iterations[i], args.verbose))
            threads.append(thread)

        start_time = time.time()
        # Start the threads
        for thread in threads:
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()
        end_time = time.time()

        print(f"{policy} summary:")
        pandas_table = pandas_table.sort_index()
        print(pandas_table)
        print(f"Total cache miss / total iterations: {total_cache_miss} / {total_iterations}")
        print("--------------------------------")

if __name__ == "__main__":
    main()

