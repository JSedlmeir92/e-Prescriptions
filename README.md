# Let'sFixID Digital Health Ecosystem - ePrescriptions

git clone --recurse-submodules https://github.com/lukwil/letsfixid

### STEP 1: Prerequisites: ###
sudo apt-get update
sudo apt-get -y upgrade

sudo apt-get install -y docker.io
sudo apt-get install -y docker-compose (make sure docker-compose is version 1.29.2 or higher)

sudo usermod -aG docker "$USER"
newgrp docker

sudo reboot

sudo apt-get install -y python3-pip
python3 -m pip install -y django
pip3 install python-dateutil django-tables2

### STEP 2: Configuration

- Make sure that the ports in the Used Ports section are open for your docker network.
  The doctor agent and pharmacy agent must be available from your mobile phone with the SSI wallet app.   
- Create a .env file in the main directory. It should look as follows:
  + ip_address=IP address where the application is running and that is available for your mobile phone
  + dir_name=path to the directory of the project, e.g., /home/user/e-Prescriptions
  + port =port where the webapp is listening
### STEP 3: Start the demo: ###

In the project directory,
    - run 'docker-compose up'
    - ...and enjoy our demo! :)

### Used Ports:
- Web-Apps: specified in .env
- Doctor-Agent: Port 7000 / API 7080
- Pharmacy-Agent: Port 9000 / API 9080
- Quorum-Network:
  + 22001 - 22003 (for node gossip)
  + 23001 - 23003 (Node RPC for interacting with the blockchain)
  + 50401 - 50403 (for RAFT consensus)
- Other: Port 8999

# Description
The application launches two blockchains (the PBS blockchain from Luxemburg and an Indy blockchain for handling SSI operations).
To interact with the SSI applications, a standardized wallet and generic protocols, such as aca-py, are used (and launched).
The patient is at the center of the application and the data finally belongs to the one person, whom it concerns most.
The front-end is organized as a Django project. Web-Apps simplify interaction for issuers and verifiers of digital health credentials.
A specialty - which extends the 'classic' SSI cases, is the prevention of double-spending of credentials, which is of utmost importance in the ePrescriptions use case. 
