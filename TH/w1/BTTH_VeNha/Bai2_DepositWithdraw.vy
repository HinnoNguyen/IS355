# @version ^0.4.0

"""Bài 2: Gửi/rút ETH, quản lý số dư theo địa chỉ."""

balances: public(HashMap[address, uint256])

@external
@payable
def deposit():
    """Người dùng gửi ETH vào hợp đồng."""
    assert msg.value > 0, "must send ETH"
    self.balances[msg.sender] += msg.value

@external
@view
def get_balance(addr: address) -> uint256:
    """Kiểm tra số dư của một địa chỉ (balances)."""
    return self.balances[addr]

@external
def withdraw():
    """Rút toàn bộ số dư của người gọi."""
    amount: uint256 = self.balances[msg.sender]
    assert amount > 0, "no balance"
    self.balances[msg.sender] = 0
    raw_call(msg.sender, b"", value=amount)
