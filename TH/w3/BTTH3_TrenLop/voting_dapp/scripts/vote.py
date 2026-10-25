"""Bo phieu bang tai khoan voter (khong phai chairperson).

Chay:
  ape run vote --network ethereum:local:http://127.0.0.1:8545

Doi voter_account / proposal de vote them lan (moi account chi vote 1 lan).
"""
from ape import accounts, project


def main():
    password = "123456"
    address = "0x943Da320295c096a3608CF7e8Aa962eA5004478d"
    # voter1 da vote roi -> dung voter2 cho lan nay
    voter_account = "voter2"
    proposal = 1  # mountain

    voter = accounts.load(voter_account)
    voter.set_autosign(True, passphrase=password)
    contract = project.VotingApp.at(address)

    status = contract.voters(voter.address)
    if status.voted:
        print(f"{voter_account} DA vote roi (vote={status.vote}) — khong vote lai duoc.")
        print(f"winnerName = {contract.winnerName()}")
        return

    contract.vote(proposal, sender=voter)
    print(f"{voter_account} voted for proposal index {proposal}")
    print(f"winnerName = {contract.winnerName()}")
