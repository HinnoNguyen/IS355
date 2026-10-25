# @version ^0.4.3

"""
Digital Health Records DApp (BTTH3 - Bai tap ve nha).

Vai tro:
- Hospital (nguoi deploy): xac thuc bac si.
- Patient: tao ho so, cap / thu hoi quyen cho bac si, xem lich su.
- Doctor: dang ky, sau khi duoc xac thuc va duoc cap quyen thi xem / ghi ho so.
Moi thao tac deu ghi log on-chain (ActivityLog) va phat event.
"""

struct PatientRecord:
    name: String[64]
    birthYear: uint256
    recordCount: uint256
    logCount: uint256
    exists: bool

struct DoctorInfo:
    name: String[64]
    specialty: String[64]
    verified: bool
    exists: bool

struct AccessPermission:
    canRead: bool
    canWrite: bool
    grantedAt: uint256

struct HealthRecord:
    diagnosis: String[200]
    prescription: String[200]
    visitDate: String[32]
    note: String[200]
    doctor: address
    timestamp: uint256

struct ActivityLog:
    actor: address
    action: String[32]
    target: address
    timestamp: uint256

event PatientRegistered:
    patient: indexed(address)
    name: String[64]

event DoctorRegistered:
    doctor: indexed(address)
    name: String[64]

event DoctorVerified:
    doctor: indexed(address)
    hospital: indexed(address)

event AccessGranted:
    patient: indexed(address)
    doctor: indexed(address)

event AccessRevoked:
    patient: indexed(address)
    doctor: indexed(address)

event RecordAdded:
    patient: indexed(address)
    author: indexed(address)
    index: uint256

event RecordViewed:
    patient: indexed(address)
    viewer: indexed(address)

hospital: public(address)
patients: public(HashMap[address, PatientRecord])
doctors: public(HashMap[address, DoctorInfo])
permissions: public(HashMap[address, HashMap[address, AccessPermission]])
records: HashMap[address, HashMap[uint256, HealthRecord]]
logs: HashMap[address, HashMap[uint256, ActivityLog]]
patientCount: public(uint256)
doctorCount: public(uint256)


@deploy
def __init__():
    self.hospital = msg.sender


@internal
def _log(patient: address, action: String[32], target: address):
    i: uint256 = self.patients[patient].logCount
    self.logs[patient][i] = ActivityLog(
        actor=msg.sender, action=action, target=target, timestamp=block.timestamp
    )
    self.patients[patient].logCount = i + 1


@view
@internal
def _canRead(patient: address, viewer: address) -> bool:
    if viewer == patient:
        return True
    return self.doctors[viewer].verified and self.permissions[patient][viewer].canRead


@view
@internal
def _canWrite(patient: address, author: address) -> bool:
    if author == patient:
        return True
    return self.doctors[author].verified and self.permissions[patient][author].canWrite


@external
def registerPatient(_name: String[64], _birthYear: uint256):
    assert not self.patients[msg.sender].exists, "patient exists"
    assert not self.doctors[msg.sender].exists, "address is a doctor"
    assert len(_name) > 0, "empty name"
    self.patients[msg.sender] = PatientRecord(
        name=_name, birthYear=_birthYear, recordCount=0, logCount=0, exists=True
    )
    self.patientCount += 1
    self._log(msg.sender, "REGISTER_PATIENT", msg.sender)
    log PatientRegistered(patient=msg.sender, name=_name)


@external
def registerDoctor(_name: String[64], _specialty: String[64]):
    assert not self.doctors[msg.sender].exists, "doctor exists"
    assert not self.patients[msg.sender].exists, "address is a patient"
    assert len(_name) > 0, "empty name"
    self.doctors[msg.sender] = DoctorInfo(
        name=_name, specialty=_specialty, verified=False, exists=True
    )
    self.doctorCount += 1
    log DoctorRegistered(doctor=msg.sender, name=_name)


@external
def verifyDoctor(_doctor: address):
    assert msg.sender == self.hospital, "only hospital"
    assert self.doctors[_doctor].exists, "doctor not registered"
    self.doctors[_doctor].verified = True
    log DoctorVerified(doctor=_doctor, hospital=msg.sender)


@external
def grantAccess(_doctor: address):
    assert self.patients[msg.sender].exists, "not a patient"
    assert self.doctors[_doctor].verified, "doctor not verified"
    self.permissions[msg.sender][_doctor] = AccessPermission(
        canRead=True, canWrite=True, grantedAt=block.timestamp
    )
    self._log(msg.sender, "GRANT_ACCESS", _doctor)
    log AccessGranted(patient=msg.sender, doctor=_doctor)


@external
def revokeAccess(_doctor: address):
    assert self.patients[msg.sender].exists, "not a patient"
    assert self.permissions[msg.sender][_doctor].canRead, "no access to revoke"
    self.permissions[msg.sender][_doctor] = empty(AccessPermission)
    self._log(msg.sender, "REVOKE_ACCESS", _doctor)
    log AccessRevoked(patient=msg.sender, doctor=_doctor)


@external
def addHealthRecord(
    _patient: address,
    _diagnosis: String[200],
    _prescription: String[200],
    _visitDate: String[32],
    _note: String[200],
):
    assert self.patients[_patient].exists, "patient not registered"
    assert self._canWrite(_patient, msg.sender), "no write access"
    i: uint256 = self.patients[_patient].recordCount
    self.records[_patient][i] = HealthRecord(
        diagnosis=_diagnosis,
        prescription=_prescription,
        visitDate=_visitDate,
        note=_note,
        doctor=msg.sender,
        timestamp=block.timestamp,
    )
    self.patients[_patient].recordCount = i + 1
    self._log(_patient, "ADD_RECORD", msg.sender)
    log RecordAdded(patient=_patient, author=msg.sender, index=i)


@external
def logView(_patient: address):
    """Ghi lai viec bac si mo ho so (view function khong ghi log duoc)."""
    assert self.patients[_patient].exists, "patient not registered"
    assert self._canRead(_patient, msg.sender), "no read access"
    self._log(_patient, "VIEW_RECORD", msg.sender)
    log RecordViewed(patient=_patient, viewer=msg.sender)


@view
@external
def viewHealthRecord(_patient: address, _index: uint256) -> HealthRecord:
    assert self._canRead(_patient, msg.sender), "no read access"
    assert _index < self.patients[_patient].recordCount, "bad index"
    return self.records[_patient][_index]


@view
@external
def getRecordCount(_patient: address) -> uint256:
    return self.patients[_patient].recordCount


@view
@external
def getLogCount(_patient: address) -> uint256:
    return self.patients[_patient].logCount


@view
@external
def getLog(_patient: address, _index: uint256) -> ActivityLog:
    assert self._canRead(_patient, msg.sender), "no read access"
    assert _index < self.patients[_patient].logCount, "bad index"
    return self.logs[_patient][_index]


@view
@external
def hasAccess(_patient: address, _doctor: address) -> bool:
    return self.permissions[_patient][_doctor].canRead
