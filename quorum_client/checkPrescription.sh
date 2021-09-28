#!/bin/bash

res=$(node quorum_client/checkPrescription.js --address "$1" --id "$2" --secret "$3")
# res="true"
echo "$res" > quorum_client/check
echo "$res"
