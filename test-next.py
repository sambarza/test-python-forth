import traceback

return_stack = []


def push_return_stack(eax_pointer_code_word):
    return_stack.append(eax_pointer_code_word)


def pop_return_stack():
    return return_stack.pop()


class defword:
    def __init__(self, definition):
        self.codeword = self.docall
        self.definition = definition

    def docall(self):
        local_eai = 0
        while local_eai < len(self.definition):
            instruction = self.definition[local_eai]
            instruction()
            local_eai += 1

        next()

    def __call__(self, *args, **kwds):
        self.codeword()


class defcode:
    def __init__(self):
        self.codeword = self.call

    def call(self):
        assert 1 == 2, "not implemented"

    def __call__(self, *args, **kwds):
        self.codeword()


class first(defcode):
    def call(self):
        print("first")
        next()


class second(defcode):
    def call(self):
        print("second")
        next()


class third(defcode):
    def call(self):
        print("third")
        next()


def next():
    global eax_pointer_code_word
    global esi_index_next_word

    if esi_index_next_word > len(instructions) - 1:
        eax_pointer_code_word = None
        return

    eax_pointer_code_word = instructions[esi_index_next_word]
    esi_index_next_word = esi_index_next_word + 1


instructions = [defword([first(), second(), third()]), third()]

eax_pointer_code_word = instructions[0]
esi_index_next_word = 1

instruction = eax_pointer_code_word

while instruction:
    traceback.print_stack()
    instruction()
    instruction = eax_pointer_code_word
