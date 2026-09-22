# @version ^0.4.3

@external
@pure
def sum() -> uint256:
    s: uint256 = 0
    for i: uint256 in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        s += i
    return s

@external
@pure
def greet(time: String[10]) -> String[20]:
    if time == "morning":
        return "Good morning!"
    elif time == "evening":
        return "Good evening!"
    else:
        return "How are you?"
