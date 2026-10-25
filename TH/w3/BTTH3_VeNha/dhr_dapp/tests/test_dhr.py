import pytest
from ape.exceptions import ContractLogicError


def test_hospital(contract, hospital):
    assert contract.hospital() == hospital


def test_register(setup, patient1, patient2, doctor):
    assert setup.patientCount() == 2
    assert setup.doctorCount() == 1
    assert setup.patients(patient1).name == "Nguyen Van A"
    assert setup.patients(patient2).exists
    assert setup.doctors(doctor).verified


def test_register_twice_fail(setup, patient1):
    with pytest.raises(ContractLogicError):
        setup.registerPatient("Again", 2000, sender=patient1)


def test_verify_only_hospital(contract, doctor, patient1):
    contract.registerDoctor("BS X", "Nhi", sender=doctor)
    with pytest.raises(ContractLogicError):
        contract.verifyDoctor(doctor, sender=patient1)


def test_grant_and_add_record(setup, patient1, doctor):
    setup.grantAccess(doctor, sender=patient1)
    assert setup.hasAccess(patient1, doctor)

    setup.addHealthRecord(
        patient1, "Cam cum", "Paracetamol 500mg", "2026-10-25", "Nghi ngoi 3 ngay",
        sender=doctor,
    )
    assert setup.getRecordCount(patient1) == 1

    rec = setup.viewHealthRecord(patient1, 0, sender=doctor)
    assert rec.diagnosis == "Cam cum"
    assert rec.doctor == doctor


def test_doctor_without_access_fail(setup, patient2, doctor):
    with pytest.raises(ContractLogicError):
        setup.addHealthRecord(patient2, "x", "y", "2026-10-25", "z", sender=doctor)


def test_revoke_access(setup, patient1, doctor):
    setup.grantAccess(doctor, sender=patient1)
    setup.revokeAccess(doctor, sender=patient1)
    assert not setup.hasAccess(patient1, doctor)
    with pytest.raises(ContractLogicError):
        setup.addHealthRecord(patient1, "x", "y", "2026-10-25", "z", sender=doctor)


def test_activity_log(setup, patient1, doctor):
    setup.grantAccess(doctor, sender=patient1)
    setup.addHealthRecord(patient1, "Dau dau", "Panadol", "2026-10-25", "", sender=doctor)
    setup.logView(patient1, sender=doctor)

    actions = [
        setup.getLog(patient1, i, sender=patient1).action
        for i in range(setup.getLogCount(patient1))
    ]
    assert actions == ["REGISTER_PATIENT", "GRANT_ACCESS", "ADD_RECORD", "VIEW_RECORD"]
