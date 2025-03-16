# Image cache for docker

## Prerequisites (You don't need to do this, this is just for development)

1. Build docker images
```bash
docker build -t image-cache-app1:latest app1
docker build -t image-cache-app2:latest app2
server_ip=121.40.242.35 registry_ip=192.168.0.17 ./upload.sh root
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

2. Run docker compose
```bash
docker compose up
```



