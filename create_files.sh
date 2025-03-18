mkdir -p data/app1/zip
mkdir -p data/app2/zip
mkdir -p data/app3/zip
dd if=/dev/urandom of=data/app1/zip/file1.img bs=1M count=128
dd if=/dev/urandom of=data/app2/zip/file2.img bs=1M count=32
dd if=/dev/urandom of=data/app3/zip/file3.img bs=1M count=1