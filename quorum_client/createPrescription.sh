#!/bin/bash

res=$(node quorum_client/createPrescription.js --id "$1")

echo "$res" > quorum_client/spendingKey
echo "Spending key: $res"
