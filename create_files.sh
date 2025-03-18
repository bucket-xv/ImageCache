#!/bin/bash

for i in {1..4}
do
    mkdir -p data/app$i/zip
    dd if=/dev/urandom of=data/app$i/zip/file$i.img bs=1M count=$(($i * $i * 5))
done
