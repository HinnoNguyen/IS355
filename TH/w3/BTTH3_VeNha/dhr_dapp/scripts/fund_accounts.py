"""Nap 10 ETH tu dev account cua Geth (eth.accounts[0]) cho 4 tai khoan DHR.

Chay:
  ape run fund_accounts --network ethereum:local:http://127.0.0.1:8545
"""
from ape import accounts, chain

ALIASES = ("hospital", "patient1", "patient2", "doctor1")


def main():
    w3 = chain.provider.web3
    dev = w3.eth.accounts[0]
    print(f"Dev account Geth: {dev}")
    for alias in ALIASES:
        to = accounts.load(alias).address
        tx_hash = w3.eth.send_transaction({"from": dev, "to": to, "value": w3.to_wei(10, "ether")})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        balance = w3.from_wei(w3.eth.get_balance(to), "ether")
        print(f"{alias:9} {to}  balance = {balance} ETH  (tx {tx_hash.hex()[:18]}...)")
