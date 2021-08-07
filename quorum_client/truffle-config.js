module.exports = {
  networks: {
    node0: {
      host: "localhost",
      port: 22000,
      network_id: "*",
      gasPrice: 0,
      gas: 300000000,
      type: "quorum"
    }
  }
};

