#!/bin/bash

rm -rf ~/.indy_client
rm db.sqlite3
# TODO: new github account for revocations
cd TailsFiles && git rm * && git commit -m "Upload via demo" && git push https://prescriptionMaster:ZYN586xGacRvabUIhvt9@github.com/prescriptionMaster/TailsFiles.git --all
