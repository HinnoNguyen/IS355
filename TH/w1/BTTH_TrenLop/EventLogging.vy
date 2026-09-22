# @version ^0.4.3

event Donation:
    donatur: indexed(address)
    amount: uint256

@external
@payable
def donate():
    log Donation(msg.sender, msg.value)
