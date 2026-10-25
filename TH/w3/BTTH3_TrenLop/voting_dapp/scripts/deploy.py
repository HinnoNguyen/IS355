"""Deploy VotingApp len Geth (chairperson account).

Chay:
  ape run deploy --network ethereum:local:http://127.0.0.1:8545
"""
from ape import accounts, project


def main():
    password = "123456"
    chairperson = accounts.load("chairperson")
    chairperson.set_autosign(True, passphrase=password)
    contract = project.VotingApp.deploy(sender=chairperson)
    print(f"VotingApp deployed at: {contract.address}")
    chair = contract.chairperson()
    print(f"The chairperson account is {chair}")
