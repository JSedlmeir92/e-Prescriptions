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
const config = require("./config.json")
const Web3 = require("web3");
const TruffleContract = require("truffle-contract");
const provider = new Web3.providers.HttpProvider(config.node);
const web3 = new Web3(provider);

const account = config.account

const artifact = require("./build/contracts/PrescriptionContract.json");

var prescriptionPrivateKey;

/**
 * module description
 * @module Bench
 */
class ePrescription {

    /**
     * Always launch after instantiating
     */
    async init () {
        const instance = new web3.eth.Contract(artifact.abi, artifact.networks['10'].address);
        this.instance = instance;
        return Promise.resolve(true);
    }

    /**
     * Always launch after completion
     */
    async close(){}


    async createPrescription()  {
	    let adminAccount = await web3.eth.getAccounts().catch(err => {
            console.log(err);
        });
        console.log("Admin account: " + adminAccount);

        let patientAccount = await web3.eth.accounts.create("Hallo");
        this.prescriptionPrivateKey = patientAccount.privateKey;
        console.log("Patient Account: " + patientAccount.address);
	console.log("Patient Account private key: " + patientAccount.privateKey);
	//console.log(this.instance);
        console.log(typeof(patientAccount.address));
        console.log(typeof(adminAccount));
	let returnValue = await this.instance.methods.create(patientAccount.address, "Receipt1").send({
            from: adminAccount.toString(),
            gas: 300000
        }).catch(err => {return Promise.reject(err)});
	console.log(returnValue);
        return Promise.resolve(1);
    };


    async spendPrescription() {
        let patientAccount = await web3.eth.accounts.privateKeyToAccount(this.prescriptionPrivateKey);
	web3.eth.accounts.wallet.add(this.prescriptionPrivateKey.toString());
        let returnValue = await this.instance.methods.spend("Receipt1").send({
            from: patientAccount.address.toString(),
            gas: 300000000
        }).catch(err => {return Promise.reject(err)});
        console.log(returnValue);
        return Promise.resolve(1);

    }

    async getBlockNumber()  {
        let blockNumber = await web3.eth.getBlockNumber().catch(err => {
            console.log(err);
            return Promise.reject(-1);
        });
        console.log("Block number: " + blockNumber);
        return Promise.resolve(1)
    };

    /**
     * getter and setter for tmp
     */

    async getTmpPublic() {
        let returnValue = await this.instance2.methods.getTmp().send({
            from: account,
            gas: 300000000
        }).catch(err => {return Promise.reject(err)});
        return Promise.resolve(returnValue)
    }

    async getTmpPrivate() {
        let returnValue = await this.instance.methods.getTmp().send({
            from: account,
            privateFor: privateFor,
            gas: 300000000
        }).catch(err => {return Promise.reject(err)});
	        return Promise.resolve(returnValue)
    }

    async setTmpPublic(value) {
        let returnValue = await this.instance2.methods.setTmp(value).send({
            from: account,
            gas: 300000000
        }).catch(err => {return Promise.reject(err)});
        return Promise.resolve(returnValue.blockNumber)
    }

    async setTmpPrivate(value) {
        let returnValue = await this.instance.methods.setTmp(value).send({
            from: account,
            privateFor: privateFor,
            gas: 300000000
        }).catch(err => {return Promise.reject(err)});
        return Promise.resolve(returnValue.blockNumber)
    }

    /**
     * Matrix Multiplication
     * @param value
     * @param account
     * @param array of public keys for private transactions
     */

    async queryMatrixMultiplicationPublic(value) {
        let returnValue = await this.instance2.methods.queryMatrixMultiplication(value).call({
            from: account,
            gas: 300000000
        }).catch(err => {return Promise.reject(err)});
        return Promise.resolve(returnValue);
    };

    async queryMatrixMultiplicationPrivate(value) {
        let returnValue = await this.instance.methods.queryMatrixMultiplication(value).call({
            from: account,
            privateFor: privateFor,
            gas: 300000000
        }).catch(err => {return Promise.reject(err)});
        return Promise.resolve(returnValue);
    };

    async invokeMatrixMultiplicationPublic(value) {
        let returnValue = await this.instance2.methods.invokeMatrixMultiplication(value).send({
            from: account,
            gas: 300000000
        }).catch(err => {return Promise.reject(err)});
        return Promise.resolve(returnValue.blockNumber);
    };

    async invokeMatrixMultiplicationPrivate(value) {
        let returnValue = await this.instance.methods.invokeMatrixMultiplication(value).send({
            from: account,
            privateFor: privateFor,
            gas: 300000000
        }).catch(err => {return Promise.reject(err)});
        return Promise.resolve(returnValue.blockNumber);
    };

    async setMatrixMultiplicationPublic(value) {
        let returnValue = await this.instance2.methods.setMatrixMultiplication(value).send({
            from: account,
            gas: 300000000
        }).catch(err => {return Promise.reject(err)});
        return Promise.resolve(returnValue.blockNumber);
    };

    async setMatrixMultiplicationPrivate(value) {
        let returnValue = await this.instance.methods.setMatrixMultiplication(value).send({
            from: account,
            privateFor: privateFor,
            gas: 300000000
        }).catch(err => {return Promise.reject(err)});
        return Promise.resolve(returnValue.blockNumber);
    };


     /**
     * Doing Nothing
     * @param account
     * @param array of public keys for private transactions
     */

     async queryDoNothingPublic() {
        let returnValue = await this.instance2.methods.queryDoNothing().call({
            from: account,
            gas: 300000000
        }).catch(err => {return Promise.reject(err)});
        return Promise.resolve(returnValue);
    }

    async queryDoNothingPrivate(){
        let returnValue = await this.instance.methods.queryDoNothing().call({
            from: account,
            privateFor: privateFor,
            gas: 300000000
        }).catch(err => {return Promise.reject(err)});
        return Promise.resolve(returnValue.blockNumber)
    }

    async invokeDoNothingPublic() {
        let returnValue = await this.instance2.methods.invokeDoNothing().send({
            from: account,
            gas: 300000000
        }).catch(err => {
            console.log(err);
            return Promise.reject(err)});
        return Promise.resolve(returnValue.blockNumber);
    }

    async invokeDoNothingPrivate(){
        let returnValue = await this.instance.methods.invokeDoNothing().send({
            from: account,
            privateFor: privateFor,
            gas: 300000000
        }).catch(err => {return Promise.reject(err)});
        return Promise.resolve(returnValue.blockNumber)
    }

    /**
     * writing data
     * @param key
     * @param value
     * @param account
     * @param array of public keys for private transactions
     */

    async writeDataPublic(key, value) {
        let returnValue = await this.instance2.methods.writeData(key, value).send({
            from: account,
            gas: 300000000
        }).catch(err => {return Promise.reject(err)});
        return Promise.resolve(returnValue.blockNumber);
    }

    async writeDataPrivate(key, value) {
        let returnValue = await this.instance.methods.writeData(key, value).send({
            from: account,
            privateFor: privateFor,
            gas: 300000000
        }).catch(err => {return Promise.reject(err)});
        return Promise.resolve(returnValue.blockNumber);
    }

     /**
     * reading data
     * @param key
     * @param account
     * @param array of public keys for private transactions
     */

     async readDataPublic(key) {
        let returnValue = await this.instance2.methods.readData(key).call({
            from: account,
            gas: 300000000
        }).catch(err => {return Promise.reject(err)});
        return Promise.resolve(returnValue);
     }

    async readDataPrivate(key) {
        let returnValue = await this.instance.methods.readData(key).call({
            from: account,
            privateFor: privateFor,
            gas: 300000000
        }).catch(err => {return Promise.reject(err)});
        return Promise.resolve(returnValue);
    }

     /**
     * writingMuchData
     * @params start, end
     * @param account
     * @param array of public keys for private transactions
     */

     async writeMuchDataPublic(len, start, delta) {
         let returnValue = await this.instance2.methods.writeMuchData(parseInt(len, 10), parseInt(start, 10), parseInt(delta, 10)).send({
             from: account,
             gas: 300000000
         }).catch(err => {return Promise.reject(err)});
         return Promise.resolve(returnValue.blockNumber)
     }

     async writeMuchDataPrivate(len, start, delta) {
         let returnValue = await this.instance.methods.writeMuchData(parseInt(len, 10), parseInt(start, 10), parseInt(delta, 10)).send({
             from: account,
             privateFor: privateFor,
            gas: 300000000
         }).catch(err => {return Promise.reject(err)});
         return Promise.resolve(returnValue)
     }

     async writeMuchDataPublic2(len, start, delta) {
         let returnValue = await this.instance2.methods.writeMuchData2(parseInt(len, 10), parseInt(start, 10), parseInt(delta, 10)).send({
             from: account,
             gas: 300000000
         }).catch(err => {return Promise.reject(err)});
         return Promise.resolve(returnValue.blockNumber)
     }

     async writeMuchDataPrivate2(len, start, delta) {
         let returnValue = await this.instance.methods.writeMuchData2(parseInt(len, 10), parseInt(start, 10), parseInt(delta, 10)).send({
             from: account,
             privateFor: privateFor,
            gas: 300000000
         }).catch(err => {return Promise.reject(err)});
         return Promise.resolve(returnValue)
     }

     /**
     * readingMuchData
     * @params start, end
     * @param account
     * @param array of public keys for private transactions
     */

     async readMuchDataPublic(len, start) {
         let returnValue = await this.instance2.methods.readMuchData(len, start).call({
             from: account,
            gas: 300000000
         }).catch(err => {return Promise.reject(err)});
         return Promise.resolve(returnValue)
     }

     async readMuchDataPrivate(len, start) {
         let returnValue = await this.instance.methods.readMuchData(len, start).call({
             from: account,
             privateFor: privateFor,
             gas: 300000000
         }).catch(err => {return Promise.reject(err)});
         return Promise.resolve(returnValue)
     }

     async readMuchDataPublic2(len, start) {
         let returnValue = await this.instance2.methods.readMuchData2(len, start).call({
             from: account,
             gas: 300000000
         }).catch(err => {return Promise.reject(err)});
         return Promise.resolve(returnValue)
     }

     async readMuchDataPrivate2(len, start) {
         let returnValue = await this.instance.methods.readMuchData2(len, start).call({
             from: account,
             privateFor: privateFor,
             gas: 300000000
         }).catch(err => {return Promise.reject(err)});
         return Promise.resolve(returnValue)
     }

     async depositZether() {
         let result = await this.alice.deposit(10).catch(err => {
             console.log(err);
             return Promise.reject(-1);
         });
         console.log(result)
         return Promise.resolve(1)
     }

     async sendZether() {
         let result = await this.alice.transfer('Bob', 50).catch(err => {
             console.log(err);
             return Promise.reject(-1);
         });
         console.log(result);
         return Promise.resolve(1);
    }

    async withdrawZether() {
        let result = await this.alice.withdraw(10).catch(err => {
            console.log(err);
            return Promise.reject(-1);
        });
        console.log(result);
        return Promise.resolve(1);
    }

}

module.exports = ePrescription;
