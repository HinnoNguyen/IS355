# @version ^0.4.3

interface Storage:
    def retrieve() -> uint256: view

storage_contract: Storage

@deploy
def __init__(storage_address: address):
    self.storage_contract = Storage(storage_address)

@external
def call_retrieve() -> uint256:
    return staticcall self.storage_contract.retrieve()
