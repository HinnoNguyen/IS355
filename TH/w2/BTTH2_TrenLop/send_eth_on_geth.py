"""Chuyen ETH tren Geth (Windows: HTTP)."""
from pathlib import Path
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
assert w3.is_connected(), "Mo Geth --dev --http truoc (port 8545)"

keystore_dir = Path("my_keystore")
files = sorted(keystore_dir.glob("UTC--*"))
assert files, "Chua co file trong my_keystore/"
keystore_path = files[0]
print("keystore:", keystore_path.name)

password = "123456"  # password luc geth account new

encrypted_key = keystore_path.read_text(encoding="utf-8")
sender_private_key = w3.eth.account.decrypt(encrypted_key, password)
print("PRIVATE KEY (hex): 0x" + sender_private_key.hex())

sender_address = w3.eth.account.from_key(sender_private_key).address
recipient_address = Web3.to_checksum_address(w3.eth.accounts[0])
print("sender   :", sender_address)
print("recipient:", recipient_address)

amount = Web3.to_wei(2, "ether")
transaction = {
    "chainId": w3.eth.chain_id,
    "from": sender_address,
    "to": recipient_address,
    "value": amount,
    "gas": 21000,
    "gasPrice": Web3.to_wei("50", "gwei"),
    "nonce": w3.eth.get_transaction_count(sender_address),
}

signed = w3.eth.account.sign_transaction(transaction, sender_private_key)
raw = getattr(signed, "raw_transaction", None) or signed.rawTransaction
tx_hash = w3.eth.send_raw_transaction(raw)
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("tx hash :", tx_hash.hex())
print("gasUsed :", receipt["gasUsed"])
print("value   :", amount, "wei =", w3.from_wei(amount, "ether"), "ETH")
print("phi ~   :", receipt["gasUsed"] * transaction["gasPrice"], "wei")
