// SPDX-License-Identifies: UNLICENSED
pragma solidity ^0.8.20;

//intial ideas behind basic user list checks

contract userAuth1{
    address public userAddress;
    mapping(address => bool) public isUser; 
    //should associtate address => bool

    event UserAdded(address indexed account);
        //emits when a user is added
    event UserRemoved(address indexed account);
        //emits when a user is removed
    //event OwnershipTransferred(address previousOwner, address newOwner);


 /*   modifier verifiedUser() {
        require(msg.sender == verified_user, "Only verified users can call this function");
        _;
    }*/


    constructor() public {
        userAddress = msg.sender;   //user is caller of contract
        isUser[msg.sender] = true;  //add user to a list of users
        emit UserAdded(msg.sender); //send to indicate user added
    }


    function addUser(address account) public {
    //add a user to the list of users
        require(!isUser[account], "Account is already a user"); //require that user not already added to list
        isUser[account] = true;                                 //add user to list
        emit UserAdded(account);                                //send to indicate user added
    }

    function removeUser(address account) public {
    //remove a user from the list of users
        require(isUser[account], "Account is not a user");  //require the user be on the list of users
        isUser[account] = false;                            //remove user association (could use delete instead?)
        emit UserRemoved(account);                          //send to indicate user removed
    }

    function checkRole(address account) view public returns (string memory) {
    //check if a user is in the list
        if (isUser[account]) {  //if user is in list and true return title "User"
            return "User";
        } 
        else {                  //if not in list/true return title "Unknown"
            return "Unknown";
        }
    }

    /*function transferOwner(address newAdmin) external onlyAdmin {
        require(newAdmin != userAdress(0), "Invalid new owner address");
        require(newAdmin != admin, "New admin is the current admin");
        isAdmin[admin] = false;
        isAdmin[newAdmin] = true;
        emit RoleRevoked(admin, "Admin");
        emit RoleAssigned(newAdmin, "Admin");
        emit OwnershipTransferred(admin, newAdmin);
        admin = newAdmin;
    }*/
}
