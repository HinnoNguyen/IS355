from ape import accounts, project


def main():
    dev = accounts.load("is355_")
    dev.set_autosign(True, passphrase="1234567890")  # passphrase luc ape accounts import

    contract = project.SimpleStorage.deploy(sender=dev)
    print(f"Deployed at {contract.address}")

    tx = contract.store(42, sender=dev)
    print("Stored value 42")

    value = contract.retrieve.call()
    print(f"Retrieved value = {value}")
