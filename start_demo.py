import asyncio
import os
import sys
import time
from dotenv import load_dotenv
import subprocess


print("If you are executing this demo inside a virtual machine, make sure the following ports are open:\n7000 and 7080\n8000\n9000 and 9080\n")

load_dotenv()
# Getting the VM's IP ADDRESS
print(os.environ['ip_address'])


if os.environ['ip_address']:
    ip_address = os.getenv('ip_address')
    print("env", ip_address)
else:
    print("IP Adress is missing") 
    sys.exit('Exiting')

print("Your VM's current IP address is set to:", ip_address)
print("Please change the IP address if necessary.\n")

#os.system("rm db.sqlite3")

#Resetting and starting Docker images
#os.system("docker-compose rm")
#os.system("docker-compose up -d")

##Deploying Smart-Contract
print("\nWaiting for quorum...")
subprocess.call("./scripts/wait-for-it.sh -h 172.16.239.11 -p 8545 -t 0", shell=True)
print("\nDeploying the ePrescription contract...") ##
os.system("cd quorum_client && npm install && truffle migrate --reset --network node0")

##Django
os.system("python3 manage.py makemigrations --noinput") 
os.system("python3 manage.py migrate") ##

print("\nStarting the Server...")
os.system("python3 manage.py runserver 0.0.0.0:8000")

#print("\nStarting Dockr-Server....")
#os.system()

#print("Starting Agents...")
#os.system("gnome-terminal --geometry=52x54+960+0 --title=Doctor-Agent -- bash agent_doctor.sh") 
#os.system("gnome-terminal --geometry=52x54+1440+0 --title=Pharmacy-Agent -- bash agent_pharmacy.sh")

print("Starting complete")

# todo: stop agents & server, delete wallets
#async def main():
#    exit_demo = input("\nTo exit the demo, please type 'x' or 'X': ")
#    if ((exit_demo == "x") or (exit_demo == "X")):
#        print("\nShutting down...")
#        sys.exit()
#    else:
#        print("\nIncorrect input. Please try again.\n")
#        await main()
#
#loop = asyncio.get_event_loop()
#loop.run_until_complete(main())

# Creating schemas TODO: 
#insurance.views.create_schema()
#doctor.views.create_schema()
#pharmacy.views.create_schema()

#TODO: Create cred defs
#insurance.views.create_cred_def()
#doctor.views.create_cred_def()
#pharmacy.views.create_cred_def()
