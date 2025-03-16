# Image cache for docker

## Prerequisites (You don't need to do this, this is just for development)

1. Build docker images
```bash
docker build -t image-cache-app1:latest app1
docker build -t image-cache-app2:latest app2
./upload.sh
```

## Setup

1. Create random file to zip
```bash
./create_files.sh
```


