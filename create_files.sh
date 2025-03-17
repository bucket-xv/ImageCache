mkdir -p data/app1/zip
mkdir -p data/app2/zip
dd if=/dev/urandom of=data/app1/zip/file.img bs=1M count=512
dd if=/dev/urandom of=data/app2/zip/file2.img bs=1M count=1