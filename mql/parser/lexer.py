import string
import json
import collections
from mql.common.errors import MqlSyntaxError
from .consts import KEYWORDS


class Tokens:
    EOF = 1
    WILDCARD = 2
    IDENTIFIER = 3
    KEYWORD = 4
    INT = 5
    FLOAT = 6
    STRING = 7
    COLON = 8
    SEMICOLON = 9
    COMA = 10
    EXPRESSION = 11
    PAREN_LEFT = 12
    PAREN_RIGHT = 13
    QUESTION = 14
    DOT = 15


TOKENS_NAMES = {
    Tokens.EOF: 'EOF',
    Tokens.WILDCARD: '*',
    Tokens.COLON: ':',
    Tokens.COMA: ',',
    Tokens.COLON: ':',
    Tokens.SEMICOLON: ';',
    Tokens.PAREN_LEFT: '(',
    Tokens.PAREN_RIGHT: ')',
    Tokens.IDENTIFIER: 'Identifier',
    Tokens.KEYWORD: 'Keyword',
    Tokens.EXPRESSION: 'Expression',
    Tokens.INT: 'Int',
    Tokens.FLOAT: 'Float',
    Tokens.STRING: 'String',
    Tokens.QUESTION: '?',
    Tokens.DOT: '.'
}


def type_to_name(type_):
    return TOKENS_NAMES.get(type_)


TOKENS_CODE = {
    ord('*'): Tokens.WILDCARD,
    ord(','): Tokens.COMA,
    ord('('): Tokens.PAREN_LEFT,
    ord(')'): Tokens.PAREN_RIGHT,
    ord('?'): Tokens.QUESTION,
    ord('.'): Tokens.DOT
    # ord('!'): Tokens.BANG,
    # ord(':'): Tokens.COLON,
    # ord('='): Tokens.EQUAL,
    # ord('|'): Tokens.PIPE
}


def print_char_code(code):
    if code is None:
        return '<EOF>'
    return json.dumps(chr(code))


def get_type_name(type_):
    return TOKENS_NAMES.get(type_)


Token = collections.namedtuple('Token', ['type', 'start', 'end', 'value'])


def EOFToken(start, end):
    return Token(Tokens.EOF, start, end, '')


def IdentifierToken(start, end, value):
    return Token(Tokens.IDENTIFIER, start, end, value)


def KeywordToken(start, end, value):
    return Token(Tokens.KEYWORD, start, end, value)


def NumberToken(type_, start, end, value):
    return Token(type_, start, end, value)


def StringToken(start, end, value):
    return Token(Tokens.STRING, start, end, value)


ESCAPED = {
    34: '"',
    47: '/',
    92: '\\',
    110: '\n',
    114: '\r',
    116: '\t',
}


class Lexer:
    def __init__(self, source):
        self.source = source
        self.length = len(source)
        self.position = 0
        self._end = False

    def __iter__(self):
        return self

    def __next__(self):
        if self._end:
            raise StopIteration
        token = self.next()
        if token.type == Tokens.EOF:
            self._end = True
        return token

    def next(self):
        self._skip_whitespace()

        if self._is_eof():
            return self._eof()

        code = self._current_char_code()
        kind = TOKENS_CODE.get(code, None)
        if kind:
            self.position += 1
            return Token(
                kind, self.position - 1, self.position - 1, chr(code)
            )
        #            !   <   =   >   &   |
        if code in (33, 60, 61, 62, 38, 124):
            return self._scan_expression()

        if code == 34:  # "
            return self._scan_string()
        if code == 45 or 48 <= code <= 57:  # [-0-9]
            return self._scan_number()
        if 65 <= code <= 90 or code == 95 or 97 <= code <= 122:  # [a-zA-Z_]
            return self._scan_identifier()

        self.position = self.length
        raise MqlSyntaxError(
            'Invalid character: {}'.format(print_char_code(code)),
            self.source, self.position
        )

    def _scan_expression(self):
        #  !   <   =   >   &   |
        # 33, 60, 61, 62, 38, 124
        code = self._current_char_code()
        start = self.position
        if code in (38, 61, 124):
            expr = self.source[start]
            self._move_to_next()
            return Token(Tokens.EXPRESSION, start, start, expr)

        next_code = self._next_char_code()
        if code == 33:
            if next_code == 61:
                self._move_to_next(2)
                return Token(Tokens.EXPRESSION, start, start+1, '!=')
        elif code in (60, 62):
            if next_code == 61:
                self._move_to_next()
            position = self.position
            expr = self.source[start:position+1]
            self._move_to_next()
            return Token(Tokens.EXPRESSION, start, position, expr)


        raise MqlSyntaxError(
            'Invalid character: {}'.format(print_char_code(code)),
            self.source, self.position-1
        )

    def _scan_number(self):
        '''
        Int:   -?(0|[1-9][0-9]*)
        Float: -?(0|[1-9][0-9]*)(\.[0-9]+)?((E|e)(+|-)?[0-9]+)?
        '''
        start = self.position
        is_float = False
        code = self._current_char_code()

        if code == 45:  # -
            self.position += 1
            code = self._current_char_code()

        if code == 48:  # 0
            self.position += 1
            code = self._current_char_code()
            if code and 48 <= code <= 57:
                self.position = self.length
                raise MqlSyntaxError(
                    'Invalid number after 0: {}'.format(print_char_code(code)),
                    self.source, self.position
                )
        else:
            self._scan_int()
            code = self._current_char_code()

        if code == 46:  # .
            is_float = True
            self.position += 1
            self._scan_int()
            code = self._current_char_code()

        number = self.source[start:self.position]

        return NumberToken(
            Tokens.FLOAT if is_float else Tokens.INT,
            start, self.position-1, number
        )

    def _scan_int(self):
        code = self._current_char_code()
        if code is not None and 48 <= code <= 57:
            while self.position < self.length:
                self.position += 1
                code = self._current_char_code()
                if not (code is not None and 48 <= code <= 57):
                    break
        else:
            scode = print_char_code(code)
            raise MqlSyntaxError(
                'Invalid number. Expected digit but got: {}'.format(scode),
                self.source, self.position
            )

    def _scan_string(self):

        self.position += 1  # fist char: "
        start = self.position
        code = self._current_char_code()
        value = []

        while self.position < self.length:
            code = self._current_char_code()
            if code == 34:  # quote: "
                break
            self.position += 1
            if code == 92:  # \
                value.append(self.source[start:self.position-1])

                code = self._current_char_code()
                escaped = ESCAPED.get(code)
                if escaped:
                    value.append(escaped)
                else:
                    raise MqlSyntaxError(
                        'Invalid escape character: \\{}'.format(print_char_code(code)),
                        self.source, self.position
                    )
                self.position += 1
                start = self.position

        if code != 34:  # quote: "
            raise MqlSyntaxError('Unterminated string', self.source, self.position)
        value.append(self.source[start:self.position])

        self.position += 1
        return StringToken(start, self.position-1, ''.join(value))

    def _read_identifier(self):
        '''Reads an alphanumeric and underscore chars for keyword
            [_a-zA-Z][_a-zA-Z0-9]
        '''
        first = True
        start = self.position
        while self.position < self.length:
            code = self._current_char_code()
            if not (code and code == 95 or  # _
                    65 <= code <= 90 or  # A-Z
                    97 <= code <= 122 or  # a-z
                    (48 <= code <= 57 and not first)):  # 0-9
                break
            first = False
            self._move_to_next()
        value = self.source[start:self.position]
        return start, self.position - 1, value

    def _scan_identifier(self):
        start, stop, value = self._read_identifier()
        if len(value) == 1:
            return IdentifierToken(start, stop, value)
        if value.upper() in KEYWORDS:
            return KeywordToken(start, stop, value)
        return IdentifierToken(start, stop, value)

    def _skip_whitespace(self):
        find = False
        while self.position < self.length:
            char = self._current_char()
            if char in string.whitespace:
                self.position += 1
                find = True
            else:
                break
        return find

    def _move_to_next(self, offset=1):
        self.position += offset

    def _current_char(self):
        try:
            return self.source[self.position]
        except IndexError:
            return ''

    def _next_char_code(self, offset=1):
        try:
            return ord(self.source[self.position + offset])
        except IndexError:
            return 0

    def _current_char_code(self):
        return self._next_char_code(0)

    def _is_eof(self):
        return self.position >= self.length

    def _eof(self):
        return EOFToken(self.position, self.position)
