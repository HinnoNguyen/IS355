"""Them de xuat sau khi deploy (chi chairperson).

Chay:
  ape run add_proposals --network ethereum:local:http://127.0.0.1:8545

Luu y: contract chi cho TOI DA 3 de xuat. Neu da them roi thi script se bo qua.
"""
from ape import accounts, project


def main():
    password = "123456"
    address = "0x943Da320295c096a3608CF7e8Aa962eA5004478d"

    chairperson = accounts.load("chairperson")
    chairperson.set_autosign(True, passphrase=password)
    contract = project.VotingApp.at(address)

    current = contract.amountProposals()
    print(f"amountProposals hien tai = {current}")
    if current >= 3:
        print("Da du 3 de xuat (MAX) — khong them nua. OK cho bao cao.")
        for i in range(current):
            print(f"  [{i}] {contract.proposals(i).name} (votes={contract.proposals(i).voteCount})")
        return

    for name in ("beach", "mountain", "city"):
        if contract.amountProposals() >= 3:
            break
        contract.addProposal(name, sender=chairperson)
        print(f"Added proposal: {name}")

    print(f"amountProposals = {contract.amountProposals()}")
