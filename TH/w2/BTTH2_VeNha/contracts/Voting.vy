# @version ^0.4.3

"""Bo phieu phi tap trung: moi account 1 phieu, getWinner()."""

MAX_CANDIDATES: constant(uint256) = 16

owner: public(address)
candidate_count: public(uint256)
names: HashMap[uint256, String[64]]
votes: HashMap[uint256, uint256]
has_voted: HashMap[address, bool]

@deploy
def __init__():
    self.owner = msg.sender

@external
def addCandidate(name: String[64]):
    assert msg.sender == self.owner, "only owner"
    assert self.candidate_count < MAX_CANDIDATES, "full"
    assert len(name) > 0, "empty name"
    idx: uint256 = self.candidate_count
    self.names[idx] = name
    self.votes[idx] = 0
    self.candidate_count = idx + 1

@external
def vote(candidate_id: uint256):
    assert not self.has_voted[msg.sender], "already voted"
    assert candidate_id < self.candidate_count, "bad id"
    self.has_voted[msg.sender] = True
    self.votes[candidate_id] += 1

@external
@view
def getVotes(candidate_id: uint256) -> uint256:
    assert candidate_id < self.candidate_count, "bad id"
    return self.votes[candidate_id]

@external
@view
def getWinner() -> (uint256, String[64], uint256):
    """Tra ve (id, ten, so phieu) ung vien nhieu phieu nhat."""
    assert self.candidate_count > 0, "no candidates"
    best_id: uint256 = 0
    best_votes: uint256 = self.votes[0]
    i: uint256 = 1
    for _: uint256 in range(MAX_CANDIDATES):
        if i >= self.candidate_count:
            break
        if self.votes[i] > best_votes:
            best_votes = self.votes[i]
            best_id = i
        i += 1
    return best_id, self.names[best_id], best_votes
