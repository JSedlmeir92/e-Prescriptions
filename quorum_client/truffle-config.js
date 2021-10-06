const HDWalletProvider = require("@truffle/hdwallet-provider");
require('dotenv').config()


module.exports = {
  networks: {
    development: {
      host: process.env.ip_address,
      port: 8545,
      network_id: "*"
    },
    quorum: {
       host: "172.16.239.11",
       port: 8545,
       network_id: "*",
       gasPrice: 0,
       gas: 300000000,
       type: "quorum"
    },
    rinkeby: {
      provider: function() {
        return new HDWalletProvider('eternal meadow wall mesh glad person outer salmon agree fish fiscal express', "https://rinkeby.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161");
      },
      network_id: 4,
      gas: 4500000,
      gasPrice: 10000000000,
    }
  }
};

