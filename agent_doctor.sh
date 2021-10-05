#!/bin/bash

ip_address="localhost"
# echo "$ip_address"

# Starting AGENT 1 - Doctor
PORTS="7000:7000 7080:7080" ./run_docker_doctor start --tails-server-base-url http://$ip_address:6543 --auto-respond-credential-proposal --auto-respond-credential-offer --auto-respond-credential-request --auto-verify-presentation --inbound-transport http 0.0.0.0 7000 --inbound-transport ws 0.0.0.0 7001 --outbound-transport ws --outbound-transport http --genesis-file /var/lib/indy/my-net/pool_transactions_genesis --log-level debug --wallet-type indy --wallet-key StewardWallet3 --wallet-name StewardWallet3 --admin-insecure-mode --admin 0.0.0.0 7080 -e http://$ip_address:7000/ -l Doctor
