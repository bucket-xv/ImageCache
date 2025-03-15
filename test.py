import subprocess
from docker_image_cache import DockerImageCache

cache = DockerImageCache(time_window=60)
image_name = 'ubuntu'
container_name = 'container1'
subprocess.run(f"docker pull {image_name}")
cache.detect_run(image_name, container_name)
subprocess.run(f"docker run --rm --name {container_name} {image_name}")
cache.detect_stop(image_name, container_name)
image_to_evict = cache.evict()
subprocess.run(f"docker rmi {image_to_evict}")

