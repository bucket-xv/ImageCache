# Docker Image LRU Cache

This project implements an LRU-like (Least Recently Used) cache strategy for Docker image storage. It provides a mechanism to track Docker image usage and evict images that are no longer in use based on configurable eviction policies.

## Overview

The cache strategy is designed to optimize Docker image storage by removing images that are:
1. Not currently used by any containers
2. Selected based on one of two eviction policies:
   - **Least Frequently Used**: Images that have been used least frequently within a configurable time window
   - **Least Total Time Used**: Images that have the lowest total usage time

This implementation is particularly useful for serverless environments where efficient management of Docker images is crucial for performance and resource utilization.

## Features

- Track when Docker images are used by containers
- Track when Docker images are no longer used by containers
- Track usage time for Docker images
- Identify images that are candidates for eviction based on different policies
- Configurable time window for usage statistics
- Simple API with three main interfaces
- Support for multiple eviction policies

## Eviction Policies

The cache supports two eviction policies:

1. **LEAST_FREQUENTLY_USED** (default): Evicts the image that has been used the least number of times within the configured time window.
2. **LEAST_TOTAL_TIME_USED**: Evicts the image that has the lowest total usage time.

## API

The `DockerImageCache` class provides the following interfaces:

### `detect_run(image_id, container_id, usage_time=0)`

Called when an image is used for a container.

- **Parameters**:
  - `image_id` (str): The ID of the Docker image
  - `container_id` (str): The ID of the container using the image
  - `usage_time` (float, optional): The time spent using the image in seconds. This is used for the LEAST_TOTAL_TIME_USED policy.

### `detect_stop(image_id, container_id)`

Called when an image is no longer used for a container.

- **Parameters**:
  - `image_id` (str): The ID of the Docker image
  - `container_id` (str): The ID of the container that was using the image

### `evict(policy=None)`

Selects an image that is no longer in use based on the specified eviction policy.

- **Parameters**:
  - `policy` (EvictionPolicy, optional): The eviction policy to use. If not provided, the policy specified at initialization is used.

- **Returns**:
  - The ID of the image to evict, or `None` if no images can be evicted

## Additional Methods

The class also provides some helper methods:

- `get_unused_images()`: Returns a list of images not currently used by any containers
- `count_recent_usage(image_id)`: Counts how many times an image was used within the time window
- `get_total_usage_time(image_id)`: Gets the total time an image has been used
- `get_image_stats()`: Returns statistics about all images in the cache

## Usage Example

```python
from docker_image_cache import DockerImageCache, EvictionPolicy

# Initialize the cache with a 1-hour time window and the default policy (LEAST_FREQUENTLY_USED)
cache = DockerImageCache(time_window=3600)

# Or initialize with a specific policy
cache = DockerImageCache(
    time_window=3600,
    policy=EvictionPolicy.LEAST_TOTAL_TIME_USED
)

# When a container starts using an image (with optional usage time)
cache.detect_run("image123", "container456", usage_time=10)

# When a container stops using an image
cache.detect_stop("image123", "container456")

# When you need to free up space by removing an unused image
# (using the policy specified at initialization)
image_to_remove = cache.evict()

# Or override the policy at eviction time
image_to_remove = cache.evict(policy=EvictionPolicy.LEAST_TOTAL_TIME_USED)
if image_to_remove:
    print(f"Evicting image: {image_to_remove}")
else:
    print("No images available for eviction")
```

## Testing

The project includes a test file `test_docker_image_cache.py` that demonstrates the functionality of the cache. Run the tests with:

```bash
python test_docker_image_cache.py
```

## Integration

To integrate this cache strategy into your Docker image management system:

1. Import the `DockerImageCache` class
2. Initialize it with an appropriate time window
3. Call `detect_run()` when containers start using images
4. Call `detect_stop()` when containers stop using images
5. Periodically call `evict()` to identify images that can be safely removed

## Customization

You can customize the cache behavior by:

- Adjusting the `time_window` parameter to consider longer or shorter usage history
- Choosing the appropriate eviction policy for your use case
- Extending the class to implement more sophisticated eviction strategies
- Adding additional metrics for image selection
