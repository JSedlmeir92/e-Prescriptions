/*
 * Copyright 2020  ChainLab
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
//console.log(artifact.networks['10'].address);

async function createPrescription(id) {

	let adminAccount = await web3.eth.getAccounts().catch(err => {
		console.log(err);
	});
	//console.log("Admin account: " + adminAccount);

	let patientAccount = await web3.eth.accounts.create("Hallo");
	let prescriptionPrivateKey = patientAccount.privateKey;
	//console.log("Patient Account: " + patientAccount.address);
	//console.log("Patient Account private key: " + patientAccount.privateKey);
	//console.log(typeof(patientAccount.address));
	//console.log(typeof(adminAccount));
	let returnValue = await instance.methods.create(patientAccount.address, id).send({
		from: adminAccount[0].toString(),
		gas: 300000
	}).catch(err => {return Promise.reject(err)});
	//console.log(returnValue);
        console.log(prescriptionPrivateKey);
	return;
};


createPrescription(args.id);
