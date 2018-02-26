from mql.common import ast
from mql.common.errors import MqlSyntaxError

from .consts import STATEMENTS_KEYWORDS, OPERATORS
from .lexer import Tokens, Lexer, type_to_name


def parse(source):
    parser = Parser(source)
    return parse_statement(parser)


def expression(source):
    parser = Parser(source)
    return parse_expression(parser)


class Parser:
    def __init__(self, source):
        self.source = source
        self.lexer = Lexer(source)
        self.current = None
        self.lookahead = None
        self.next()

    def raise_unexpected_token_type(self, token, types):
        msg = 'Expected token type: "{}" but found: "{}({})"'.format(
            '","'.join(map(type_to_name, types)),
            type_to_name(token.type), token.value
        )
        raise MqlSyntaxError(msg, self.source, token.start)

    def raise_unexpected_token(self, token):
        msg = 'Unexpected token {}'.format(token)
        raise MqlSyntaxError(msg, self.source, token.start)

    def next(self):
        self.current = self.lookahead
        self.lookahead = self.lexer.next()
        return self.current

    def skip_one(self, type_):
        if self.current:
            return False
        if self.current.type == type_:
            self.next()
            return True
        return False

    def skip_all(self, type_):
        if not self.current:
            return False

        while self.current.type == type_:
            self.next()
        return True

    def expect(self, value):
        token = self.next()
        if token.value == value:
            return token
        self.raise_unexpected_token(token)

    def expect_types(self, *types):
        token = self.next()
        if token.type in types:
            return token

        self.raise_unexpected_token_type(token, types)

    def expect_type(self, type_):
        token = self.next()
        if token.type == type_:
            return token
        self.raise_unexpected_token_type(token, (type_,))

    def expect_identifier(self):
        return self.expect_type(Tokens.IDENTIFIER)

    def expect_keyword(self, value):
        token = self.expect_type(Tokens.KEYWORD)
        if token.value.upper() == value.upper():
            return token

        self.raise_unexpected_token(token)

    def match(self, value):
        '''Return true if next token has match the specified value'''
        return self.lookahead.value == value

    def match_type(self, type_):
        '''Return true if next token has match the specified type'''
        return self.lookahead.type == type_

    def match_types(self, *types):
        '''Return true if next token has match the specified type'''
        return self.lookahead.type in types

    def match_identifier(self):
        '''Return true if next token is identifier '''
        return self.lookahead.type == Tokens.IDENTIFIER

    def match_keyword(self, value):
        '''Return true if next token is identifier with specified value'''
        return self.lookahead.type == Tokens.KEYWORD \
            and self.lookahead.value.upper() == value.upper()


def get_operator_precedence(token):
    return OPERATORS[token.value.upper()]


def parse_expression(parser):
    left = parse_expression_token(parser)
    if not left:
        raise MqlSyntaxError('Empty expression', parser.source)
    if not parser.match_type(Tokens.EXPRESSION) and not parser.match_keyword('AND') and not parser.match_keyword('OR'):
        return left
    operator = parser.next()
    right = parse_expression_token_right(parser)
    if not right:
        msg = 'Expected expression after {}'.format(operator)
        raise MqlSyntaxError(msg, parser.source)
    stack = [left, operator, right];

    while parser.match_type(Tokens.EXPRESSION) or parser.match_keyword('AND') or parser.match_keyword('OR'):
        operator = parser.next()
        precedence = get_operator_precedence(operator)
        while len(stack) > 2 and precedence <= get_operator_precedence(stack[-2]):
            right = stack.pop()
            op = stack.pop()
            left = stack.pop()
            stack.append(create_binary_expression(op.value, left, right))
        node = parse_expression_token_right(parser)
        if not node:
            msg = 'Expected expression after {}'.format(operator)
            raise MqlSyntaxError(msg, parser.source)
        stack.append(operator)
        stack.append(node)
    i = len(stack) - 1
    node = stack[i]
    while i > 1:  # roll up
        operator = stack[i - 1]
        left = stack[i - 2]
        node = create_binary_expression(operator.value, left, node)
        i -= 2
    return node


def create_binary_expression(operator, left, right):
    if operator in ['AND', 'OR']:
        return ast.LogicalExpression(operator, left, right)
    return ast.BinaryExpression(operator, left, right)


def parse_expression_token(parser):
    if parser.match_type(Tokens.PAREN_LEFT):
        return parse_expression_group(parser)
    if parser.match_type(Tokens.IDENTIFIER):
        return ast.Identifier(parser.next().value)


def parse_expression_token_right(parser):
    if parser.match_type(Tokens.PAREN_LEFT):
        return parse_expression_group(parser)

    value = parse_value(parser)
    if value:
        return value

    if parser.match_type(Tokens.IDENTIFIER):
        return ast.Identifier(parser.next().value)

    if parser.match_keyword('NOT'):
        parser.next()
        return ast.UnaryExpression(parse_expression_token(parser))
    raise MqlSyntaxError('Not found right expression', parser.source)


def parse_value(parser):
    if parser.match_type(Tokens.QUESTION):
        parser.next()
        return ast.Placeholder()

    if parser.match_type(Tokens.INT):
        return ast.IntNumber(parser.next().value)

    if parser.match_type(Tokens.STRING):
        return ast.String(parser.next().value)

    return None

def parse_expression_group(parser):
    parser.expect_type(Tokens.PAREN_LEFT)
    node = parse_expression(parser)
    parser.expect_type(Tokens.PAREN_RIGHT)
    return node


def parse_expression_identifier(parser):
    token = parser.expect_types(Tokens.IDENTIFIER)
    return ast.Identifier(token.value)



def parse_expression_in(parser):
    parser.expect_keyword('IN')
    parser.expect_type(Tokens.PAREN_LEFT)
    items = []
    while parser.match_types(Tokens.QUESTION, Tokens.INT):
        if parser.match_type(Tokens.QUESTION):
            parser.next()
            items.append(ast.Placeholder())
        elif parser.match_type(Tokens.INT):
            token = parser.next()
            items.append(ast.IntNumber(token.value))
        if parser.match_type(Tokens.COMA):
            parser.next()

    parser.expect_type(Tokens.PAREN_RIGHT)
    return ast.InExpression(items)


def parse_statement(parser):
    token = parser.expect_type(Tokens.KEYWORD)
    name = token.value.upper()
    if name not in STATEMENTS_KEYWORDS:
        msg = 'Expect statements {}, got: {}'.format(STATEMENTS_KEYWORDS, name)
        raise MqlSyntaxError(msg, parser.source, token.start)

    if name == 'SELECT':
        return parse_select(parser)
    if name == 'INSERT':
        return parse_insert(parser)
    if name == 'UPDATE':
        return parse_update(parser)
    if name == 'DELETE':
        return parse_delete(parser)
    if name == 'SHOW':
        return parse_show(parser)
    raise MqlSyntaxError('Unknow statement: {}'.format(name), parser.source, token.start)


def parse_show(parser):
    token = parser.expect_type(Tokens.KEYWORD)
    name = token.value.upper()
    if name == 'SOURCES':
        return ast.ShowSourcesStatement()
    if name == 'SOURCE':
        value = parse_identifier_name(parser)
        return ast.ShowSourceStatement(ast.Source(value))
    msg = 'Unknow show statement: {}'.format(name)
    raise MqlSyntaxError(msg, parser.source, token.start)

def parse_select(parser):
    stmt = ast.SelectStatement()
    stmt.results = parse_select_results(parser)
    stmt.table = parse_select_table(parser)
    if not parser.match_type(Tokens.EOF):
        if parser.match_keyword('WHERE'):
            stmt.where = parse_select_where(parser)
    if not parser.match_type(Tokens.EOF):
        if parser.match_keyword('ORDER'):
            stmt.order = parse_select_order(parser)
    if not parser.match_type(Tokens.EOF):
        if parser.match_keyword('LIMIT'):
            stmt.limit = parse_select_limit(parser)
    if not parser.match_type(Tokens.EOF):
        if parser.match_keyword('OFFSET'):
            stmt.offset = parse_select_offset(parser)
    parser.expect_type(Tokens.EOF)
    return stmt


def parse_identifier_name(parser):
    names = [parser.expect_identifier().value]
    while parser.match_type(Tokens.DOT):
        parser.next()
        names.append(parser.expect_identifier().value)
    return '.'.join(names)


def parse_select_results(parser):
    results = [parse_select_identifier(parser)]
    while parser.match_type(Tokens.COMA):
        parser.next()
        results.append(parse_select_identifier(parser))
    return results


def parse_select_identifier(parser):
    if parser.match_type(Tokens.WILDCARD):
        token = parser.next()
        return ast.SelectIdentifier(token.value)

    name = parse_identifier_name(parser)
    alias = ''
    if parser.match_keyword('AS'):
        parser.next()
        alias = parser.expect_identifier().value
    return ast.SelectIdentifier(name, alias)


def parse_select_table(parser):
    parser.expect_keyword('FROM')
    name = parse_identifier_name(parser)
    return ast.SelectTable(name)


def parse_select_where(parser):
    parser.expect_keyword('WHERE')
    return ast.SelectWhere(parse_expression(parser))


def parse_select_order(parser):
    parser.expect_keyword('ORDER')
    if parser.match_keyword('BY'):
        parser.next()

    order = ast.SelectOrder()
    order.add(parse_select_order_item(parser))

    while parser.match_type(Tokens.COMA):
        parser.next()
        order.add(parse_select_order_item(parser))
    return order


def parse_select_order_item(parser):
    token = parser.expect_identifier()
    direction = None
    if parser.match_keyword('ASC') or parser.match_keyword('DESC'):
        direction = parser.next().value
    return ast.SelectOrderItem(token.value, direction)


def parse_select_limit(parser):
    parser.expect_keyword('LIMIT')
    value = parser.expect_type(Tokens.INT).value
    return ast.SelectLimit(value)


def parse_select_offset(parser):
    parser.expect_keyword('OFFSET')
    value = parser.expect_type(Tokens.INT).value
    return ast.SelectOffset(value)


def parse_insert(parser):
    parser.expect_keyword('INTO')
    table = ast.Table(parser.expect_identifier().value)
    ids = parse_insert_results(parser)
    values = parse_insert_values(parser)
    if len(ids) != len(values):
        msg = 'Incorect holders number. filed:{} holders:{}'.format(ids, values)
        raise MqlSyntaxError(msg, parser.source, parser.current.start)
    parser.expect_type(Tokens.EOF)
    return ast.InsertStatement(table, ids, values)


def parse_insert_results(parser):
    parser.expect_type(Tokens.PAREN_LEFT)
    ids = [ast.Identifier(parser.expect_identifier().value)]
    while parser.match_type(Tokens.COMA):
        parser.next()
        ids.append(ast.Identifier(parser.expect_identifier().value))
    parser.expect_type(Tokens.PAREN_RIGHT)
    return ids


def parse_insert_values(parser):
    parser.expect_keyword('VALUES')
    parser.expect_type(Tokens.PAREN_LEFT)
    values = []
    parser.expect_type(Tokens.QUESTION)
    values.append(ast.Placeholder())
    while parser.match_type(Tokens.COMA):
        parser.next()
        parser.expect_type(Tokens.QUESTION)
        values.append(ast.Placeholder())
    parser.expect_type(Tokens.PAREN_RIGHT)
    return values


def parse_update(parser):
    table_name = ast.UpdateTable(parse_identifier_name(parser))
    columns = parse_update_columns(parser)
    parser.expect_keyword('WHERE')
    where = parse_expression(parser)
    parser.expect_type(Tokens.EOF)
    return ast.UpdateStatement(table_name, columns, where)

def parse_update_columns(parser):
    parser.expect_keyword('SET')
    columns = []
    while True:
        name = parser.expect_identifier().value
        parser.expect('=')
        value = parse_value(parser)
        if not value:
            raise MqlSyntaxError('Incorrect update column value', parser.source)

        columns.append(ast.UpdateColumn(name, value))
        if not parser.match_type(Tokens.COMA):
            break
        parser.next()
    return columns

def parse_delete(parser):
    parser.expect_keyword('FROM')
    table_name = ast.DeleteTable(parse_identifier_name(parser))
    parser.expect_keyword('WHERE')
    where = parse_expression(parser)
    parser.expect_type(Tokens.EOF)
    return ast.DeleteStatement(table_name, where)
