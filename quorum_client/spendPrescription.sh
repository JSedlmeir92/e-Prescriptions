#!/bin/bash

res=$(node spendPrescription.js --address "$1$" --id "$2" --secret "$3")
echo "$res"
