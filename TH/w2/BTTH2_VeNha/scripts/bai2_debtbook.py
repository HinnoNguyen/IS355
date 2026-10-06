"""Bai 2: Deploy + test DebtBook (Ape script)."""
from ape import accounts, project


def main():
    owner = accounts[0]
    debtor = accounts[1]

    book = project.DebtBook.deploy(sender=owner)
    print("DebtBook at", book.address)
    print("debt ban dau:", book.getDebt(debtor))

    book.addDebt(debtor, 1000, sender=owner)
    print("sau addDebt(1000):", book.getDebt(debtor))

    book.addDebt(debtor, 500, sender=owner)
    print("sau addDebt(+500):", book.getDebt(debtor))


if __name__ == "__main__":
    main()
