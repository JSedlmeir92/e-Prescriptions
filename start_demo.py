import asyncio
import os
import sys
import time
from dotenv import load_dotenv

print("If you are executing this demo inside a virtual machine, make sure the following ports are open:\n7000 and 7080\n8000\n9000 and 9080\n")

load_dotenv()


# Getting the VM's IP ADDRESS
FileHandler = open("ip_address_vm", "a+")

print(os.environ)
print(os.environ['ip_address'])


if os.stat("ip_address_vm").st_size != 0:
    FileHandler = open("ip_address_vm", "r")
    ip_address = FileHandler.read()
    print("file", os.stat("ip_address_vm").st_size, ip_address)
elif os.environ['ip_address']:
    ip_address = os.getenv('ip_address')
    FileHandler.write(ip_address)
    print("env", ip_address)
else:
    ip_address = input("\nPlease enter your VM's IP address: ")
    FileHandler.write(ip_address)
    print("type", ip_address)

print("Your VM's current IP address is set to:", ip_address)
print("Please change the IP address if necessary.\n")
FileHandler.close()

print(os.environ['ip_address'])
os.environ['IP_ADDRESS'] = ip_address
# Getting the Quorum node's IP ADDRESS
# FileHandler = open("ip_address_quorum_node", "a+")
# if os.stat("ip_address_quorum_node").st_size == 0:
#     ip_address = input("\nPlease enter your quorum node's IP address: ")
#     FileHandler.write(ip_address)
# else:
#     FileHandler = open("ip_address_quorum_node", "r")
#     print("Your quorum node's current IP address is set to:", FileHandler.read())
#     print("Please change the IP address if necessary.\n")
# FileHandler.close()

os.system("rm db.sqlite3")

#Resetting and starting Docker images
os.system("docker-compose rm")
os.system("docker-compose up -d")



print("\nDeploying the ePrescription contract...") ##
os.system("cd quorum_client && npm install && truffle migrate --reset --network node0")

##Django
os.system("python3 manage.py makemigrations") 
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
#cns.views.create_schema()
#doctor.views.create_schema()
#pharmacy.views.create_schema()

#TODO: Create cred defs
#cns.views.create_cred_def()
#doctor.views.create_cred_def()
#pharmacy.views.create_cred_def()
