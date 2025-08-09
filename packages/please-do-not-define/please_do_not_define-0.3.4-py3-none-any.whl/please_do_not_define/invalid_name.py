_illegal_name = [
    "女", "姑", "婆", "媳", "妇", "娘", "嬷", "姐", "妹", "嬢", "媛",
    "woman", "women", "girl", "lady", "Miss", "Mrs", "queen", "female",
    "she_", "_she", "her_", "_her"
]

def _is_illegal_name(name: str) -> bool:
    if not name:
        return False
    if name.lower() in ("she", "her"):
        return True
    return any(i.lower() in name.lower()
               if i not in ("Miss", "Mrs") else
               i in name for i in _illegal_name)
