import subprocess
from docker_image_cache import DockerImageCache, EvictionPolicy
import threading
import time
import argparse
import os
total_cache_miss = 0
total_cache_miss_lock = threading.Lock()
total_pulling_time = 0
total_pulling_time_lock = threading.Lock()

project_dir = os.path.dirname(os.path.abspath(__file__))

def thread_func(cache, folder_to_zip, image_name, container_name, iterations, verbose=False):
    cache_miss = 0
    pulling_time = 0
    for i in range(iterations):
        print(f"Iteration {i+1} of {iterations} with image {image_name}")
        result = subprocess.run(f"docker images -q {image_name}", shell=True, capture_output=True, text=True)

        # When the image is not in the cache, it will be pulled, and the cache will be updated
        cache.detect_run(image_name, container_name)
        if result.stdout.strip() == '':
            start_time = time.time()
            subprocess.run(f"docker pull {image_name}", shell=True,capture_output=not verbose, text=True)
            end_time = time.time()
            pulling_time += end_time - start_time
            cache_miss += 1
        else:
            print(f"Image {image_name} already in cache")
        
        # Run the container
        subprocess.run(f"docker run -v {folder_to_zip}:/files --rm --name {container_name} {image_name}", shell=True, capture_output=not verbose, text=True)
        cache.detect_stop(image_name, container_name)
        image_to_evict = cache.evict()
        if image_to_evict is not None:
            print(f"Evicting image: {image_to_evict}")
            subprocess.run(f"docker rmi {image_to_evict}", shell=True, capture_output=not verbose, text=True)
        time.sleep(1)

    with total_cache_miss_lock:
        global total_cache_miss
        total_cache_miss += cache_miss
    with total_pulling_time_lock:
        global total_pulling_time
        total_pulling_time += pulling_time

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, required=True)
    args = parser.parse_args()
    registry_ip = args.ip

    cache = DockerImageCache(time_window=60, cache_size=2, policy=EvictionPolicy.LEAST_FREQUENTLY_USED)
    folders_to_zip = [
        os.path.join(project_dir, f'data/app{i+1}/zip') for i in range(3)
    ]
    iterations = [4, 8, 16]
    total_iterations = sum(iterations)

    # Create one thread for each function
    threads = []
    for i, folder in enumerate(folders_to_zip):
        thread = threading.Thread(target=thread_func, args=(cache,folder, f'{registry_ip}:5000/image-cache-app{i+1}:latest', f'container{i+1}', iterations[i]))
        threads.append(thread)


    # Start the threads
    for thread in threads:
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Clean up the images
    for i in range(len(folders_to_zip)):
        subprocess.run(f"docker rmi {registry_ip}:5000/image-cache-app{i+1}:latest", shell=True, text=True)

    print("All threads have finished")
    print(f"Total cache miss / total iterations: {total_cache_miss} / {total_iterations}")
    print(f"Total pulling time: {total_pulling_time} seconds")

if __name__ == "__main__":
    main()

