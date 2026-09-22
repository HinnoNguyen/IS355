# @version ^0.4.3

number: uint256

@external
def store(num: uint256):
    self.number = num

@external
def retrieve() -> uint256:
    return self.number
