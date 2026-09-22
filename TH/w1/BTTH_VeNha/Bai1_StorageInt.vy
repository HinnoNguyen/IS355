# @version ^0.4.0

"""Bài 1: Lưu trữ số nguyên (int128)."""

stored_value: int128

@external
def store(num: int128):
    """Lưu một số nguyên vào biến trạng thái."""
    self.stored_value = num

@external
@view
def retrieve() -> int128:
    """Trả về giá trị đã lưu."""
    return self.stored_value
