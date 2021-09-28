#!/bin/bash

echo "update and upgrade"
sudo apt-get update && sudo apt-get -y upgrade

echo "install docker and docker-compose"
sudo apt-get install -y docker.io && sudo apt-get install -y docker-compose
sudo usermod -aG docker "$USER" && newgrp docker

echo "install python and django"
sudo apt-get install -y python3-pip
python3 -m pip install django

echo "install nvm and node 8.16.0"
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash
. ~/.nvm/nvm.sh
. ~/.profile
. ~/.bashrc

nvm install 8.16.0 echo "export PATH=$PATH:/home/$USER/.nvm/versions/node/v8.16.0/bin" >> "/home/$USER/.profile"
. ~/.profile
. ~/.bashrc

echo "install truffle"
npm install -g truffle@5.1.39

echo "install quorum packages"
cd $(pwd)/quorum_client && npm install
