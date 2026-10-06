# @version ^0.4.3

"""Chuoi cung ung nong san: theo doi san pham + event."""

struct Product:
    id: uint256
    name: String[64]
    currentOwner: address
    status: String[32]
    exists: bool

event ProductUpdated:
    id: indexed(uint256)
    newOwner: indexed(address)
    newStatus: String[32]

manager: public(address)
products: HashMap[uint256, Product]

@deploy
def __init__():
    self.manager = msg.sender

@external
def addProduct(id: uint256, name: String[64]):
    assert msg.sender == self.manager, "only manager"
    assert not self.products[id].exists, "exists"
    assert len(name) > 0, "empty name"
    self.products[id] = Product(
        id=id,
        name=name,
        currentOwner=msg.sender,
        status="created",
        exists=True,
    )
    log ProductUpdated(id=id, newOwner=msg.sender, newStatus="created")

@external
def transferProduct(id: uint256, newOwner: address, newStatus: String[32]):
    assert self.products[id].exists, "not found"
    assert newOwner != empty(address), "bad owner"
    assert len(newStatus) > 0, "empty status"
    # Chi manager hoac owner hien tai duoc chuyen
    p: Product = self.products[id]
    assert msg.sender == self.manager or msg.sender == p.currentOwner, "not allowed"
    self.products[id] = Product(
        id=p.id,
        name=p.name,
        currentOwner=newOwner,
        status=newStatus,
        exists=True,
    )
    log ProductUpdated(id=id, newOwner=newOwner, newStatus=newStatus)

@external
@view
def getProduct(id: uint256) -> (uint256, String[64], address, String[32]):
    assert self.products[id].exists, "not found"
    p: Product = self.products[id]
    return p.id, p.name, p.currentOwner, p.status
