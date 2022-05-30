from dataclasses import dataclass

from app.modules.utils import dataclass_from_dict

TEST_DICT = {"x": 0, "y": 1}


@dataclass
class DClass:
    x: int
    y: int


def test_dataclass_from_dict():
    T = dataclass_from_dict(DClass, TEST_DICT)
    assert T == DClass(x=0, y=1)
