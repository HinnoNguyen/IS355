"""Kich ban kiem thu tren Geth: 2 benh nhan + 1 bac si, cap quyen, ghi ho so, xem log.

Chay (sau deploy):
  ape run demo_flow --network ethereum:local:http://127.0.0.1:8545
"""
from datetime import datetime
from pathlib import Path

from ape import accounts, project

PASSWORD = "123456"


def load(alias):
    account = accounts.load(alias)
    account.set_autosign(True, passphrase=PASSWORD)
    return account


def show_tx(label, receipt):
    print(f"[{label}] tx={receipt.txn_hash}  status={'confirmed' if receipt.status == 1 else 'failed'}  block={receipt.block_number}")


def main():
    address = Path("dhr_address.txt").read_text(encoding="utf-8").strip()
    contract = project.DHR.at(address)
    hospital, p1, p2, doc = (load(a) for a in ("hospital", "patient1", "patient2", "doctor1"))
    print(f"DHR contract: {address}\n")

    if not contract.patients(p1).exists:
        show_tx("patient1 registerPatient", contract.registerPatient("Nguyen Van A", 1990, sender=p1))
    if not contract.patients(p2).exists:
        show_tx("patient2 registerPatient", contract.registerPatient("Tran Thi B", 1995, sender=p2))
    if not contract.doctors(doc).exists:
        show_tx("doctor1 registerDoctor", contract.registerDoctor("BS Le Van C", "Noi tong quat", sender=doc))
    if not contract.doctors(doc).verified:
        show_tx("hospital verifyDoctor", contract.verifyDoctor(doc, sender=hospital))

    show_tx("patient1 grantAccess(doctor1)", contract.grantAccess(doc, sender=p1))
    show_tx("doctor1 addHealthRecord(patient1)", contract.addHealthRecord(
        p1, "Viem hong cap", "Amoxicillin 500mg x 7 ngay", "2026-10-25", "Tai kham sau 1 tuan",
        sender=doc,
    ))
    show_tx("patient2 addHealthRecord(tu ghi)", contract.addHealthRecord(
        p2, "Kham suc khoe dinh ky", "Khong", "2026-10-25", "Binh thuong", sender=p2,
    ))
    show_tx("doctor1 logView(patient1)", contract.logView(p1, sender=doc))

    print("\nPatient count:", contract.patientCount(), "| Doctor count:", contract.doctorCount())

    for patient, name in ((p1, "patient1"), (p2, "patient2")):
        print(f"\n=== Ho so {name} ({patient.address}) ===")
        for i in range(contract.getRecordCount(patient)):
            r = contract.viewHealthRecord(patient, i, sender=patient)
            print(f"  #{i} {r.visitDate} | {r.diagnosis} | {r.prescription} | {r.note} | boi {r.doctor}")
        print(f"--- Activity log {name} ---")
        for i in range(contract.getLogCount(patient)):
            log = contract.getLog(patient, i, sender=patient)
            when = datetime.fromtimestamp(log.timestamp).strftime("%Y-%m-%d %H:%M:%S")
            print(f"  {when} | {log.action:16} | actor={log.actor} | target={log.target}")

    try:
        contract.addHealthRecord(p2, "x", "y", "2026-10-25", "z", sender=doc)
    except Exception as err:
        print(f"\ndoctor1 ghi ho so patient2 (chua duoc cap quyen) -> bi tu choi: {type(err).__name__}")
