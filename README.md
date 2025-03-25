# Image cache for docker

This is a tool to cache docker images.

<!-- ## Prerequisites (You don't need to do this, this is just for development)

1. Build docker images
```bash
server_ip=121.40.242.35 ./upload.sh root
``` -->

## Requirements

Related docker images must have been pushed to the registry on **master node** using `upload.sh`.

## Setup

![result](images/result.png)

<!-- 0. Clone the repository
```bash
git clone git@github.com:bucket-xv/ImageCache.git
cd ImageCache
``` -->

1. Create random file to setup
```bash
./create_files.sh
```

2. Run the test
```bash
python3 test.py
```



