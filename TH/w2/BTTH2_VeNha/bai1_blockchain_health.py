"""Bai 1: Kiem tra suc khoe Blockchain (Geth)."""
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
assert w3.is_connected(), "Mo Geth --dev --http (port 8545) truoc"

block_number = w3.eth.block_number
block = w3.eth.get_block(block_number, full_transactions=False)

print("=== Suc khoe Blockchain ===")
print("1) So block hien tai :", block_number)
print("2) Block moi nhat:")
print("   hash  :", block["hash"].hex())
# miner / coinbase tuy hardfork
miner = block.get("miner") or block.get("author")
print("   miner :", miner)
txs = block.get("transactions") or []
print("   so tx :", len(txs))

# Gas trung binh: gasUsed / so tx (neu co tx); neu 0 tx thi gasUsed=0
gas_used = block.get("gasUsed") or 0
if len(txs) > 0:
    avg_gas = gas_used / len(txs)
else:
    avg_gas = 0
print("3) Gas trung binh/tx cua block:", avg_gas)
print("   (gasUsed block =", gas_used, ")")
