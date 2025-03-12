import time
from docker_image_cache import DockerImageCache, EvictionPolicy


def test_basic_functionality():
    """Test the basic functionality of the Docker image cache with the default policy."""
    cache = DockerImageCache(time_window=60)  # 1 minute window for testing

    # Simulate some container builds
    cache.detect_build("image1", "container1")
    cache.detect_build("image1", "container2")
    cache.detect_build("image2", "container3")
    cache.detect_build("image3", "container4")

    # Check that no images are unused yet
    assert len(cache.get_unused_images()) == 0

    # Simulate removing some containers
    cache.detect_remove("image1", "container1")

    # image1 should still be in use by container2
    assert "image1" not in cache.get_unused_images()

    # Remove the last container using image1
    cache.detect_remove("image1", "container2")

    # Now image1 should be unused
    assert "image1" in cache.get_unused_images()

    # The least used image should be image1 (it has 2 usages but is unused)
    assert cache.evict() == "image1"

    print("Basic functionality test passed!")


def test_time_window():
    """Test the time window functionality of the Docker image cache with the default policy."""
    cache = DockerImageCache(time_window=2)  # 2 second window for testing

    # Simulate some container builds
    cache.detect_build("image1", "container1")
    cache.detect_build("image2", "container2")

    # Wait for 1 second
    time.sleep(1)

    # Use image2 again
    cache.detect_build("image2", "container3")

    # Remove all containers
    cache.detect_remove("image1", "container1")
    cache.detect_remove("image2", "container2")
    cache.detect_remove("image2", "container3")

    # Both images should be unused now
    assert "image1" in cache.get_unused_images()
    assert "image2" in cache.get_unused_images()

    # image1 should be evicted first as it was used less recently
    assert cache.evict() == "image1"

    # Wait for 2 more seconds (exceeding the time window)
    time.sleep(2)

    # Now both images should have 0 recent usages
    assert cache.count_recent_usage("image1") == 0
    assert cache.count_recent_usage("image2") == 0

    print("Time window test passed!")


def test_least_total_time_used_policy():
    """Test the least total time used eviction policy."""
    cache = DockerImageCache(
        time_window=60,
        policy=EvictionPolicy.LEAST_TOTAL_TIME_USED
    )

    # Simulate some container builds with different usage times
    cache.detect_build("image1", "container1", usage_time=10)  # 10 seconds
    cache.detect_build("image2", "container2", usage_time=5)   # 5 seconds
    cache.detect_build("image3", "container3", usage_time=15)  # 15 seconds

    # Check that no images are unused yet
    assert len(cache.get_unused_images()) == 0

    # Simulate removing all containers
    cache.detect_remove("image1", "container1")
    cache.detect_remove("image2", "container2")
    cache.detect_remove("image3", "container3")

    # All images should be unused now
    assert len(cache.get_unused_images()) == 3

    # The image with the least total usage time should be image2 (5 seconds)
    evicted_image = cache.evict()
    assert evicted_image == "image2"

    # Manually remove image2 from the cache to simulate it being deleted
    # This is necessary because our cache implementation doesn't actually delete images
    cache.image_containers.pop("image2")
    cache.image_usage_history.pop("image2")
    cache.image_total_usage_time.pop("image2")

    # Use image1 again with additional time
    # Now image1 has 18 seconds total
    cache.detect_build("image1", "container4", usage_time=8)
    cache.detect_remove("image1", "container4")

    # Debug: Print the total usage times for each image
    print(
        f"DEBUG: image1 total usage time: {cache.get_total_usage_time('image1')}")
    print(
        f"DEBUG: image3 total usage time: {cache.get_total_usage_time('image3')}")
    print(f"DEBUG: Unused images: {cache.get_unused_images()}")

    # With LEAST_TOTAL_TIME_USED policy, image3 should be evicted next
    # because it has less total time (15 seconds) than image1 (18 seconds)
    evicted_image = cache.evict()
    print(f"DEBUG: Evicted image: {evicted_image}")
    assert evicted_image == "image3"

    # Manually remove image3 from the cache to simulate it being deleted
    cache.image_containers.pop("image3")
    cache.image_usage_history.pop("image3")
    cache.image_total_usage_time.pop("image3")

    # Only image1 should be left
    assert len(cache.get_unused_images()) == 1
    assert cache.get_unused_images()[0] == "image1"

    print("Least total time used policy test passed!")


def test_policy_override():
    """Test overriding the eviction policy at eviction time."""
    # Initialize with LEAST_FREQUENTLY_USED policy
    cache = DockerImageCache(
        time_window=60,
        policy=EvictionPolicy.LEAST_FREQUENTLY_USED
    )

    # Simulate some container builds with different usage patterns
    # image1: Used once with 20 seconds
    cache.detect_build("image1", "container1", usage_time=20)

    # image2: Used twice with 5 seconds each (10 seconds total)
    cache.detect_build("image2", "container2", usage_time=5)
    cache.detect_build("image2", "container3", usage_time=5)

    # Remove all containers
    cache.detect_remove("image1", "container1")
    cache.detect_remove("image2", "container2")
    cache.detect_remove("image2", "container3")

    # With LEAST_FREQUENTLY_USED policy, image1 should be evicted (used once vs twice)
    assert cache.evict() == "image1"

    # Add image1 back
    cache.detect_build("image1", "container4", usage_time=0)
    cache.detect_remove("image1", "container4")

    # With LEAST_TOTAL_TIME_USED policy, image2 should be evicted (10 seconds vs 20 seconds)
    assert cache.evict(policy=EvictionPolicy.LEAST_TOTAL_TIME_USED) == "image2"

    print("Policy override test passed!")


def main():
    """Run all tests."""
    print("Testing Docker Image Cache...")
    test_basic_functionality()
    test_time_window()
    test_least_total_time_used_policy()
    test_policy_override()
    print("All tests passed!")


if __name__ == "__main__":
    main()
