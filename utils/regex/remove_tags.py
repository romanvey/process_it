import re
def remove_tags(text):
    pattern = r"<[^>]*>"
    return re.sub(pattern, "", text, flags=re.M | re.S)