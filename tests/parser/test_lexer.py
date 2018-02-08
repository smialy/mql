import string
import pytest
from mql.common.errors import MqlSyntaxError
from mql.parser.lexer import Lexer, Tokens


def all_tokens(txt):
    lexer = Lexer(txt)
    return list(lexer)


def first_token(txt):
    lexer = Lexer(txt)
    return lexer.next()


def test_eof():
    assert first_token('').type == Tokens.EOF


def test_one_space():
    assert first_token(' ').type == Tokens.EOF
    assert first_token('   ').type == Tokens.EOF


def test_one_dot():
    assert first_token('.').type == Tokens.DOT
    assert first_token(' . ').type == Tokens.DOT


def test_many_space():
    assert first_token(string.whitespace).type == Tokens.EOF


def test_wildcard():
    assert first_token('*').type == Tokens.WILDCARD


def test_indentifier():
    assert first_token('abc').type == Tokens.IDENTIFIER
    assert first_token('_').type == Tokens.IDENTIFIER
    assert first_token('a_').type == Tokens.IDENTIFIER
    assert first_token('_a').type == Tokens.IDENTIFIER
    assert first_token('_a_').type == Tokens.IDENTIFIER
    assert first_token('_a_b_').type == Tokens.IDENTIFIER
    assert first_token('a0').type == Tokens.IDENTIFIER
    assert first_token('a0a').type == Tokens.IDENTIFIER


def test_binary_and():
    assert first_token('&').type == Tokens.EXPRESSION
    assert first_token('&').value == '&'


def test_binary_or():
    assert first_token('|').type == Tokens.EXPRESSION
    assert first_token('|').value == '|'


def test_indentifier_dot():
    tokens = all_tokens('ab.cd')
    assert len(tokens) == 4
    assert tokens[0].type == Tokens.IDENTIFIER
    assert tokens[1].type == Tokens.DOT
    assert tokens[2].type == Tokens.IDENTIFIER
    assert tokens[3].type == Tokens.EOF


def test_indentifier_dots():
    tokens = all_tokens('ab.cd.ef')
    assert len(tokens) == 6
    assert tokens[0].type == Tokens.IDENTIFIER
    assert tokens[1].type == Tokens.DOT
    assert tokens[2].type == Tokens.IDENTIFIER
    assert tokens[3].type == Tokens.DOT
    assert tokens[4].type == Tokens.IDENTIFIER
    assert tokens[5].type == Tokens.EOF


def test_single_token():
    token = first_token('select')
    assert token.value == 'select'
    assert token.type == Tokens.KEYWORD
    assert token.start == 0
    assert token.end == 5


def test_coma():
    tokens = all_tokens('a,b,c')
    assert tokens[0].type == Tokens.IDENTIFIER
    assert tokens[1].type == Tokens.COMA
    assert tokens[1].value == ','
    assert tokens[2].type == Tokens.IDENTIFIER
    assert tokens[3].type == Tokens.COMA
    assert tokens[3].value == ','
    assert tokens[4].type == Tokens.IDENTIFIER
    assert tokens[5].type == Tokens.EOF


def test_parent():
    tokens = all_tokens('(a)')
    assert len(tokens) == 4  # + EOF
    token = tokens[0]
    assert token.type == Tokens.PAREN_LEFT
    assert token.value == '('
    assert token.start == 0
    assert token.end == 0

    token = tokens[1]
    assert token.type == Tokens.IDENTIFIER
    assert token.value == 'a'
    assert token.start == 1
    assert token.end == 1

    token = tokens[2]
    assert token.type == Tokens.PAREN_RIGHT
    assert token.value == ')'
    assert token.start == 2
    assert token.end == 2


def test_more_tokens():
    txt = 'select * from table'
    expect = [
        (Tokens.KEYWORD, 'select', 0, 5),
        (Tokens.WILDCARD, '*', 7, 7),
        (Tokens.KEYWORD, 'from', 9, 12),
        (Tokens.KEYWORD, 'table', 14, 18),
        (Tokens.EOF, '', 19, 19),
    ]

    def token_map(t):
        return (t.type, t.value, t.start, t.end)

    tokens = list(map(token_map, all_tokens(txt)))
    assert len(tokens) == 5  # 4 + EOF
    assert expect[0] == tokens[0]
    assert expect[1] == tokens[1]
    assert expect[2] == tokens[2]
    assert expect[3] == tokens[3]
    assert expect[4] == tokens[4]


def test_one_digit():
    tokens = all_tokens('1')
    assert tokens[0].type == Tokens.INT
    assert tokens[0].value == '1'
    assert tokens[1].type == Tokens.EOF


def test_one_zero():
    tokens = all_tokens('0')
    assert tokens[0].type == Tokens.INT
    assert tokens[0].value == '0'
    assert tokens[1].type == Tokens.EOF


def test_incorect_zero():
    with pytest.raises(MqlSyntaxError):
        all_tokens('01')


def test_many_single_digits():
    tokens = all_tokens('1 2 3')
    assert tokens[0].type == Tokens.INT
    assert tokens[0].value == '1'
    assert tokens[1].type == Tokens.INT
    assert tokens[1].value == '2'
    assert tokens[2].type == Tokens.INT
    assert tokens[2].value == '3'
    assert tokens[3].type == Tokens.EOF


def test_many_numbers():
    tokens = all_tokens('1 2 3')
    assert tokens[0].type == Tokens.INT
    assert tokens[0].value == '1'
    assert tokens[1].type == Tokens.INT
    assert tokens[1].value == '2'
    assert tokens[2].type == Tokens.INT
    assert tokens[2].value == '3'
    assert tokens[3].type == Tokens.EOF


def test_number_int():
    tokens = all_tokens('12')
    assert tokens[0].type == Tokens.INT
    assert tokens[0].value == '12'
    assert tokens[1].type == Tokens.EOF


def test_number_int_minus():
    tokens = all_tokens('-12')
    assert tokens[0].type == Tokens.INT
    assert tokens[0].value == '-12'
    assert tokens[1].type == Tokens.EOF


def test_many_number_int():
    tokens = all_tokens('12 345')
    assert tokens[0].type == Tokens.INT
    assert tokens[0].value == '12'
    assert tokens[1].type == Tokens.INT
    assert tokens[1].value == '345'
    assert tokens[2].type == Tokens.EOF


def test_float():
    tokens = all_tokens('12.345')
    assert tokens[0].type == Tokens.FLOAT
    assert tokens[0].value == '12.345'
    assert tokens[1].type == Tokens.EOF


def test_incorect_float():
    with pytest.raises(MqlSyntaxError):
        all_tokens('12.a')


def test_many_floats():
    tokens = all_tokens('1.2 3.4')
    assert tokens[0].type == Tokens.FLOAT
    assert tokens[0].value == '1.2'
    assert tokens[1].type == Tokens.FLOAT
    assert tokens[1].value == '3.4'
    assert tokens[2].type == Tokens.EOF


def test_mix_number():
    tokens = all_tokens('1 2.3')
    assert tokens[0].type == Tokens.INT
    assert tokens[0].value == '1'
    assert tokens[1].type == Tokens.FLOAT
    assert tokens[1].value == '2.3'
    assert tokens[2].type == Tokens.EOF


def test_mix_simple():
    tokens = all_tokens('name 1 2.3')
    assert tokens[0].type == Tokens.IDENTIFIER
    assert tokens[0].value == 'name'
    assert tokens[1].type == Tokens.INT
    assert tokens[1].value == '1'
    assert tokens[2].type == Tokens.FLOAT
    assert tokens[2].value == '2.3'
    assert tokens[3].type == Tokens.EOF


def test_no_closed_string():
    with pytest.raises(MqlSyntaxError):
        all_tokens('"Lore lipsum...')


def test_empty_string():
    tokens = all_tokens('""')
    assert tokens[0].type == Tokens.STRING
    assert tokens[0].value == ""


def test_single_string():
    tokens = all_tokens('"a"')
    assert tokens[0].type == Tokens.STRING
    assert tokens[0].value == "a"


def test_incorect_escape_string():
    tokens = all_tokens('"\\n\\"')
    assert tokens[0].type == Tokens.STRING
    assert tokens[0].value == "\n\""


def test_expression_one_unary():
    tokens = all_tokens('not')
    assert len(tokens) == 2  # + EOF
    unary = tokens[0]
    assert unary.type == Tokens.KEYWORD
    assert unary.value == "not"
    assert unary.start == 0
    assert unary.end == 2


def test_expression_unary_expr():
    tokens = all_tokens('not a')
    assert len(tokens) == 3  # + EOF
    unary = tokens[0]
    assert unary.type == Tokens.KEYWORD
    assert unary.value == "not"
    assert unary.start == 0
    assert unary.end == 2

    token = tokens[1]
    assert token.type == Tokens.IDENTIFIER
    assert token.value == "a"
    assert token.start == 4
    assert token.end == 4


def test_expression_eq():
    tokens = all_tokens('=')
    assert len(tokens) == 2  # + EOF
    token = tokens[0]
    assert token.type == Tokens.EXPRESSION
    assert token.value == "="
    assert token.start == 0
    assert token.end == 0


def test_expression_in():
    tokens = all_tokens('id IN ( 1 ,2, 3 )')
    assert len(tokens) == 10
    token = tokens[0]
    assert token.type == Tokens.IDENTIFIER
    assert token.value == 'id'

    token = tokens[1]
    assert token.type == Tokens.KEYWORD
    assert token.value == 'IN'

    token = tokens[2]
    assert token.type == Tokens.PAREN_LEFT
    assert token.value == '('

    token = tokens[3]
    assert token.type == Tokens.INT
    assert token.value == '1'

    token = tokens[4]
    assert token.type == Tokens.COMA
    assert token.value == ','

    token = tokens[5]
    assert token.type == Tokens.INT
    assert token.value == '2'

    token = tokens[6]
    assert token.type == Tokens.COMA
    assert token.value == ','

    token = tokens[7]
    assert token.type == Tokens.INT
    assert token.value == '3'

    token = tokens[8]
    assert token.type == Tokens.PAREN_RIGHT
    assert token.value == ')'


def test_expression_eq_ids():
    tokens = all_tokens('a = b')
    assert len(tokens) == 4  # + EOF
    token = tokens[0]
    assert token.type == Tokens.IDENTIFIER
    assert token.value == "a"
    assert token.start == 0
    assert token.end == 0

    eq = tokens[1]
    assert eq.type == Tokens.EXPRESSION
    assert eq.value == '='
    assert eq.start == 2
    assert eq.end == 2

    token = tokens[2]
    assert token.type == Tokens.IDENTIFIER
    assert token.value == "b"
    assert token.start == 4
    assert token.end == 4


def test_expression_ge():
    tokens = all_tokens('>=')
    assert len(tokens) == 2  # + EOF
    token = tokens[0]
    assert token.type == Tokens.EXPRESSION
    assert token.value == ">="
    assert token.start == 0
    assert token.end == 1


def test_expression_le():
    tokens = all_tokens('<=')
    assert len(tokens) == 2  # + EOF
    token = tokens[0]
    assert token.type == Tokens.EXPRESSION
    assert token.value == "<="
    assert token.start == 0
    assert token.end == 1


def test_expression_ne():
    tokens = all_tokens('!=')
    assert len(tokens) == 2  # + EOF
    token = tokens[0]
    assert token.type == Tokens.EXPRESSION
    assert token.value == "!="
    assert token.start == 0
    assert token.end == 1


def test_expression_one_lt():
    match_tokens('<', (
        (Tokens.EXPRESSION,  '<', 0, 0),
        (Tokens.EOF,         '',  1, 1)
    ))


def test_expression_lt():
    match_tokens('a < b', (
        (Tokens.IDENTIFIER,  'a', 0, 0),
        (Tokens.EXPRESSION,  '<', 2, 2),
        (Tokens.IDENTIFIER,  'b', 4, 4),
        (Tokens.EOF,         '',  5, 5)
    ))


def test_expression_gt():
    match_tokens('>', (
        (Tokens.EXPRESSION,  '>', 0, 0),
        (Tokens.EOF,         '',  1, 1)
    ))


def test_expression_invalid():
    with pytest.raises(MqlSyntaxError):
        all_tokens('!')


def test_invalid():
    with pytest.raises(MqlSyntaxError):
        all_tokens('{}')


def test_method():
    match_tokens('sum(id)', (
        (Tokens.IDENTIFIER,  'sum', 0, 2),
        (Tokens.PAREN_LEFT,  '(',   3, 3),
        (Tokens.IDENTIFIER,  'id',  4, 5),
        (Tokens.PAREN_RIGHT, ')',   6, 6),
        (Tokens.EOF,         '',    7, 7)
    ))


def match_tokens(query, matches):
    tokens = all_tokens(query)
    assert len(tokens) == len(matches)
    for match in matches:
        token = tokens.pop(0)
        assert token.type == match[0]
        assert token.value == match[1]
        assert token.start == match[2]
        assert token.end == match[3]
