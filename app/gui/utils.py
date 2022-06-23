import re
from collections import namedtuple


def split_meta_name(meta_name: str) -> list:
    pattern = f"(\d+)-(\d+)\s(.+)\s\("
    matches = re.findall(pattern, meta_name)[0]
    Field = namedtuple("Field", "prefix, suffix, name")
    return Field(int(matches[0]), int(matches[1]), matches[2])
