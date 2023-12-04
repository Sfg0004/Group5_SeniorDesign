// SPDX-License-Identifier: UNLISCENSED
pragma solidity ^0.8.20;

//THIS IS A WORK IN PROGRESS!
//this has been initially tested in remix but is not fully ready for integration
// into the current solution. Considerations for changes for impletmentation
// or troubale shooting are mentioned in comments throughout.
// need to further refine gas cost and address addressing issues in blockchain code
// before inegration can be finalized

//OpenZeppelin AccessControl framework for hasRole, _grantRole
import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
    //consider writing some "in house" for increase security/internal vuln ID
    //removing this may remove unneeded/unviewable risks

contract AccessController is AccessControl {
    // Create role identifiers admin and user
    //admin -> able to add and removed roles/access
    //accesser -> a user, can be assigned/stripped of access
    
    bytes32 internal constant admin = keccak256(abi.encodePacked("ADMIN"));
    bytes32 public constant accesser = keccak256(abi.encodePacked("ACCESSER"));
    //made roles public for testing/debugging/tracing/etc 
    //conisdering making internal for final integration to reduce potential account targeting
    //use abi.encodePacked("X") to reduce gas cost 
    
    mapping(bytes32 => mapping(address => bool)) public verifiedAccess;
    //associates: role -> address -> bool(t/f)
    //role = key, address -> y/n = value
    //could (in theory) search by role later?
    //otherwise may break into two seperate association to reduce params passed often
   
    mapping(address => string) userHash;
    //associates: address -> ipfsHash (file hash)


//consider using indexed params (decreae storage and gas cost)
//BUT indexed params are visible on the BC so LESS SECURE!!
//investiage "msg.sender" logic instead of passing userHash for decreaed gas

    event UserAccessAdded(address userAddr, string action); 
        //emits when admin grants a user an access to ipfs
    event UserAccessRemoved(address userAddr, string action);
        //emits when admin strips user of an access to ipfs
    event RoleAssigned(bytes32 role, address userAddr);
        //emits when admin assigns user a role
    event RoleRemoved(bytes32 role, address userAddr);
        //emits when admine removes user role
    event BadAccessAttempt(address userAddr, string action);
        //emits when a bad attemts to access ipfs is made


//create modifer -> this allows quick check for functions to check for role
    modifier onlyAdmin(){
        require(hasRole(admin,msg.sender), "only admin can edit access");
        //ensure caller of function has the role of admin
        _;
    }

    constructor(address adminAddr) {
        // Grant the role to a specified account  
        //only called when first deployed      
     
        _grantRole(admin, adminAddr);
        emit RoleAssigned(admin, adminAddr);
        //send signal that the role was assigned
  
    }

    function assignRole(bytes32 role, address userAddr) onlyAdmin public{
        // checks that the calling account has the admin role
        //admin assigns user a role (aasocitate role to address and marks true)
           
            verifiedAccess[role][userAddr] = true;
            emit RoleAssigned(role, userAddr);
            //sends signal that the role was assigned
    }

//will need to implement something to prevent deleting only admin (locking contract)
    function removeRole(bytes32 role, address userAddr) onlyAdmin public{
        // checks that the calling account has the admin role
        //admin removes role from user (associate role to address and mark false)
            
            verifiedAccess[role][userAddr] = false;
            emit RoleRemoved(role, userAddr);
            //sends signal that the role was removed
    }

    function addAccess(address userAddr, string memory ipfsHash) onlyAdmin public {
        // checks that the calling account has the admin role
        //admin allows associtation of user and hash (can be used to verify access checks)
      
        userHash[userAddr] = ipfsHash;
        emit UserAccessAdded(userAddr, "added IPFS access");
        //sends signal that an access was granted to user
    }

    function deleteAccess(address userAddr) onlyAdmin public {
        // checks that the calling account has the admin role
        //admin deletes association of user with hash
       
        delete userHash[userAddr];
        emit UserAccessRemoved(userAddr, "removed IPFS access");
        //sends signal that an acces was removed from user
    }

//may need to input verify if user exists before checking?
    function checkRole(address userAddr, bytes32 role) public view returns (bytes32 Checkedrole) {
        //checks what role user has if a role is associated as true
       
        if(verifiedAccess[role][userAddr]){  //if a role is true return what it is
            return role;
        }
        else{ //if no role is associated return unknown
            return keccak256(abi.encodePacked("Unknown"));
        }
    }

/*    function checkAccess(address userAddr, bytes32 role) public view returns(bool access){
        if(verifiedAccess[role][userAddr]){
            return true;
        }
        else{
            return false;
        }
    }
*/

//may need to validate/error handle for association exisiting
    function checkIPFSHash(address userAddr) public view returns(string memory ipfsHash){
    //checks what hash string is associtated with address
    //string memory -> uses memory of the function to reduce gas and storage
    //returns the associated hash
   
        return userHash[userAddr];
    }

    function badAccessFallback() external {
    //when bad access occur in the BC, will run this, emit error message, cancel transaction
      
        emit BadAccessAttempt(msg.sender, "fallback");
        revert("bad access attempt");
        //revert will immediatly halt transaction, refund any remaining gas, undo anything
        //perfored in the current transaction
    }
}