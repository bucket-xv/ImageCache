mkdir -p data/app1
mkdir -p data/app2
dd if=/dev/urandom of=data/app1/file.img bs=1M count=128
dd if=/dev/urandom of=data/app2/file2.img bs=1M count=1