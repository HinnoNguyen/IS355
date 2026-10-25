# @version ^0.4.3

"""
Voting DApp — bo phieu phi tap trung (BTTH3 Tren Lop).
Chairperson khoi tao de xuat, cap quyen; voter bo phieu / uy quyen.
"""

struct Voter:
    weight: uint256
    voted: bool
    delegate: address
    vote: uint256

struct Proposal:
    name: String[100]
    voteCount: uint256

voters: public(HashMap[address, Voter])
proposals: public(HashMap[uint256, Proposal])
voterCount: public(uint256)
chairperson: public(address)
amountProposals: public(uint256)

MAX_NUM_PROPOSALS: constant(uint256) = 3


@deploy
def __init__():
    self.chairperson = msg.sender


@external
def addProposal(_proposalName: String[100]):
    assert msg.sender == self.chairperson
    assert self.amountProposals < MAX_NUM_PROPOSALS
    i: uint256 = self.amountProposals
    self.proposals[i].name = _proposalName
    self.proposals[i].voteCount = 0
    self.amountProposals += 1


@external
def giveRightToVote(voter: address, _weight: uint256):
    assert msg.sender == self.chairperson
    assert not self.voters[voter].voted
    assert self.voters[voter].weight == 0
    self.voters[voter].weight = _weight
    self.voterCount += 1


@internal
def _forwardWeight(voter: address):
    """Chuyen weight theo chuoi uy quyen den nguoi chua vote (hoac cong vao proposal neu da vote)."""
    to: address = self.voters[voter].delegate
    # Theo doi chuoi delegate (toi da MAX_NUM_PROPOSALS buoc)
    for _: uint256 in range(MAX_NUM_PROPOSALS):
        next_to: address = self.voters[to].delegate
        if next_to == empty(address):
            break
        assert next_to != voter  # tranh vong lap
        to = next_to

    weight: uint256 = self.voters[voter].weight
    self.voters[voter].weight = 0

    if self.voters[to].voted:
        self.proposals[self.voters[to].vote].voteCount += weight
    else:
        self.voters[to].weight += weight


@external
def delegate(to: address):
    assert not self.voters[msg.sender].voted
    assert to != msg.sender
    assert to != empty(address)

    self.voters[msg.sender].voted = True
    self.voters[msg.sender].delegate = to

    self._forwardWeight(msg.sender)


@external
def vote(proposal: uint256):
    assert not self.voters[msg.sender].voted
    assert proposal < self.amountProposals

    self.voters[msg.sender].vote = proposal
    self.voters[msg.sender].voted = True

    self.proposals[proposal].voteCount += self.voters[msg.sender].weight
    self.voters[msg.sender].weight = 0


@view
@internal
def _winningProposal() -> uint256:
    winning_vote_count: uint256 = 0
    winning_proposal: uint256 = 0
    for i: uint256 in range(MAX_NUM_PROPOSALS):
        if self.proposals[i].voteCount > winning_vote_count:
            winning_vote_count = self.proposals[i].voteCount
            winning_proposal = i
    return winning_proposal


@view
@external
def winningProposal() -> uint256:
    return self._winningProposal()


@view
@external
def winnerName() -> String[100]:
    return self.proposals[self._winningProposal()].name
