### STEP 1: Prerequisites: ###
sudo apt-get update
sudo apt-get -y upgrade

sudo apt-get install -y docker.io
sudo apt-get install -y docker-compose (make sure docker-compose is version 1.29.2 or higher - especially on debian!)

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
  + port=port where the webapp is listening
- Create an another .env file in the von-network folder. It should include the following parameters:
  + DOCKERHOST= the same IP-Adress as previous
  + WEB_SERVER_HOST_PORT=9700 (or any other port not used by the prototype)
  + REGISTER_NEW_DIDS=True
  + LEDGER_INSTANCE_NAME=ePrescription-Demo (for example)

### STEP 3: Add the path to genesis.txt into the first env-file
- genesis_url=DOCKERHOST:WEB_SERVER_HOST_PORT/genesis

### STEP 4: Start the demo: ###
- Start the portable development Indy Node Network
  - In the von-network directory
    -./manage build
    -./manage start
- In the project directory,
    - run 'docker-compose up'
    - ...and enjoy our demo! :)



### Used Ports:
- Web-Apps: specified in .env
- Insurance-Agent: Port 6000 / API 6080
- Doctor-Agent: Port 7000 / API 7080
- Pharmacy-Agent: Port 9000 / API 9080
- Quorum-Network:
  + 22001 - 22003 (for node gossip)
  + 23001 - 23003 (Node RPC for interacting with the blockchain)
  + 50401 - 50403 (for RAFT consensus)
- von-network
  + specified in .env (WEB_SERVER_HOST_PORT)
  + 9701-9708
- Other: Port 8999 (really?)

# Description
The application launches two blockchains (a local Quorum-network and an Indy blockchain for handling SSI operations).
To interact with the SSI applications, a standardized wallet and generic protocols, such as aca-py, are used (and launched).
The patient is at the center of the application and the data finally belongs to the one person, whom it concerns most.
The front-end is organized as a Django project. Web-Apps simplify interaction for issuers and verifiers of digital health credentials.
A specialty - which extends the 'classic' SSI cases, is the prevention of double-spending of credentials, which is of utmost importance in the ePrescriptions use case. 
