"""Bai 4: 3 account bo phieu + in getWinner (Ape)."""
from ape import accounts, project, networks


def main():
    # Dung accounts test/local: accounts[0] deploy, [1][2][3] bo phieu
    deployer = accounts[0]
    voters = [accounts[1], accounts[2], accounts[3]]

    voting = project.Voting.deploy(sender=deployer)
    print("Voting at", voting.address)

    voting.addCandidate("An", sender=deployer)
    voting.addCandidate("Binh", sender=deployer)
    voting.addCandidate("Chi", sender=deployer)
    print("Candidates: 0=An, 1=Binh, 2=Chi")

    # 3 phieu: An, An, Binh -> An thang
    voting.vote(0, sender=voters[0])
    voting.vote(0, sender=voters[1])
    voting.vote(1, sender=voters[2])
    print("Votes cast.")

    winner_id, name, count = voting.getWinner()
    print(f"Winner: id={winner_id}, name={name}, votes={count}")


if __name__ == "__main__":
    # ape run bai4_voting --network ethereum:local:http://127.0.0.1:8545
    main()
