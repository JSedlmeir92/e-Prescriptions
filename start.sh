#!/bin/bash

pip3 install -r requirements.txt
apt-get -y update
apt-get -y install npm
npm i truffle -g
python3 start_demo.py
