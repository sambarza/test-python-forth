class Token:
    @staticmethod
    def type_determination(value, modifier: TokenModifier) -> TokenType:

        if value == ";":
            return TokenType.END_DEFINE, TokenModifier.NORMAL

        if modifier == TokenModifier.DEFINE:
            return TokenType.DEFINITION, TokenModifier.DEFINE

        match value:
            case v if v[0] == "\\":
                return TokenType.COMMENT_LINE, TokenModifier.NORMAL

            case v if (v.startswith("-") and v[1:].isdigit()) or v.isdigit():
                return TokenType.NUMBER, TokenModifier.NORMAL

            case "+":
                return TokenType.ADD, TokenModifier.NORMAL

            case ".":
                return TokenType.PRINT, TokenModifier.NORMAL

            case ".s":
                return TokenType.PRINT_STACK, TokenModifier.NORMAL

            case v if v.lower() == "dup":
                return TokenType.DUP, TokenModifier.NORMAL

            case ":":
                return TokenType.START_DEFINE, TokenModifier.DEFINE

            case ";":
                return TokenType.END_DEFINE, TokenModifier.NORMAL

            case v if not v.isdigit():
                return TokenType.WORD, TokenModifier.NORMAL

            case _:
                return TokenType.UNKNOWN, TokenModifier.NORMAL

    @staticmethod
    def cast_value(value, type: TokenType):

        match type:
            case TokenType.NUMBER:
                return int(value)
            case _:
                return value

    @staticmethod
    def start_creation(line, start_at):

        new_token = Token()
        new_token.status = TokenStatus.INVALID

        new_token.line = line
        new_token.start_at = start_at
        new_token.end_at = None
        new_token.value = None
        new_token.next_modifier = None

        return new_token

    def complete_creation(self, end_at, value, modifier):
        self.end_at = end_at
        self.modifier = modifier

        self.type, self.next_modifier = Token.type_determination(value, modifier)

        self.value = Token.cast_value(value, self.type)

    @staticmethod
    def create(line: int, start_at: int, end_at: int, value, modifier):
        new_token = Token()

        new_token.line = line
        new_token.start_at = start_at
        new_token.end_at = end_at
        new_token.modifier = modifier

        new_token.type, new_token.next_modifier = Token.type_determination(value, modifier)

        new_token.value = Token.cast_value(value, new_token.type)

        return new_token

    @staticmethod
    def create_execution(value: str):
        new_token = Token()

        new_token.line = 0
        new_token.start_at = 0
        new_token.end_at = 0

        new_token.type, new_token.next_modifier = Token.type_determination(
            value, TokenModifier.NORMAL
        )

        new_token.value = Token.cast_value(value, new_token.type)

        return new_token

    def __str__(self):

        if self.type == TokenType.WORD:
            formatted_value = str(self.value)[:40]
        else:
            formatted_value = self.value

        return f"line {self.line:>3} {self.start_at:>2}:{self.end_at:>2} {self.type:30} {self.modifier} {self.next_modifier} value : {[formatted_value]}"


class Context:
    def __init__(self):
        self.stack = []


def parse_line(line_number, source_code):

    tokens = []

    token = None

    token_modifier = TokenModifier.NORMAL

    for i, c in enumerate(source_code):
        try:
            if c == "\\":
                token = Token.create(
                    line=line_number,
                    start_at=i,
                    end_at=i,
                    value=source_code[i:],
                    modifier=token_modifier,
                )
                tokens.append(token)

                token = None

                break

            if i == 0 and c == "(":
                break

            match c:
                case " ":
                    if token:
                        token.complete_creation(
                            end_at=i,
                            value=source_code[token.start_at : i],
                            modifier=token_modifier,
                        )
                        token_modifier = token.next_modifier

                        tokens.append(token)

                        token = None

                case "[":
                    token = Token.create(
                        line=line_number,
                        start_at=i,
                        end_at=i,
                        value=source_code[token.start_at : i],
                        token_modifer=token_modifier,
                    )
                    token_modifier = token.next_modifier

                    tokens.append(token)

                    token = None

                case _:
                    if not token:
                        token = Token.start_creation(line=line_number, start_at=i)

        except Exception as e:
            print(f"Line {line_number} column {i + 1} character `{c}`")
            raise e

    if token:
        token.complete_creation(
            end_at=i,
            value=source_code[token.start_at : len(source_code)],
            modifier=token_modifier,
        )
        token_modifier = token.next_modifier

        tokens.append(token)

        token = None

    return tokens


def parse_code(program_source_code):
    tokens = []

    lines = program_source_code.splitlines()

    for line_number, source_code in enumerate(lines, 1):
        tokens.extend(parse_line(line_number=line_number, source_code=source_code))

    return tokens


def print_pp(parsed_program):
    print("=============== Parsed program ===============")
    for token in parsed_program:
        print(token)


def exec(parsed_program: list[Token]):

    print("================== Execution =================")

    ctx = Context()

    for token in parsed_program:
        match token.type:
            case TokenType.NUMBER:
                ctx.stack.append(token)

            case TokenType.ADD:
                v1 = ctx.stack.pop(-2)
                v2 = ctx.stack.pop(-1)

                ctx.stack.append(Token.create_execution(value=str(v1.value + v2.value)))

            case TokenType.PRINT:
                print(ctx.stack[-1].value)

            case TokenType.PRINT_STACK:
                for t in ctx.stack:
                    print(t.value)

            case TokenType.DUP:
                v = ctx.stacko[-1]

                ctx.stack.append(Token.create_execution(value=v))


def main():
    with open(file="program.fs", mode="r") as program:
        source_code = program.read()

    parsed_program = parse_code(source_code)
    print_pp(parsed_program)
    exec(parsed_program)
