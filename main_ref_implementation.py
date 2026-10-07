from enum import Enum, StrEnum


class TokenType(StrEnum):
    UNKNOWN = "UNKNOWN"
    NUMBER = "NUMBER"
    COMMENT = "COMMENT"
    DUP = "DUP"
    PRINT_STACK = "PRINT_STACK"
    ADD = "ADD"
    MINUS = "MINUS"


# ========================================= TOKEN DEFINITION =========================================
class ForthToken:
    @staticmethod
    def is_number(text: str, _):
        if (text.startswith("-") and text[1:].isdigit()) or text.isdigit():
            return True

    @staticmethod
    def is_word(text: str, word: str):
        return text.capitalize() == word.capitalize()

    TOKEN_TYPE_DET = [
        (is_number, None, TokenType.NUMBER),
        (is_word, "DUP", TokenType.DUP),
        (is_word, ".S", TokenType.PRINT_STACK),
        (is_word, "+", TokenType.ADD),
        (is_word, "-", TokenType.MINUS),
    ]

    def __init__(self):
        self.line_number = None
        self.start_pos = None
        self.end_pos = None
        self.text = None

    def start(self, line_number: int, start_pos: int, token_type: TokenType = TokenType.UNKNOWN):
        self.line_number = line_number
        self.start_pos = start_pos
        self.token_type = token_type

    def end(self, end_pos, text):
        self.end_pos = end_pos
        self.text = text

        # If the type not set during the start we need to determine the type
        if self.token_type == TokenType.UNKNOWN:
            for check_rule, rule_value, token_type in ForthToken.TOKEN_TYPE_DET:
                if check_rule(text, rule_value):
                    self.token_type = token_type
                    break

    def start_end(self):
        pass

    def is_pending(self):
        """Is the token pending? I mean started but not completed yet"""

        return self.start_pos

    def __str__(self):
        formatted_value = f"{self.text}"

        return f"line {self.line_number:>3} {self.start_pos:>2}:{self.end_pos:>2} type: {self.token_type:10} value : {[formatted_value]}"


# =========================================== FORTH PARSER ===========================================
class ForthParser:
    @staticmethod
    def is_generic_char(char: str):
        return char.isalpha() or char.isdigit() or char == "-" or char == "." or char == "+"

    @staticmethod
    def is_space(char: str):
        return char == " "

    @staticmethod
    def is_eol(char: str):
        return char == "\n"

    @staticmethod
    def is_comment(char: str):
        return char == "\\" or char == "("

    @staticmethod
    def is_not_eol(char: str):
        return char != "\n"

    class State(Enum):
        NORMAL_PARSING = 1
        WAITING_END_OF_TOKEN = 2
        WAITING_END_OF_COMMENT = 3

    class TokenEvent(Enum):
        START_TOKEN = 1
        PARSING_TOKEN = 2
        END_TOKEN = 3
        SKIP_CHAR = 4
        START_COMMENT = 5
        PARSING_COMMENT = 6
        END_COMMENT = 7

    class CharEvent:
        def __init__(self, line_number, position, character, line_source_code):
            self.line_number: int = line_number
            self.position: int = position
            self.character: str = character
            self.line_source_code: str = line_source_code

    # Rules to determine the event, ORDER IS VERY IMPORTANT!!!
    EVENT_RULES = [
        ((State.WAITING_END_OF_TOKEN, is_space), TokenEvent.END_TOKEN),
        ((State.WAITING_END_OF_TOKEN, is_eol), TokenEvent.END_TOKEN),
        ((State.WAITING_END_OF_TOKEN, is_generic_char), TokenEvent.PARSING_TOKEN),
        ((State.NORMAL_PARSING, is_space), TokenEvent.SKIP_CHAR),
        ((State.NORMAL_PARSING, is_eol), TokenEvent.SKIP_CHAR),
        ((State.NORMAL_PARSING, is_comment), TokenEvent.START_COMMENT),
        ((State.NORMAL_PARSING, is_generic_char), TokenEvent.START_TOKEN),
        ((State.WAITING_END_OF_COMMENT, is_not_eol), TokenEvent.PARSING_COMMENT),
        ((State.WAITING_END_OF_COMMENT, is_eol), TokenEvent.END_COMMENT),
    ]

    STATE_MACHINE = {
        (State.NORMAL_PARSING, TokenEvent.START_TOKEN): State.WAITING_END_OF_TOKEN,
        (State.NORMAL_PARSING, TokenEvent.SKIP_CHAR): State.NORMAL_PARSING,
        (State.WAITING_END_OF_TOKEN, TokenEvent.PARSING_TOKEN): State.WAITING_END_OF_TOKEN,
        (State.WAITING_END_OF_TOKEN, TokenEvent.END_TOKEN): State.NORMAL_PARSING,
        (State.NORMAL_PARSING, TokenEvent.START_COMMENT): State.WAITING_END_OF_COMMENT,
        (State.WAITING_END_OF_COMMENT, TokenEvent.PARSING_COMMENT): State.WAITING_END_OF_COMMENT,
        (State.WAITING_END_OF_COMMENT, TokenEvent.END_COMMENT): State.NORMAL_PARSING,
    }

    def __init__(self):
        self.state = self.State.NORMAL_PARSING
        self.last_event = None
        self.tokens = []
        self.user_words = []

    def _handle_token_event(
        self, token_event: TokenEvent, char_event: CharEvent, token: ForthToken
    ):

        match token_event:
            case self.TokenEvent.START_TOKEN:
                token.start(
                    char_event.line_number,
                    char_event.position,
                )

            case self.TokenEvent.PARSING_TOKEN:
                return

            case self.TokenEvent.END_TOKEN:
                token_text = char_event.line_source_code[token.start_pos : char_event.position]

                token.end(
                    end_pos=char_event.position,
                    text=token_text,
                )

            case self.TokenEvent.SKIP_CHAR:
                return

            case self.TokenEvent.START_COMMENT:
                token.start(char_event.line_number, char_event.position, TokenType.COMMENT)

            case self.TokenEvent.PARSING_COMMENT:
                return

            case self.TokenEvent.END_COMMENT:
                token_text = char_event.line_source_code[token.start_pos : char_event.position]

                token.end(
                    end_pos=char_event.position,
                    text=token_text,
                )

    def filter_rules_for_state(self, state: State):
        # I think this is really not so much transparent, I get it more trasparent wrapping in a function
        return [(event[0][1], event[1]) for event in self.EVENT_RULES if event[0][0] == state]

    def _handle_char_event(
        self, current_state: State, char_event: CharEvent, current_token: ForthToken
    ):

        event_det_rules = self.filter_rules_for_state(current_state)

        for event_det_rule_check, token_event in event_det_rules:
            if event_det_rule_check(char_event.character):
                self._handle_token_event(token_event, char_event, current_token)

                return token_event

        raise BaseException(
            f"No rule defined for state {current_state} char '{char_event.character}'"
        )

    def _parse_line(self, line_number, line_source_code):

        tokens = []

        current_state: ForthParser.State = ForthParser.State.NORMAL_PARSING

        current_token: ForthToken = ForthToken()

        # For each char in the line
        for position, char in enumerate(line_source_code):
            # Wrap info in a dataclass
            char_event = self.CharEvent(line_number, position, char, line_source_code)

            # Handle the char event
            token_event = self._handle_char_event(current_state, char_event, current_token)

            # A new token has been completed?
            if token_event == self.TokenEvent.END_TOKEN:
                tokens.append(current_token)

                current_token = ForthToken()

            # New state determination using the current state and the token event happened
            new_state = self.STATE_MACHINE[(current_state, token_event)]

            print(
                f"Current state {current_state} char '{char_event.character}' token event {token_event} next state {new_state}"
            )

            current_state = new_state

        # Handle the end of the line
        char_event = self.CharEvent(line_number, len(line_source_code), "\n", line_source_code)

        token_event = self._handle_char_event(current_state, char_event, current_token)

        if token_event == self.TokenEvent.END_TOKEN or token_event == self.TokenEvent.END_COMMENT:
            tokens.append(current_token)

        print(
            f"Current state {current_state} char '{char_event.character}' token event {token_event}, line completely parsed"
        )

        return tokens

    def parse(self, program_source_code):

        tokens = []

        lines = program_source_code.splitlines()

        for (
            line_number,
            source_code,
        ) in enumerate(lines, 1):
            tokens.extend(
                self._parse_line(
                    line_number=line_number,
                    line_source_code=source_code,
                )
            )

        return tokens


def print_pp(
    parsed_program: list[ForthToken],
):
    print("=============== Parsed program ===============")
    for token in parsed_program:
        print(token)


# ============================================     MAIN     ==========================================
def forth_main():
    with open(file="program.fs", mode="r") as program:
        source_code = program.read()

    forthParser = ForthParser()

    parsed_program = forthParser.parse(source_code)
    print_pp(parsed_program)
    # exec(parsed_program)


if __name__ == "__main__":
    forth_main()
