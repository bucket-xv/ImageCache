#! /bin/bash

username=$1
registry_ip=master
# Function to upload a certain image to the registry
upload_image() {
    image_name=$1
    docker build -t $image_name app
    docker save -o /tmp/$image_name.zip $image_name
    scp /tmp/$image_name.zip $username@$server_ip:/tmp/$image_name.zip
    ssh $username@$server_ip "sudo docker load -i /tmp/$image_name.zip"
    ssh $username@$server_ip "sudo docker tag $image_name $registry_ip:5000/$image_name"
    ssh $username@$server_ip "sudo docker push $registry_ip:5000/$image_name"
}

# upload_image image-cache-app1:latest
# upload_image image-cache-app2:latest
# upload_image image-cache-app3:latest
upload_image image-cache-app4:latest