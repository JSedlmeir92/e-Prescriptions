### Clone recursively to get aries-cloudagent-python, indy-tails-server and quorum-examples

git clone --recurse-submodules https://github.com/JSedlmeir92/e-Prescriptions.git

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
- Create an .env file in the main directory. It should look as follows:
  + ip_address=<<IP address where the application is running and that is available from your mobile phone>>
  + dir_name=<<path to the directory of the project, e.g., /home/user/e-Prescriptions>>

### STEP 3: Start the demo: ### 

In the project directory, run ./start.sh.
    - Builds and runs the docker-container as a daemon 
    - Starts django
    - Deletes the sqlite-database and the docker-container, only if the docker-daemon was stopped --> docker-compose stop)

### Used Ports:
- Web-Apps: Port 8000
- Doctor-Agent: Port 7000 / API 7080
- Pharmacy-Agent: Port 9000 / API 9080
- Quorum-Network: 
  + 22001 - 22003 (for node gossip)
  + 23001 - 23003 (Node RPC for interacting with the blockchain)
  + 50401 - 50403 (for RAFT consensus)


# Node installation (will be unnecessary as soon as the django applications will be dockerized): 

wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash
. ~/.nvm/nvm.sh
. ~/.profile
. ~/.bashrc

nvm install 8.16.0
echo "export PATH=$PATH:/home/$USER/.nvm/versions/node/v8.16.0/bin" >> "/home/$USER/.profile"
. ~/.profile
. ~/.bashrc

npm install -g truffle@5.1.39

cd quorum_client && npm install



# A brief overview of the view-functions used in the pharmacy-app
  #### /
  path('', views.home_view, name='pharmacy-home'),
  
  - No functions
  #### login/
  path('login/', views.login_view, name='pharmacy-connection'),
  
  path('login/<int:way>', views.login_view, name='pharmacy-connection'),
  - checks if a SCHEMA and a CREDENTIAL DEFINITION are available.
  - The old Way; Displays the QR-Code for the proof-invitation AND redirects **directly** without an ID to **login-confirmation**/
    - uses *http-equiv="refresh"* content in the html-header
  -  Parameter: 
      - way 1 = connectionless (default, when no parameter is provided)
      - way 2 = connectionbased
  #### login-connectionless/
  path('login-connectionless/', views.login_connectionless_view, name='pharmacy-connectionless'),
  - The new way (Using the prescription-overview): Displays a **static** QR-Code for the connectionless proof
  - QR-Code points to login_url/
  #### login_url
  path('login_url', views.login_url_view, name='pharmacy-connectionless_url'),

  - Redirects to the pharmacy-agent with the required parameters for the connectionless proof 
    - The invitation_url contains the invitation_string
      - see: https://ldej.nl/post/building-an-acapy-controller-accounts/#qr-codes-and-links
  #### login-confirmation/<int:id>
  path('login-confirmation/', views.login_confirmation_view, name='pharmacy-connection_confirmation'),
 
  path('login-confirmation/<int:id>', views.login
  
  - If no ID is provided: waits in a loop until a proof is presented
  - If an ID is provided, retrieves the data directly from the database
  - Gives the last chance before spending the ePrescription
    - links to login-result with the corrosponding ID
  #### login-result/<int:id>
  path('login-result/<int:id>', views.login_result_view, name='pharmacy-connection_result')
  
  - If no ID is provided: Redeem the ePrescription the old way 
    - Waits until a proof is presented and gets the data directly from the presented proof
    --> **not used in the current version**, because the view is always called with parameter
  - If an ID is provided: Redeem the ePrescription
    - Gets the data from the database
  - When a prescription is redeemed, the following attributes are updated in the database:
    - not_spent = False
    - redeemed = True (redeemed by the pharmarcy)
    - date_redeemed = now()
  #### logged-in/
  path('logged-in/', views.logged_in_view, name='pharmacy-logged_in'),
  - Presentation of the spent ePrescription --NOT USED

  ### Pharmarcy - Prescription Overview
  #### prescription/
  path("prescription/", views.prescription_table_view, name="pharmacy-prescription-table"),
  - displays all prescription saved in the database
  #### prescription/detail/<int:id>/
  path('prescription/detail/<int:id>/', views.prescription_detail_view, name='pharmacy-prescription_detail'),
  - Shows more information about an ePrescription
  - ID is mandotory! 
  #### prescription/delete_item/<int:id>
  path('prescription/delete_item/<int:id>', views.prescription_delete_item_view, name="pharmacy-prescription_delete_item"),
  - Deletes the ePrescription from the database and redirects to pharmacy-prescription-table
  - without a html-template
  #### prescription/check_item/<int:id>
  path('prescription/check_item/<int:id>', views.prescription_check_item_view, name="pharmacy-prescription_check_item"), 
  - Not implemented
 
  ## WEBHOOKS
  #### topic/connections/
  path('topic/connections/', views.webhook_connection_view, name='pharmacy-webhook_connection'),
  - Connectionbased Proof: Creates the proof-request and sends it to the prover
  #### topic/present_proof/
  path('topic/present_proof/', views.webhook_proof_view, name='pharmacy-webhook_proof'),
  - Saves the presented proof into the database
  - If a presented proof already exists in the database, the parameters valid, not_spent and date_presented are updated
  - Saved parameters:
      - valid = proof['verified'] == "true", (not revoked AND expiration_date > today
      - not spent = the token has a value > 0
      - "patient_fullname",
      - "patient_birthday",
      - "doctor_fullname",
      - "doctor_address",
      - "pharmaceutical",
      - "number",
      - "prescription_id",
      - "spending_key",
      - "contract_address"
      - date_issued
      - date_presented 
  
