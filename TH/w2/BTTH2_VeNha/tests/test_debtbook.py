import pytest


@pytest.fixture
def owner(accounts):
    return accounts[0]


@pytest.fixture
def debtor(accounts):
    return accounts[1]


@pytest.fixture
def book(owner, project):
    return owner.deploy(project.DebtBook)


def test_initial_debt(book, debtor):
    assert book.getDebt(debtor) == 0


def test_add_debt(book, owner, debtor):
    book.addDebt(debtor, 100, sender=owner)
    assert book.getDebt(debtor) == 100
    book.addDebt(debtor, 50, sender=owner)
    assert book.getDebt(debtor) == 150


def test_only_owner(book, debtor, accounts):
    with pytest.raises(Exception):
        book.addDebt(debtor, 1, sender=accounts[2])
