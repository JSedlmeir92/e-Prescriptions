

git clone --recursive https://gitlab.fit.fraunhofer.de/vincent.schlatt/sso-prescriptions.git

### PART 1: Prerequisites: ### 
sudo apt-get update
sudo apt-get -y upgrade

sudo apt-get install -y docker.io
sudo apt-get install -y docker-compose

sudo usermod -aG docker "$USER"
newgrp docker

sudo reboot


### END PART 1 ###


sudo apt-get install -y python3-pip
python3 -m pip install -y django


# Node installation: 

wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash
. ~/.nvm/nvm.sh
. ~/.profile
. ~/.bashrc

nvm install 8.16.0
echo "export PATH=$PATH:/home/$USER/.nvm/versions/node/v8.16.0/bin" >> "/home/$USER/.profile"
. ~/.profile
. ~/.bashrc

npm install -g truffle@5.1.39


