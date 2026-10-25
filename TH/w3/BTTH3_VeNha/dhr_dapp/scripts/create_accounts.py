"""Tao 4 tai khoan Ape: hospital, patient1, patient2, doctor1 (password 123456).

Chay:
  ape run create_accounts
"""
from ape import accounts
from ape_accounts import generate_account

PASSWORD = "123456"
ALIASES = ("hospital", "patient1", "patient2", "doctor1")


def main():
    existing = set(accounts.aliases)
    for alias in ALIASES:
        if alias in existing:
            print(f"{alias:9} da ton tai: {accounts.load(alias).address}")
            continue
        account, _mnemonic = generate_account(alias, PASSWORD)
        print(f"{alias:9} tao moi : {account.address}")
