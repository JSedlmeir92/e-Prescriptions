#!/bin/bash

res=$(node quorum_client/spendPrescription.js --address "$1" --id "$2" --secret "$3")
echo "$res" > quorum_client/result
