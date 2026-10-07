from enum import Enum, StrEnum


class ForthWord(self):
    def __init__(self):
        self.name: str = None
        self.hidden: bool = None
        self.immediate: bool = None
        self.definition = None

    def __call__(self, *args, **kwargs):
        pass


class Forth:
    def __init__(self):
        self.return_stack = []

    def def_word(self):
        pass

    def def_code(self):
        pass

    def push_return_stack(self):
        pass

    def docoll(self):
        pass


def forth_main():
    print("Hello, Forth!")


if __name__ == "__main__":
    forth_main()
