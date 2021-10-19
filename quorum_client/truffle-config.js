module.exports = {
  networks: {
    node0: {
      host: "172.16.239.11",
      port: 8545,
      network_id: "*",
      gasPrice: 0,
      gas: 300000000,
      type: "quorum"
    }
  }
};

