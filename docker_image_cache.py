import time
import enum
from collections import defaultdict
from typing import Dict, Set, List, Tuple, Optional


class EvictionPolicy(enum.Enum):
    """Enumeration of available eviction policies."""
    LEAST_FREQUENTLY_USED = 1  # Evict the least frequently used image in the time window
    LEAST_TOTAL_TIME_USED = 2  # Evict the image with the least total usage time


class DockerImageCache:
    """
    An LRU-like cache strategy for Docker image storage.

    This class implements a cache strategy that tracks Docker image usage
    and provides mechanisms to evict images based on different policies:
    1. Least frequently used in a time window
    2. Least total time used
    """

    def __init__(self, time_window: int = 3600, policy: EvictionPolicy = EvictionPolicy.LEAST_FREQUENTLY_USED):
        """
        Initialize the Docker image cache.

        Args:
            time_window: Time window in seconds to consider for usage statistics (default: 1 hour)
            policy: Eviction policy to use (default: LEAST_FREQUENTLY_USED)
        """
        # Map of image_id -> set of container_ids using this image
        self.image_containers: Dict[str, Set[str]] = defaultdict(set)

        # Map of image_id -> list of timestamps when the image was used
        self.image_usage_history: Dict[str, List[float]] = defaultdict(list)

        # Map of image_id -> total usage time (in seconds)
        self.image_total_usage_time: Dict[str, float] = defaultdict(float)

        # Map of (image_id, container_id) -> start timestamp
        self.container_start_times: Dict[Tuple[str, str], float] = {}

        # Time window to consider for usage statistics (in seconds)
        self.time_window = time_window

        # Eviction policy to use
        self.policy = policy

    def detect_run(self, image_id: str, container_id: str) -> None:
        """
        Called when an image is used for a container.

        Args:
            image_id: The ID of the Docker image
            container_id: The ID of the container using the image
        """
        # Record that this container is using this image
        self.image_containers[image_id].add(container_id)

        # Record the current time as a usage timestamp
        current_time = time.time()
        self.image_usage_history[image_id].append(current_time)

        # Store the start time for this container/image pair
        self.container_start_times[(image_id, container_id)] = current_time

    def detect_stop(self, image_id: str, container_id: str) -> None:
        """
        Called when an image is no longer used for a container.

        Args:
            image_id: The ID of the Docker image
            container_id: The ID of the container that was using the image
        """
        # Calculate usage time if we have a start time for this container/image pair
        if (image_id, container_id) in self.container_start_times:
            start_time = self.container_start_times[(image_id, container_id)]
            end_time = time.time()
            usage_time = end_time - start_time

            # Add the calculated usage time to the total for this image
            self.image_total_usage_time[image_id] += usage_time

            # Remove the start time entry
            del self.container_start_times[(image_id, container_id)]

        # Remove this container from the set of containers using this image
        if image_id in self.image_containers and container_id in self.image_containers[image_id]:
            self.image_containers[image_id].remove(container_id)

    def get_unused_images(self) -> List[str]:
        """
        Get a list of images that are not currently used by any containers.

        Returns:
            A list of image IDs that are not in use
        """
        return [
            image_id for image_id, containers in self.image_containers.items()
            if len(containers) == 0
        ]

    def count_recent_usage(self, image_id: str) -> int:
        """
        Count how many times an image was used within the time window.

        Args:
            image_id: The ID of the Docker image

        Returns:
            The number of times the image was used within the time window
        """
        if image_id not in self.image_usage_history:
            return 0

        current_time = time.time()
        cutoff_time = current_time - self.time_window

        # Count usages that occurred within the time window
        recent_usages = sum(
            1 for timestamp in self.image_usage_history[image_id]
            if timestamp >= cutoff_time
        )

        return recent_usages

    def get_total_usage_time(self, image_id: str) -> float:
        """
        Get the total time an image has been used.

        Args:
            image_id: The ID of the Docker image

        Returns:
            The total time the image has been used (in seconds)
        """

        return self.image_total_usage_time.get(image_id, 0)

    def evict(self, policy: Optional[EvictionPolicy] = None) -> Optional[str]:
        """
        Select an image that is no longer in use based on the specified eviction policy.

        Args:
            policy: Eviction policy to use (default: None, which uses the policy specified at initialization)

        Returns:
            The ID of the image to evict, or None if no images can be evicted
        """
        # Get list of images not in use by any containers
        unused_images = self.get_unused_images()

        if not unused_images:
            return None  # No images available for eviction

        # Use the specified policy or the default policy
        active_policy = policy if policy is not None else self.policy

        if active_policy == EvictionPolicy.LEAST_FREQUENTLY_USED:
            # Find the image with the least usage in the time window
            least_used_image = min(
                unused_images,
                key=self.count_recent_usage
            )
            return least_used_image
        elif active_policy == EvictionPolicy.LEAST_TOTAL_TIME_USED:
            # Find the image with the least total usage time
            least_time_used_image = min(
                unused_images,
                key=lambda image_id: self.get_total_usage_time(image_id)
            )
            return least_time_used_image
        else:
            raise ValueError(f"Unknown eviction policy: {active_policy}")

    def get_image_stats(self) -> List[Tuple[str, int, int, float]]:
        """
        Get statistics about all images in the cache.

        Returns:
            A list of tuples (image_id, container_count, recent_usage_count, total_usage_time)
        """
        stats = []
        for image_id in self.image_containers:
            container_count = len(self.image_containers[image_id])
            recent_usage_count = self.count_recent_usage(image_id)
            total_usage_time = self.get_total_usage_time(image_id)
            stats.append((image_id, container_count,
                         recent_usage_count, total_usage_time))

        return stats
