"""Bai 3: Gui tx voi gas qua thap -> quan sat loi."""
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
assert w3.is_connected(), "Mo Geth truoc"

# Dung account[0] cua Geth --dev (thuong da unlock)
accounts = w3.eth.accounts
assert len(accounts) >= 1, "Khong co account"
sender = accounts[0]
# Neu chi 1 account, gui cho chinh no van du de thay loi gas
recipient = accounts[0]

print("sender   :", sender)
print("recipient:", recipient)
print("balance  :", w3.from_wei(w3.eth.get_balance(sender), "ether"), "ETH")

# Gas transfer toi thieu thuong = 21000. Dat gas=100 -> that bai
tx = {
    "from": sender,
    "to": recipient,
    "value": Web3.to_wei(0.001, "ether"),
    "gas": 100,  # CO TINH QUA THAP
    "gasPrice": Web3.to_wei("1", "gwei"),
    "nonce": w3.eth.get_transaction_count(sender),
}

print("\nThu gui tx gas=100 ...")
try:
    # Geth --dev: co the gui bang send_transaction neu account unlock
    tx_hash = w3.eth.send_transaction(tx)
    print("tx hash:", tx_hash.hex())
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
    print("status :", receipt["status"], "(0=fail)")
    print("gasUsed:", receipt["gasUsed"])
except Exception as e:
    print("LOI:", type(e).__name__)
    print(e)
    print(
        """
Giai thich:
- Transfer ETH can it nhat ~21000 gas.
- Dat gas=100 < 21000 -> node tu choi / intrinsic gas too low.
Cach sua: dat gas=21000 (hoac cao hon neu goi contract).
"""
    )
