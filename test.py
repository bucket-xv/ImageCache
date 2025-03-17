import subprocess
from docker_image_cache import DockerImageCache
import threading
import time
import argparse
import os
total_cache_miss = 0
total_cache_miss_lock = threading.Lock()

project_dir = os.path.dirname(os.path.abspath(__file__))

def thread_func(cache, folder_to_zip, image_name, container_name, iterations):
    cache_miss = 0
    for i in range(iterations):
        result = subprocess.run(f"docker images -q {image_name}", shell=True, capture_output=True, text=True)
        if result.stdout.strip() == '':
            subprocess.run(f"docker pull {image_name}")
            cache_miss += 1
        cache.detect_run(image_name, container_name)
        subprocess.run(f"docker run -v {folder_to_zip}:/files --rm --name {container_name} {image_name}", shell=True, text=True)
        cache.detect_stop(image_name, container_name)
        image_to_evict = cache.evict()
        if image_to_evict is not None:
            print(f"Evicting image: {image_to_evict}")
            subprocess.run(f"docker rmi {image_to_evict}")
        time.sleep(1)

    with total_cache_miss_lock:
        total_cache_miss += cache_miss
    return cache_miss

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, required=True)
    args = parser.parse_args()
    registry_ip = args.ip

    cache = DockerImageCache(time_window=60, cache_size=1)
    folder1_to_zip = os.path.join(project_dir, 'data/app1')  
    folder2_to_zip = os.path.join(project_dir, 'data/app2')

    # Create one thread for each function
    thread1 = threading.Thread(target=thread_func, args=(cache,folder1_to_zip, f'{registry_ip}:5000/image-cache-app1:latest', 'container1', 10))
    thread2 = threading.Thread(target=thread_func, args=(cache,folder2_to_zip, f'{registry_ip}:5000/image-cache-app2:latest', 'container2', 30))

    # Start the threads
    thread1.start()
    thread2.start()

    # Wait for all threads to finish
    thread1.join()
    thread2.join()

    print("All threads have finished")

if __name__ == "__main__":
    main()

