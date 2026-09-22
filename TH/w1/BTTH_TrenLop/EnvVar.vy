# @version ^0.4.3

donatur: address
donation: uint256
time: uint256

@external
@payable
def donate():
    self.donatur = msg.sender
    self.donation = msg.value
    self.time = block.timestamp
