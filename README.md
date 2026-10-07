# Forth language implementation in Python

## Example
5 4 + print  # Output: 9


### Token Determination Rules
Token Event rules, exit at first matched rule:

| _State_              | _Char Event_ | Description                              | Token Event   |
| -------------------- | ------------ | ---------------------------------------- | ------------- |
|                      |              |                                          |               |
| WAITING_END_OF_TOKEN | _(space)_    | Found a space, token is complete         | END_TOKEN     |
| WAITING_END_OF_TOKEN | _            | Found a char, continue parsing the token | PARSING_TOKEN |
| NORMAL_PARSING       | _(space)_    | Found a space, no meaning space, skip    | <no event>    |
| NORMAL_PARSING       | _            | Found a char                             | START_TOKEN   |
|                      |              |                                          |               |

### State Machine

| _Current State_              | _Event_               | Description                                                               | Next State                   |
| ---------------------------- | --------------------- | ------------------------------------------------------------------------- | ---------------------------- |
|                              |                       |                                                                           |                              |
| NORMAL_PARSING               | START_TOKEN           | Found the first char of a token, we don't know yet what this token means  | WAITING_END_OF_TOKEN         |
| WAITING_END_OF_TOKEN         | END_TOKEN             | Found the last char of a token, we have to decide what this token means   | NORMAL_PARSING               |
|                              |                       |                                                                           |                              |
| NORMAL_PARSING               | START_STRING          | Found the start string chars ´." ´                                        | PARSING_STRING               |
| PARSING_STRING               | END_STRING            | Found the last string char ´"´                                            | NORMAL_STRING                |
|                              |                       |                                                                           |                              |
| NORMAL_PARSING               | START_WORD_DEFINITION | Found the colon ":", starting the definition of a user word               | WAITING_USER_WORD_NAME       |
| WAITING_USER_WORD_NAME       | FOUND_USER_WORD_NAME  | The name of the word has been set                                         | WAITING_USER_WORD_DEFINITION |
| WAITING_USER_WORD_DEFINITION | DEFINITION            | Found the semocolon ";" char, the definition of the user word is complete | NORMAL_PARSING               |


### Token Type Determination

| _Rule_     | _Description_                                           | Token Type |
| ---------- | ------------------------------------------------------- | ---------- |
| IS_INTEGER | contains only digit and an optional initial minus sign? | INTEGER    |
| IS_COMMENT | contains only digit and an optional initial minus sign? | COMMENT    |


## Tokenizer

Token info:
(CATEGORY, TYPE, TEXT, VALUE, LINE, START_AT, END_AT)

```
57 4 .s

tokens = [
    ('LITERAL', 'NUMBER', "57", 47, 1, 1, 2),
    ('LITERAL', NUMBER', "4", 47, 1, 4, 5),
    ('WORD', "PRINT", ".s", ".s", 1, 7, 8),
]

```

```
22 +

tokens = [
    ('LITERAL', 'NUMBER', "22", 22, 1, 1, 2),
    ('MATH_OPERATOR', 'ADD', "+", "+", 1, 3, 4),

]
```

```
4 / comment

tokens = [
    ('LITERAL', 'NUMBER', "4", 4, 1, 1, 2),
    ('COMMENT', 'COMMENT', "/ comment", "/ comment", 1, 3, 12),
]
```

```
: square dup * ;

tokens = [
    ('DEFINITION', 'DEFINE_USER_WORD', ":", ":", 1, 1, 2),
    ('DEFINITION', 'USER_WORD_NAME', "SQUARE", "square", 1, 3, 8),
    ('DEFINITION', 'USER_WORD_DEFINITION', "DUP *", "dup *", 1, 3, 12),
]
```

# Appunti jonesforth

## Registro ESI
Puntatore alla prossima istruzione da eseguire

## Macro NEXT
Salva l'istruzione corrente, avanza ESI all'istruzione successiva da eseguire, esegue l'istruzione corrente.
Ogni istruzione deve richiamare NEXT, viene così eseguita l'istruzione successiva

## Interpret function
Interpreta una word che è composta da codice forth.
