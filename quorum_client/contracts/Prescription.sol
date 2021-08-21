// You could make it iterable by changing the second mapping to an array. But handling arrays is a little more complicated than the way with the second mapping, where unique identifiers are given anyway
// Changed the mapping, so that the owner of the precriptions public key maps to all of his precriptions
//
pragma solidity ^0.5.16;

contract PrescriptionContract {
    address admin;
    
    struct Prescription {
        address issuer; //a public key 
        string id; //the hash or serial number of an off-chain prescription VC, referenced also in the prescription VC
        uint value; //0 = 0 times spendable
    }
    
    constructor() public {
        admin = msg.sender;
    }
    
        //createdBy: bytes32, //the doctor's public key (could be stored on indy as well)
    mapping (address => mapping (string => Prescription)) public prescriptions;
        //event Create(address indexed owner, bytes32 indexed id);
        //event Spend(address indexed from);
    modifier onlyAdmin() {
        require (msg.sender == admin, "Not admin");
        _;
    }
    
    function create(address _to, string memory _id) public onlyAdmin() {
        prescriptions[_to][_id] = Prescription({issuer: msg.sender, id: _id, value: 1});
        //emit Create(owner, id);
    }
    
    function spend(string memory _id) public {
        require (prescriptions[msg.sender][_id].value == 1, "Receipt already spent");
        prescriptions[msg.sender][_id].value--;
        //emit Spend(id);
    }
}
