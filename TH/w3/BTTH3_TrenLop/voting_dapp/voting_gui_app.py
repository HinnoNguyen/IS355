"""GUI PySide6 — Voting DApp (BTTH3 Tren Lop).

Chay:
  cd d:\\Study\\IS355\\TH\\w3\\voting_dapp
  d:\\Study\\IS355\\.venv-ape\\Scripts\\ape.exe run voting_gui_app --network ethereum:local:http://127.0.0.1:8545

hoac:
  d:\\Study\\IS355\\.venv-ape\\Scripts\\python.exe voting_gui_app.py
"""
import sys

from ape import accounts, networks, project
from PySide6 import QtWidgets, QtCore

VOTING_APP_ADDRESS = "0x943Da320295c096a3608CF7e8Aa962eA5004478d"
VOTER_PASSWORD = "123456"
VOTER_ACCOUNT = "voter3"  # voter1/voter2 da vote; dung voter3 cho GUI
NETWORK = "ethereum:local:http://127.0.0.1:8545"


class VotingWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.label = QtWidgets.QLabel("Voting Blockchain App")

        self.combobox = QtWidgets.QComboBox()
        self.combobox.addItems(["---"])

        self.button = QtWidgets.QPushButton("Vote")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combobox)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.button_on_clicked)

    @QtCore.Slot()
    def button_on_clicked(self):
        proposal = self.combobox.currentText()
        index = self.combobox.currentIndex()
        print(f"The selected proposal is {proposal}")
        print(f"The selected index is {index}")

        if index <= 0:
            print("Chon 1 de xuat hop le (khong phai ---).")
            return

        with networks.parse_network_choice(NETWORK):
            voter = accounts.load(VOTER_ACCOUNT)
            voter.set_autosign(True, passphrase=VOTER_PASSWORD)
            contract = project.VotingApp.at(VOTING_APP_ADDRESS)
            contract.vote(index - 1, sender=voter)
            print(f"Voted OK for proposal index {index - 1}")
            print(f"winnerName = {contract.winnerName()}")


def main():
    with networks.parse_network_choice(NETWORK):
        contract = project.VotingApp.at(VOTING_APP_ADDRESS)
        amount_proposals = int(contract.amountProposals())
        names = [contract.proposals(i).name for i in range(amount_proposals)]

    app = QtWidgets.QApplication([])

    widget = VotingWidget()
    widget.show()

    for name in names:
        widget.combobox.addItem(name)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
