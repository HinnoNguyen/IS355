"""Deploy DHR len Geth cuc bo bang tai khoan hospital.

Chay:
  ape run deploy --network ethereum:local:http://127.0.0.1:8545

Dia chi contract duoc ghi vao dhr_address.txt (GUI va script demo doc file nay).
"""
from pathlib import Path

from ape import accounts, project

PASSWORD = "123456"


def main():
    hospital = accounts.load("hospital")
    hospital.set_autosign(True, passphrase=PASSWORD)

    contract = project.DHR.deploy(sender=hospital)
    Path("dhr_address.txt").write_text(contract.address, encoding="utf-8")

    print(f"DHR deployed at : {contract.address}")
    print(f"Hospital        : {contract.hospital()}")
    print("Da luu dia chi vao dhr_address.txt")
