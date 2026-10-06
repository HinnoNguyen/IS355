# @version ^0.4.3

"""Sổ nợ cá nhân: owner ghi nợ cho từng địa chỉ."""

owner: public(address)
debts: HashMap[address, uint256]

@deploy
def __init__():
    self.owner = msg.sender

@external
def addDebt(debtor: address, amount: uint256):
    """Chi owner duoc them no."""
    assert msg.sender == self.owner, "only owner"
    assert debtor != empty(address), "bad debtor"
    self.debts[debtor] += amount

@external
@view
def getDebt(debtor: address) -> uint256:
    return self.debts[debtor]
