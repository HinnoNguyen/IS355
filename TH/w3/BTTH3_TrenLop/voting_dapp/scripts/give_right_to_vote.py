"""Cap quyen bo phieu cho voter1/2/3 (chi chairperson goi duoc).

Chay:
  ape run give_right_to_vote --network ethereum:local:http://127.0.0.1:8545

Neu voter da duoc cap quyen (weight>0) hoac da vote thi bo qua.
"""
from ape import accounts, project


def main():
    password = "123456"
    address = "0x943Da320295c096a3608CF7e8Aa962eA5004478d"
    voters = {
        "voter1": "0xf7F4E94C28beC0BCc0082f277b2AAdb7BD149202",
        "voter2": "0x1Cc299d4c374E56E26E1626147fA44113775F99D",
        "voter3": "0x5A94046CD5Eb0736e4AC969581B00cb3100ca326",
    }

    chairperson = accounts.load("chairperson")
    chairperson.set_autosign(True, passphrase=password)
    contract = project.VotingApp.at(address)

    print(f"voterCount hien tai = {contract.voterCount()}")
    for name, addr in voters.items():
        v = contract.voters(addr)
        # Da cap quyen (weight>0) HOAC da vote (weight ve 0 nhung voted=True)
        if v.weight > 0 or v.voted:
            print(f"  {name}: weight={v.weight}, voted={v.voted} — da xu ly, skip")
            continue
        contract.giveRightToVote(addr, 1, sender=chairperson)
        print(f"  Gave right to {name} weight=1")

    print(f"Done. voterCount = {contract.voterCount()}")
