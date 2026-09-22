# @version ^0.4.0

"""Bài 4: Quản lý danh bạ (struct + tra cứu theo tên)."""

struct Contact:
    name: String[64]
    phone: String[32]

contacts: HashMap[String[64], Contact]

@external
def addContract(name: String[64], phone: String[32]):
    """Thêm liên hệ mới (theo đề: addContract)."""
    assert len(name) > 0, "empty name"
    self.contacts[name] = Contact(name=name, phone=phone)

@external
@view
def getPhone(name: String[64]) -> String[32]:
    """Tra cứu số điện thoại theo tên."""
    assert len(self.contacts[name].name) > 0, "not found"
    return self.contacts[name].phone
