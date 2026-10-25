import pytest


@pytest.fixture
def hospital(accounts):
    return accounts[0]


@pytest.fixture
def patient1(accounts):
    return accounts[1]


@pytest.fixture
def patient2(accounts):
    return accounts[2]


@pytest.fixture
def doctor(accounts):
    return accounts[3]


@pytest.fixture
def contract(hospital, project):
    return hospital.deploy(project.DHR)


@pytest.fixture
def setup(contract, hospital, patient1, patient2, doctor):
    contract.registerPatient("Nguyen Van A", 1990, sender=patient1)
    contract.registerPatient("Tran Thi B", 1995, sender=patient2)
    contract.registerDoctor("BS Le Van C", "Noi tong quat", sender=doctor)
    contract.verifyDoctor(doctor, sender=hospital)
    return contract
