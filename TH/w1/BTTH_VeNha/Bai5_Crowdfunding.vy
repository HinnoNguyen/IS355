# @version ^0.4.0

"""Bài 5: Crowdfunding - mục tiêu 5 ETH, deadline 10 phút."""

owner: public(address)
goal: public(uint256)
deadline: public(uint256)
totalRaised: public(uint256)
contributions: public(HashMap[address, uint256])
ownerWithdrawn: public(bool)

@deploy
def __init__():
    self.owner = msg.sender
    self.goal = 5 * 10**18  # 5 ETH
    self.deadline = block.timestamp + 10 * 60  # 10 phút

@external
@payable
def contribute():
    """Người dùng quyên góp ETH."""
    assert block.timestamp < self.deadline, "campaign ended"
    assert msg.value > 0, "must send ETH"
    self.contributions[msg.sender] += msg.value
    self.totalRaised += msg.value

@external
def withdraw():
    """
    - Đạt mục tiêu: chủ dự án rút toàn bộ quỹ.
    - Không đạt và đã hết hạn: người đóng góp rút lại phần của mình.
    """
    if self.totalRaised >= self.goal:
        assert msg.sender == self.owner, "only owner"
        assert not self.ownerWithdrawn, "already withdrawn"
        self.ownerWithdrawn = True
        amount: uint256 = self.balance
        raw_call(self.owner, b"", value=amount)
    else:
        assert block.timestamp >= self.deadline, "still ongoing"
        amount: uint256 = self.contributions[msg.sender]
        assert amount > 0, "nothing to refund"
        self.contributions[msg.sender] = 0
        raw_call(msg.sender, b"", value=amount)
