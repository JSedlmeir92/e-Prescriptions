### Clone recursively to get aries-cloudagent-python, indy-tails-server and quorum-examples

git clone --recurse-submodules https://github.com/JSedlmeir92/e-Prescriptions.git

### PART 1: Prerequisites: ### 
sudo apt-get update
sudo apt-get -y upgrade

sudo apt-get install -y docker.io
sudo apt-get install -y docker-compose (make sure docker-compose is version 1.29.2 or higher)

sudo usermod -aG docker "$USER"
newgrp docker

sudo reboot


### END PART 1 ###

sudo apt-get install -y python3-pip
python3 -m pip install -y django
pip3 install python-dateutil django-tables2

### PART 2: Start the demo: ### 

- Check if port 8000 (Web-Apps) and 9000 (pharmarcy's agent) can be accessed from the outside.
- ./start.sh
    - Builds and runs the docker-container as a deamon 
    - starts django
    - it deletes the sqlite-database and the docker-container, only if the docker-daemon was stopped --> docker-compose stop)

### Used Ports:
Web-Apps: Port 8000

Doctor-Agent: Port 7000 / API 7080

Pharmacy-Agent: Port 9000 / API 9080


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

