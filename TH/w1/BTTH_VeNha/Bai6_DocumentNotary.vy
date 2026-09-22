# @version ^0.4.0

"""Bài 6 (nâng cao): Document Notary - công chứng hash + chữ ký số."""

struct Document:
    doc_hash: bytes32
    owner: address
    timestamp: uint256
    signature: String[256]
    exists: bool

documents: HashMap[bytes32, Document]

event DocumentRegistered:
    doc_hash: indexed(bytes32)
    owner: indexed(address)
    timestamp: uint256

event SignatureAdded:
    doc_hash: indexed(bytes32)
    owner: indexed(address)
    signature: String[256]

@external
def registerDocument(doc_hash: bytes32):
    """Đăng ký tài liệu bằng hash (bytes32)."""
    assert doc_hash != empty(bytes32), "empty hash"
    assert not self.documents[doc_hash].exists, "already registered"
    self.documents[doc_hash] = Document(
        doc_hash=doc_hash,
        owner=msg.sender,
        timestamp=block.timestamp,
        signature="",
        exists=True,
    )
    log DocumentRegistered(doc_hash=doc_hash, owner=msg.sender, timestamp=block.timestamp)

@external
@view
def verifyDocument(doc_hash: bytes32) -> bool:
    """Kiểm tra tài liệu với hash đã tồn tại chưa."""
    return self.documents[doc_hash].exists

@external
@view
def getDocument(doc_hash: bytes32) -> Document:
    """Lấy thông tin tài liệu đã đăng ký."""
    assert self.documents[doc_hash].exists, "not found"
    return self.documents[doc_hash]

@external
def addSignature(doc_hash: bytes32, signature: String[256]):
    """Chỉ chủ đăng ký mới được gắn chữ ký số."""
    assert self.documents[doc_hash].exists, "not found"
    assert msg.sender == self.documents[doc_hash].owner, "not owner"
    assert len(signature) > 0, "empty signature"
    self.documents[doc_hash].signature = signature
    log SignatureAdded(doc_hash=doc_hash, owner=msg.sender, signature=signature)
