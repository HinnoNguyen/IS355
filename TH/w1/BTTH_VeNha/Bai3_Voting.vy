# @version ^0.4.0

"""Bài 3: Bỏ phiếu đơn giản - ứng viên Tý, Tèo, Mai."""

candidates: DynArray[String[32], 3]
votes: HashMap[String[32], uint256]
has_voted: HashMap[address, bool]

@deploy
def __init__():
    self.candidates.append("Ty")
    self.candidates.append("Teo")
    self.candidates.append("Mai")

@internal
@view
def _is_candidate(name: String[32]) -> bool:
    for c: String[32] in self.candidates:
        if c == name:
            return True
    return False

@external
def vote(name_candidate: String[32]):
    """Mỗi địa chỉ chỉ được bỏ phiếu một lần."""
    assert not self.has_voted[msg.sender], "already voted"
    assert self._is_candidate(name_candidate), "invalid candidate"
    self.has_voted[msg.sender] = True
    self.votes[name_candidate] += 1

@external
@view
def getWinner() -> String[32]:
    """Trả về ứng viên có số phiếu cao nhất."""
    best_name: String[32] = self.candidates[0]
    best_votes: uint256 = self.votes[best_name]
    for c: String[32] in self.candidates:
        if self.votes[c] > best_votes:
            best_votes = self.votes[c]
            best_name = c
    return best_name

@external
@view
def getVotes(name_candidate: String[32]) -> uint256:
    return self.votes[name_candidate]
