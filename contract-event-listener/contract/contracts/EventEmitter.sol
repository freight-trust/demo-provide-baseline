// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.8.0;

contract EventEmitter {

  event MessageSent(string receiver, string text);
  event MessageReceived(string receiver, string text);

  function stringEqual(string memory s1, string memory s2) public pure returns(bool){
      return keccak256(abi.encodePacked(s1)) == keccak256(abi.encodePacked(s2));
  }

  function emitEvent(string memory name, string memory receiver, string memory text) public {
    if(stringEqual(name, "MessageSent")){
      emit MessageSent(receiver, text);
    }else if(stringEqual(name, "MessageReceived")){
      emit MessageReceived(receiver, text);
    }
  }
}
