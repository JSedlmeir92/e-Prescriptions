#!/bin/bash

#pip install -r requirements.txt

#start von-network
cd von-network

./manage start

cd ..

sleep 5

# start demo

docker-compose up -d
