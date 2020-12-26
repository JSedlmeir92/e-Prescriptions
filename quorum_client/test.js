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

const ePrescription = require("./wrapper.js")
const prescription = new ePrescription();

async function test(){

    let start;
    let nr;
    let result;

    console.log("");
    console.log("===Starting the test===");
    console.log("");

    //initializing the contracts
    await prescription.init().catch(err => {console.log(err)});

    start = Date.now();
    result = await prescription.createPrescription();
    nr = await prescription.getBlockNumber();
    console.log("createPrescription:" + result);
    console.log("elapsed time: " + (Date.now()-start));
    console.log("");
    console.log("=======================");
    console.log("");

    start = Date.now()
    result = await prescription.spendPrescription();
    nr = await prescription.getBlockNumber();
    console.log("spendPrescription:" + result);
    console.log("elapsed time: " + (Date.now()-start));
    console.log("");
    console.log("=======================");
    console.log("");


}

test()
