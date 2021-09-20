from enum import Enum

class myEnum(Enum):
    RED = 1
    BLUE = 2
    GREEN = 3


def test():

    print(myEnum.BLUE.value)


if __name__ == "__main__":
    test()