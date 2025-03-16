import subprocess
from docker_image_cache import DockerImageCache
import threading



def thread1(cache,folder_to_zip):
    image_name = 'image-cache-app1:latest'
    container_name = 'container1'
    subprocess.run(f"docker pull {image_name}")
    cache.detect_run(image_name, container_name)
    subprocess.run(f"docker run -v {folder_to_zip}:/files --rm --name {container_name} {image_name}")
    cache.detect_stop(image_name, container_name)
    image_to_evict = cache.evict()
    subprocess.run(f"docker rmi {image_to_evict}")


def thread2(cache,folder_to_zip):
    image_name = 'image-cache-app2:latest'
    container_name = 'container2'
    subprocess.run(f"docker pull {image_name}")
    cache.detect_run(image_name, container_name)
    subprocess.run(f"docker run -v {folder_to_zip}:/files --rm --name {container_name} {image_name}")
    cache.detect_stop(image_name, container_name)
    image_to_evict = cache.evict()
    subprocess.run(f"docker rmi {image_to_evict}")

def main():
    cache = DockerImageCache(time_window=60)
    folder_to_zip = '/tmp/image_cache'  
    
    # Create one thread for each function
    thread1 = threading.Thread(target=thread1, args=(cache,folder_to_zip))
    thread2 = threading.Thread(target=thread2, args=(cache,folder_to_zip))

    # Start the threads
    thread1.start()
    thread2.start()
