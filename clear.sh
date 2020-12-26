#!/bin/bash

rm -rf ~/.indy_client
rm db.sqlite3
# TODO: new github account for revocations
cd git-test && git rm * && git commit -m "Upload via demo" && git push https://Jana-Gl:ycRMtJtmmEZNDs3@github.com/Jana-Gl/git-test.git --all
