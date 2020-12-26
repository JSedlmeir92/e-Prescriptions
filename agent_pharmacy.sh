#!/bin/bash

ip_address="$(cat ip_address_vm)"
# echo "$ip_address"

# Starting AGENT 2 - Pharmacy
PORTS="9000:9000 9080:9080" aries-cloudagent/scripts/run_docker start --inbound-transport http 0.0.0.0 9000 --inbound-transport ws 0.0.0.0 9001 --outbound-transport ws --outbound-transport http --genesis-file /var/lib/indy/my-net/pool_transactions_genesis --log-level info --wallet-type indy --seed 000000000000000000000000000Agent --wallet-key welldone --wallet-name AgentWallet2 --admin-insecure-mode --admin 0.0.0.0 9080 -e http://$ip_address:9000/ --webhook http://$ip_address:8000/pharmacy -l Pharmacy --auto-verify-presentation
