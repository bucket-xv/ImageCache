# Image cache for docker

## Prerequisites (You don't need to do this, this is just for development)

1. Build docker images
```bash
docker build -t image-cache-app1:latest app
docker build -t image-cache-app2:latest app
docker build -t image-cache-app3:latest app
server_ip=121.40.242.35 ./upload.sh root
```

## Setup

0. Clone the repository
```bash
git clone git@github.com:bucket-xv/ImageCache.git
cd ImageCache
```

1. Create random file to zip
```bash
./create_files.sh
```

2. Run test
```bash
python3 test.py
```



