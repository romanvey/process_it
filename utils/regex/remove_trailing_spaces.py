import re
def remove_trailing_spaces(text):
    pattern = r"[\s\t]{2,}"
    return re.sub(pattern, "", text, flags=re.M | re.S)