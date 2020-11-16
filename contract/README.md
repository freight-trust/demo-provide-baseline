# README

ChannelNode is a contract designed to transfer messages using the ethereum contracts events system.
Before the communication two or more channels must undergo "pairing" procedure. There are several properties each abstract contract owner possess:
```
Owner:
  participant_name: str - two letters country code, for example "SG", "AU"
  address: str, public key of an ethereum wallet that performs deployment
```
These properties must be exchanged between the owners to form the channel. There is no lookup mechanism integrated into ChannelNode contract,and only a contract owner can add a participant to his channel.

**Pairing:**

1. owner ``A`` **deploys** ```ChannelNode(A.participant_name)``` contract as ``ChannelNodeA``
1. owner ``B`` **deploys** ```ChannelNode(B.participant_name)``` contract as ``ChannelNodeB``
1. owner ``A`` **calls** ```ChannelNodeA.addParticipant(B.participant_name, B.address)```
1. owner ``B`` **calls** ```ChannelNodeB.addParticipant(A.participant_name, B.address)```
1. owner ``B`` **calls** ```ChannelNodeA.updateParticipantContractAddress(B.participant_name, ChannelNodeB.address)```
1. owner ``A`` **calls** ```ChannelNodeB.updateParticipantContractAddress(A.participant_name, ChannelNodeA.address)```

After the ChannelNode contracts are paired they can start communicating

**Communication**:

```
Message:
    sender: str
    sender_ref: str
    receiver: str
    subject: str
    object: str
    predicate: str
```
1. owner ``A`` **calls** ```ChannelNodeA.send(Message)``` where ```Message.receiver``` is ```B.participant_name```
1. ``ChannelNodeA`` **calls** ```ChannelNodeB.receiveMessage(Message)```
1. ``ChannelNodeB`` **emits** ```MessageReceivedEvent(Message)```
1. ``ChannelNodeA`` **emits** ```MessageSentEvent(Message)```
