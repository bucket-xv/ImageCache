import subprocess
from docker_image_cache import DockerImageCache
import threading


def thread1(cache):
    image_name = 'ubuntu'
    container_name = 'container1'
    subprocess.run(f"docker pull {image_name}")
    cache.detect_run(image_name, container_name)
    subprocess.run(f"docker run --rm --name {container_name} {image_name}")
    cache.detect_stop(image_name, container_name)
    image_to_evict = cache.evict()
    subprocess.run(f"docker rmi {image_to_evict}")


def thread2(cache):
    image_name = 'ubuntu'
    container_name = 'container2'
    subprocess.run(f"docker pull {image_name}")
    cache.detect_run(image_name, container_name)


def main():

    cache = DockerImageCache(time_window=60)

    # Create one thread for each function
    thread1 = threading.Thread(target=thread1, args=(cache,))
    thread2 = threading.Thread(target=thread2, args=(cache,))

    # Start the threads
    thread1.start()
    thread2.start()
