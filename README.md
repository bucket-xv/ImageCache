# Image cache for docker

This is a tool to cache docker images.

## Requirements

- Related docker images must have been pushed to the registry on **master node** using `upload.sh`.

```bash
server_ip=xxx ./upload.sh root
```

## Run the test

![result](images/result.png)


1. Create random file to setup
```bash
./create_files.sh
```

2. Run the test
```bash
python3 test.py
```



