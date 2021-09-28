### Clone recursively to get aries-cloudagent-python, indy-tails-server and quorum-examples

git clone --recurse-submodules https://github.com/JSedlmeir92/e-Prescriptions.git

### PART 1: Prerequisites: ### 
1. Updating system: ```sudo apt-get update && sudo apt-get -y upgrade```
2. Installing docker and docker-compose: 
    1. ```sudo apt-get install -y docker.io && sudo apt-get install -y docker-compose``` (make sure docker-compose is version 1.29.2 or higher)
    2. ```sudo usermod -aG docker "$USER" && newgrp docker```
3. Reboot: ```sudo reboot```


### END PART 1 ###

1. Install python: ```sudo apt-get install -y python3-pip```
2. Install django: ```python3 -m pip install -y django```


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

cd /home/$USER/ssi-prescriptions/quorum_client && npm install

