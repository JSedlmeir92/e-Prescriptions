#!/bin/bash

ip_address="$(cat ip_address_vm)"
# echo "$ip_address"

# Starting AGENT 1 - Doctor
PORTS="7000:7000 7080:7080" aries-cloudagent/scripts/run_docker start --auto-respond-credential-proposal --auto-respond-credential-offer --auto-respond-credential-request  --inbound-transport http 0.0.0.0 7000 --inbound-transport ws 0.0.0.0 7001 --outbound-transport ws --outbound-transport http --genesis-file /var/lib/indy/my-net/pool_transactions_genesis --log-level info --wallet-type indy --seed 000000000000000000000000Steward3 --wallet-key doctor --wallet-name StewardWallet3 --admin-insecure-mode --admin 0.0.0.0 7080 -e http://$ip_address:7000/ -l Doctor
