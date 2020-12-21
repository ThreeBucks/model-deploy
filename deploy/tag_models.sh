#!/bin/bash

cat deploy/models_tag_info.txt | while read line
do
    array=($line)
    docker pull ${array[0]}
    docker tag ${array[0]} ${array[1]}
    docker push ${array[1]}
    docker rmi ${array[0]}
    docker rmi ${array[1]}
done