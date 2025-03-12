#!/usr/bin/env python3
"""
Example usage of the Docker Image Cache.

This script demonstrates how to integrate the DockerImageCache into a
Docker image management system. It simulates a scenario where containers
are created and destroyed, and the cache is used to manage Docker images
with different eviction policies.
"""

import time
import random
from docker_image_cache import DockerImageCache, EvictionPolicy


def simulate_docker_environment(duration=30, time_window=300, policy=EvictionPolicy.LEAST_FREQUENTLY_USED):
    """
    Simulate a Docker environment where containers are created and destroyed.

    Args:
        duration: Duration of the simulation in seconds
        time_window: Time window for the cache in seconds
        policy: Eviction policy to use
    """
    # Initialize the cache with the specified policy
    cache = DockerImageCache(time_window=time_window, policy=policy)

    # Available images for simulation
    images = [f"image{i}" for i in range(1, 6)]  # image1, image2, ..., image5

    # Track active containers
    active_containers = {}  # container_id -> image_id
    container_counter = 0

    print(f"Starting Docker environment simulation (duration: {duration}s)")
    print(
        f"Using cache with time window of {time_window}s and policy: {policy.name}")
    print("-" * 60)

    start_time = time.time()
    while time.time() - start_time < duration:
        # Randomly decide what action to take
        action = random.choice(["create", "destroy", "evict"])

        if action == "create" or (action == "destroy" and not active_containers):
            # Create a new container
            container_counter += 1
            container_id = f"container{container_counter}"
            image_id = random.choice(images)

            print(
                f"Creating container {container_id} using image {image_id}")
            cache.detect_run(image_id, container_id)
            active_containers[container_id] = image_id

        elif action == "destroy" and active_containers:
            # Destroy a random container
            container_id = random.choice(list(active_containers.keys()))
            image_id = active_containers[container_id]

            print(
                f"Destroying container {container_id} (was using image {image_id})")
            cache.detect_stop(image_id, container_id)
            del active_containers[container_id]

        elif action == "evict":
            # Try to evict an unused image
            image_to_evict = cache.evict()
            if image_to_evict:
                print(f"Evicting unused image: {image_to_evict}")
            else:
                print("No images available for eviction")

        # Print current stats
        print("\nCurrent status:")
        print(f"Active containers: {len(active_containers)}")
        unused_images = cache.get_unused_images()
        print(
            f"Unused images: {len(unused_images)} {unused_images if unused_images else ''}")

        # Print detailed image stats
        print("\nImage statistics:")
        for image_id, container_count, usage_count, total_time in cache.get_image_stats():
            print(
                f"  {image_id}: {container_count} containers, {usage_count} recent usages, {total_time:.1f}s total time")

        print("-" * 60)
        time.sleep(2)  # Wait for 2 seconds between actions

    print("Simulation completed")
    print("\nFinal statistics:")
    for image_id, container_count, usage_count, total_time in cache.get_image_stats():
        print(
            f"  {image_id}: {container_count} containers, {usage_count} recent usages, {total_time:.1f}s total time")


def compare_eviction_policies():
    """
    Compare the two eviction policies by running two simulations with the same random seed.
    """
    print("=" * 80)
    print("COMPARING EVICTION POLICIES")
    print("=" * 80)

    # Set a fixed random seed for reproducibility
    random.seed(42)

    print("\n1. LEAST FREQUENTLY USED POLICY\n")
    simulate_docker_environment(
        duration=20,
        time_window=300,
        policy=EvictionPolicy.LEAST_FREQUENTLY_USED
    )

    print("\n" + "=" * 80)

    # Reset the random seed to get the same sequence of events
    random.seed(42)

    print("\n2. LEAST TOTAL TIME USED POLICY\n")
    simulate_docker_environment(
        duration=20,
        time_window=300,
        policy=EvictionPolicy.LEAST_TOTAL_TIME_USED
    )

    print("\n" + "=" * 80)
    print("COMPARISON COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    # Compare the two eviction policies
    compare_eviction_policies()
