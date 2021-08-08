/*
 * Copyright 2019  ChainLab
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

'use strict';

const stdio = require("stdio");
const args = stdio.getopt({
    "address": {key: "address", args: 1, description: "contract address", mandatory: true},
    "secret": {key: "secret", args: 1, description: "secret key for spending the ePrescription", mandatory: true},
    "id": {key: "id", args: 1, description: "id of the prescription", mandatory: true},
});

const config = require("./config.json")
const Web3 = require("web3");
const TruffleContract = require("truffle-contract");
const provider = new Web3.providers.HttpProvider(config.node);
const web3 = new Web3(provider);

const account = config.account

const artifact = require("./build/contracts/PrescriptionContract.json");

const instance = new web3.eth.Contract(artifact.abi, artifact.networks['10'].address);

async function spendPrescription(secret, id) {
    //let patientAccount = await web3.eth.accounts.privateKeyToAccount(secret);

    let adminAccount = await web3.eth.getAccounts().catch(err => {
        //console.log(err);
    });
    //console.log("Admin account: " + adminAccount);

    //web3.eth.accounts.wallet.add(secret.toString());
    let returnValue = await instance.methods.spend(id).send({
        from: adminAccount.toString(),
        gas: 300000
    }).catch(err => {
        //console.log(err);
        //console.log("false");
        return;
        //return Promise.reject(err);
    });
    console.log(returnValue);
    try {
        console.log(returnValue.status);
    } catch (err) {
        console.log("false");
    }
    ;
    return;
}

spendPrescription(args.secret, args.id);

