// SPDX-License-Identifies: UNLICENSED
pragma solidity ^0.8.20;

//modified from userAuth1.sol to attempt to work without addresses
//WIP 

contract userAuth2{
    uint public userAddress;    //attempt uint ID instead of address
    mapping(uint => bool) public isUser; 
    //associate uint => bool

    event UserAdded(uint);
        //emit when user is added to list

    modifier verifiedUser() {
        //create modifier that only a veridied user can do something

        require(msg.sender == verified_user, "Only verified users can call this function");
        //check that the caller is a user
        _;  //required for modifier
    }

    constructor() public {
        userAddress = msg.sender;   //user is the caller
        isUser[msg.sender] = true;  //add the caller to user list
        verified_user == true;
        emit UserAdded(msg.sender); //send to indicate user added to list
    }

    function addUser(uint account) public verifiedUser {
    //verified user adds new user to list
      
        require(!isUser[account], "Account is already a user"); //check if user already in list
        isUser[account] = true;                                 //add user to list
        emit UserAdded(account);                                //send to indicate user added to list
    }

    function removeUser(uint account) verifiedUser public {
    //verified user removes user from list
      
        require(isUser[account], "Account is not a user");  //user must be in list
        isUser[account] = false;                            //remove user from true value in list (may also use delete)
        emit UserRemoved(account);                          //send to indicate user was removed
    }

//may need to implement data validation
    function checkRole(uint account) view public returns (string memory) {
    //can be called to check role of a user
   
        if (isUser[account]) {  //if user is in list return title "User"
            return "User";
        } 
        else {                 //if user is not in list return title "Unknown"
            return "Unknown";
        }
    }
}