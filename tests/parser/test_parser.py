import pytest
from mql.common import ast
from mql.common.errors import MqlSyntaxError
from mql.parser.parser import parse, expression


def test_empty_expression():
    with pytest.raises(MqlSyntaxError):
        expression('')


def test_select_table_dots():
    stmt = parse('SELECT * FROM foo.bar.boo')
    assert isinstance(stmt.table, ast.SelectTable)
    assert stmt.table.name == 'foo.bar.boo'


def test_incorrect_describe_scheme():
    with pytest.raises(MqlSyntaxError):
        parse('SOURCES')

    with pytest.raises(MqlSyntaxError):
        parse('SOURCE')

    with pytest.raises(MqlSyntaxError):
        parse('SHOW SOURCE')


def test_select_empty_from():
    with pytest.raises(MqlSyntaxError):
        parse('SELECT * FROM')


def test_select_table_dots_bugs():
    with pytest.raises(MqlSyntaxError):
        parse('SELECT * FROM a.')

    with pytest.raises(MqlSyntaxError):
        parse('SELECT * FROM a.b.')

    with pytest.raises(MqlSyntaxError):
        parse('SELECT * FROM .b.')

    with pytest.raises(MqlSyntaxError):
        parse('SELECT * FROM .')


def test_empty_select():
    with pytest.raises(MqlSyntaxError):
        parse('SELECT')

    with pytest.raises(MqlSyntaxError):
        parse('SELECT foo')


def test_incorect_order():
    with pytest.raises(MqlSyntaxError):
        parse('SELECT * FROM foo ORDER BY name WHERE id = ?')


def test_empty_where():
    with pytest.raises(MqlSyntaxError):
        parse('SELECT * FROM foo WHERE')


def test_incorrect_order():
    with pytest.raises(MqlSyntaxError):
        parse('SELECT * FROM foo ORDER')

    with pytest.raises(MqlSyntaxError):
        parse('SELECT * FROM foo ORDER BY')


def test_incorrect_limit():
    with pytest.raises(MqlSyntaxError):
        parse('SELECT * FROM LIMIT')

    with pytest.raises(MqlSyntaxError):
        parse('SELECT * FROM a LIMIT a')

    with pytest.raises(MqlSyntaxError):
        parse('SELECT * FROM a LIMIT 1,1')

def test_incorrect_OFFSET():
    with pytest.raises(MqlSyntaxError):
        parse('SELECT * FROM OFFSET')

    with pytest.raises(MqlSyntaxError):
        parse('SELECT * FROM OFFSET a')

    with pytest.raises(MqlSyntaxError):
        parse('SELECT * FROM OFFSET ?')


def test_expression_band():
    expr = expression('a & b')
    assert isinstance(expr, ast.BinaryExpression)
    assert expr.operator == '&'
    assert expr.left.name == 'a'
    assert expr.right.name == 'b'

def test_expression_band2():
    expr = expression('(a & b) = c')
    assert isinstance(expr, ast.BinaryExpression)
    assert expr.operator == '='
    assert expr.right.name == 'c'
    assert isinstance(expr.left, ast.BinaryExpression)
    assert expr.left.operator == '&'
    assert expr.left.left.name == 'a'
    assert expr.left.right.name == 'b'


def test_expression_band3():
    expr = expression('a & b = c')
    assert isinstance(expr, ast.BinaryExpression)
    assert expr.operator == '='
    assert expr.right.name == 'c'
    assert isinstance(expr.left, ast.BinaryExpression)
    assert expr.left.operator == '&'
    assert expr.left.left.name == 'a'
    assert expr.left.right.name == 'b'


def test_expression_one_eq_space():
    expr = expression('a = b')
    assert isinstance(expr, ast.BinaryExpression)
    assert expr.operator == '='
    assert expr.left.name == 'a'
    assert expr.right.name == 'b'

def test_expression_one_eq():
    expr = expression('a=b')
    assert isinstance(expr, ast.BinaryExpression)
    assert expr.operator == '='
    assert expr.left.name == 'a'
    assert expr.right.name == 'b'


def test_expression_one_gt_space():
    expr = expression('a > b')
    assert isinstance(expr, ast.BinaryExpression)
    assert expr.operator == '>'
    assert expr.left.name == 'a'
    assert expr.right.name == 'b'


def test_expression_one_gt():
    expr = expression('a>b')
    assert isinstance(expr, ast.BinaryExpression)
    assert expr.operator == '>'
    assert expr.left.name == 'a'
    assert expr.right.name == 'b'


def test_expression_one_lt():
    expr = expression('a < b')
    assert isinstance(expr, ast.BinaryExpression)
    assert expr.operator == '<'
    assert expr.left.name == 'a'
    assert expr.right.name == 'b'


def test_expression_one_le():
    expr = expression('a <= b')
    assert isinstance(expr, ast.BinaryExpression)
    assert expr.operator == '<='
    assert expr.left.name == 'a'
    assert expr.right.name == 'b'


def test_expression_one_ge():
    expr = expression('a >= b')
    assert isinstance(expr, ast.BinaryExpression)
    assert expr.operator == '>='
    assert expr.left.name == 'a'
    assert expr.right.name == 'b'


def test_expression_one_ne():
    expr = expression('a != b')
    assert isinstance(expr, ast.BinaryExpression)
    assert expr.operator == '!='
    assert expr.left.name == 'a'
    assert expr.right.name == 'b'


def test_expression_one_placeholder():
    expr = expression('a = ?')
    assert isinstance(expr, ast.BinaryExpression)
    assert expr.operator == '='
    assert isinstance(expr.left, ast.Identifier)
    assert expr.left.name == 'a'
    assert isinstance(expr.right, ast.Placeholder)


def test_expression_one_int():
    expr = expression('a = 1')
    assert isinstance(expr, ast.BinaryExpression)
    assert expr.operator == '='
    assert isinstance(expr.left, ast.Identifier)
    assert expr.left.name == 'a'
    assert isinstance(expr.right, ast.IntNumber)
    assert expr.right.value == 1


def test_expression_equal_string():
    expr = expression('a = "test"')
    assert isinstance(expr, ast.BinaryExpression)
    assert expr.operator == '='
    assert isinstance(expr.left, ast.Identifier)
    assert expr.left.name == 'a'
    assert isinstance(expr.right, ast.String)
    assert expr.right.value == "test"


def test_expression_many_1():
    expr = expression('a = b AND c = d OR e = f')
    assert isinstance(expr, ast.LogicalExpression)
    assert expr.operator == 'OR'

    assert isinstance(expr.left, ast.LogicalExpression)
    assert expr.left.operator == 'AND'
    assert isinstance(expr.right, ast.BinaryExpression)
    assert expr.right.operator == '='


def test_expression_many_2():
    expr = expression('a = b OR b = c AND d = e')
    assert isinstance(expr, ast.LogicalExpression)
    assert expr.operator == 'OR'
    assert isinstance(expr.left, ast.BinaryExpression)
    assert isinstance(expr.right, ast.LogicalExpression)
    assert expr.right.operator == 'AND'


def test_expression_paren_simple():
    expr = expression('(a = b)')
    assert isinstance(expr, ast.BinaryExpression)
    assert expr.operator == '='
    assert isinstance(expr.left, ast.Identifier)
    assert isinstance(expr.right, ast.Identifier)


def test_expression_paren_left():
    with pytest.raises(MqlSyntaxError):
        expression('(a = b')


def test_expression_paren_right():  # its looks as bug but it doesn't
    expr = expression('a = b)')
    assert isinstance(expr, ast.BinaryExpression)
    assert expr.operator == '='
    assert isinstance(expr.left, ast.Identifier)
    assert isinstance(expr.right, ast.Identifier)


def test_expression_many_3():
    expr = expression('(((a = b) OR b = c) AND d = e)')
    assert isinstance(expr, ast.LogicalExpression)
    assert expr.operator == 'AND'
    assert isinstance(expr.left, ast.LogicalExpression)
    assert expr.left.operator == 'OR'
    assert isinstance(expr.right, ast.BinaryExpression)
    assert expr.right.operator == '='


def test_expression_many_4():
    expr = expression('(a = b OR (b = c OR c = d)) AND d = e')
    assert isinstance(expr, ast.LogicalExpression)
    assert expr.operator == 'AND'
    assert isinstance(expr.left, ast.LogicalExpression)
    assert expr.left.operator == 'OR'
    assert isinstance(expr.left.left, ast.BinaryExpression)
    assert isinstance(expr.left.right, ast.LogicalExpression)
    assert expr.left.right.operator == 'OR'
    assert isinstance(expr.right, ast.BinaryExpression)


def test_empty():
    with pytest.raises(MqlSyntaxError):
        parse('')


def test_incorect():
    with pytest.raises(MqlSyntaxError):
        parse('test')


def test_or():
    with pytest.raises(MqlSyntaxError):
        expression('OR')


def test_and():
    with pytest.raises(MqlSyntaxError):
        expression('AND')


def test_expression_logic_incorrect_1():
    with pytest.raises(MqlSyntaxError):
        expression('a = b AND')


def test_expression_logic_incorrect_2():
    with pytest.raises(MqlSyntaxError):
        expr = expression('a = b OR')


def test_expression_logic_incorrect_4():
    with pytest.raises(MqlSyntaxError):
        expr = expression('a = b OR b = c AND')


def test_expression_logic_incorrect_5():
    with pytest.raises(MqlSyntaxError):
        expr = expression('a = b OR b = c OR')


def test_expression_logic_incorrect_5():
    with pytest.raises(MqlSyntaxError):
        expr = expression('a = b OR b = c OR AND')


def test_select_one_char():
    stmt = parse('SELECT a FROM foo')
    assert len(stmt.results) == 1

    identifier = stmt.results[0]
    assert isinstance(identifier, ast.SelectIdentifier)
    assert identifier.name == 'a'


def test_select_one_name():
    stmt = parse('SELECT name FROM foo')
    assert len(stmt.results) == 1

    identifier = stmt.results[0]
    assert isinstance(identifier, ast.SelectIdentifier)
    assert identifier.name == 'name'


def test_select_one_name_dot():
    stmt = parse('SELECT a.b.c FROM foo')
    assert len(stmt.results) == 1
    identifier = stmt.results[0]
    assert isinstance(identifier, ast.SelectIdentifier)
    assert identifier.name == 'a.b.c'


def test_select_many_names():
    stmt = parse('SELECT foo, bar, baz FROM foo')
    assert len(stmt.results) == 3

    id1 = stmt.results[0]
    assert isinstance(id1, ast.SelectIdentifier)
    assert id1.name == 'foo'

    id2 = stmt.results[1]
    assert isinstance(id1, ast.SelectIdentifier)
    assert id2.name == 'bar'

    id3 = stmt.results[2]
    assert isinstance(id1, ast.SelectIdentifier)
    assert id3.name == 'baz'


def test_select_many_names_dot():
    stmt = parse('SELECT a.b.c, b.c.d, c.d.e FROM foo')
    assert len(stmt.results) == 3

    id1 = stmt.results[0]
    assert isinstance(id1, ast.SelectIdentifier)
    assert id1.name == 'a.b.c'

    id2 = stmt.results[1]
    assert isinstance(id1, ast.SelectIdentifier)
    assert id2.name == 'b.c.d'

    id3 = stmt.results[2]
    assert isinstance(id1, ast.SelectIdentifier)
    assert id3.name == 'c.d.e'


def test_select_identifier_as():
    stmt = parse('SELECT foo as f, bar as b FROM foo')
    assert len(stmt.results) == 2

    id1 = stmt.results[0]
    assert isinstance(id1, ast.SelectIdentifier)
    assert id1.name == 'foo'
    assert id1.alias == 'f'
    id2 = stmt.results[1]
    assert isinstance(id2, ast.SelectIdentifier)
    assert id2.name == 'bar'
    assert id2.alias == 'b'


def test_select_identifier_as_dot():
    stmt = parse('SELECT a.b.c as f, bar as b FROM foo')
    assert len(stmt.results) == 2

    id1 = stmt.results[0]
    assert isinstance(id1, ast.SelectIdentifier)
    assert id1.name == 'a.b.c'
    assert id1.alias == 'f'
    id2 = stmt.results[1]
    assert isinstance(id2, ast.SelectIdentifier)
    assert id2.name == 'bar'
    assert id2.alias == 'b'


def test_widlcard():
    stmt = parse('SELECT *, name as n, foo as f FROM foo')
    assert len(stmt.results) == 3

    id1 = stmt.results[0]
    assert isinstance(id1, ast.SelectIdentifier)
    assert id1.is_wildcard()
    assert id1.name == '*'
    assert id1.alias == ''

    id2 = stmt.results[1]
    assert isinstance(id2, ast.SelectIdentifier)
    assert not id2.is_wildcard()
    assert id2.name == 'name'
    assert id2.alias == 'n'

    id3 = stmt.results[2]
    assert isinstance(id3, ast.SelectIdentifier)
    assert not id3.is_wildcard()
    assert id3.name == 'foo'
    assert id3.alias == 'f'


def test_select_table():
    stmt = parse('SELECT * FROM foo')
    assert isinstance(stmt.table, ast.SelectTable)
    assert stmt.table.name == 'foo'


def test_select_order_one_default():
    stmt = parse('SELECT * FROM foo ORDER BY name')
    assert isinstance(stmt.order, ast.SelectOrder)
    assert len(stmt.order.items) == 1
    assert stmt.order.items[0].name == 'name'
    assert stmt.order.items[0].direction == 'ASC'


def test_select_order_one_asc():
    stmt = parse('SELECT * FROM foo ORDER BY name ASC')
    assert isinstance(stmt.order, ast.SelectOrder)
    assert len(stmt.order.items) == 1
    assert stmt.order.items[0].name == 'name'
    assert stmt.order.items[0].direction == 'ASC'


def test_select_order_one_desc():
    stmt = parse('SELECT * FROM foo ORDER BY name DESC')
    assert isinstance(stmt.order, ast.SelectOrder)
    assert len(stmt.order.items) == 1
    assert stmt.order.items[0].name == 'name'
    assert stmt.order.items[0].direction == 'DESC'


def test_select_order_many():
    stmt = parse('SELECT * FROM foo ORDER BY a, b DESC, c ASC, d')
    assert isinstance(stmt.order, ast.SelectOrder)
    assert len(stmt.order.items) == 4
    assert stmt.order.items[0].name == 'a'
    assert stmt.order.items[0].direction == 'ASC'
    assert stmt.order.items[1].name == 'b'
    assert stmt.order.items[1].direction == 'DESC'
    assert stmt.order.items[2].name == 'c'
    assert stmt.order.items[2].direction == 'ASC'
    assert stmt.order.items[3].name == 'd'
    assert stmt.order.items[3].direction == 'ASC'


def test_select_limit():
    stmt = parse('SELECT * FROM foo LIMIT 5')
    assert isinstance(stmt.limit, ast.SelectLimit)
    assert stmt.limit.value == 5


def test_select_offset():
    stmt = parse('SELECT * FROM foo OFFSET 10')
    assert isinstance(stmt.offset, ast.SelectOffset)
    assert stmt.offset.value == 10


def test_select_limit_offset():
    stmt = parse('SELECT * FROM foo LIMIT 5 OFFSET 10')
    assert isinstance(stmt.limit, ast.SelectLimit)
    assert stmt.limit.value == 5
    assert isinstance(stmt.offset, ast.SelectOffset)
    assert stmt.offset.value == 10


def test_select_where():
    stmt = parse('SELECT * FROM foo WHERE id = 1')
    assert isinstance(stmt, ast.SelectStatement)
    assert isinstance(stmt.table, ast.Table)
    assert len(stmt.results) == 1
    assert isinstance(stmt.results[0], ast.SelectIdentifier)
    assert stmt.table.name == 'foo'
    assert stmt.results[0].is_wildcard()
    assert isinstance(stmt.where.condition, ast.BinaryExpression)
    assert isinstance(stmt.where.condition.left, ast.Identifier)
    assert stmt.where.condition.left.name == 'id'
    assert stmt.where.condition.operator == '='
    assert isinstance(stmt.where.condition.right, ast.IntNumber)
    assert stmt.where.condition.right.value == 1


def test_select_where_order():
    stmt = parse('SELECT * FROM foo WHERE id = 1 ORDER by name')
    assert isinstance(stmt, ast.SelectStatement)
    assert isinstance(stmt.table, ast.Table)
    assert len(stmt.results) == 1
    assert isinstance(stmt.results[0], ast.SelectIdentifier)
    assert stmt.table.name == 'foo'
    assert stmt.results[0].is_wildcard()
    assert isinstance(stmt.where.condition, ast.BinaryExpression)
    assert isinstance(stmt.where.condition.left, ast.Identifier)
    assert stmt.where.condition.left.name == 'id'
    assert stmt.where.condition.operator == '='
    assert isinstance(stmt.where.condition.right, ast.IntNumber)
    assert stmt.where.condition.right.value == 1
    assert isinstance(stmt.order, ast.SelectOrder)
    assert len(stmt.order.items) == 1
    assert isinstance(stmt.order.items[0], ast.SelectOrderItem)
    assert stmt.order.items[0].name == 'name'
    assert stmt.order.items[0].direction == 'ASC'



def test_insert_simple():
    stmt = parse('INSERT INTO foo.bar (a,b,c) VALUES (1, "a", ?)')
    assert isinstance(stmt, ast.InsertStatement)
    assert isinstance(stmt.table, ast.InsertTable)
    assert len(stmt.results) == 3
    assert len(stmt.values) == 3
    assert isinstance(stmt.results[0], ast.Identifier)
    assert isinstance(stmt.results[1], ast.Identifier)
    assert isinstance(stmt.results[1], ast.Identifier)
    assert isinstance(stmt.values[0], ast.IntNumber)
    assert isinstance(stmt.values[1], ast.String)
    assert isinstance(stmt.values[2], ast.Placeholder)
    assert stmt.table.name == 'foo.bar'
    assert stmt.results[0].name == 'a'
    assert stmt.results[1].name == 'b'


def test_insert():
    stmt = parse('INSERT INTO foo.bar (a,b,c) VALUES (?, ?, ?)')
    assert isinstance(stmt, ast.InsertStatement)
    assert isinstance(stmt.table, ast.InsertTable)
    assert len(stmt.results) == 3
    assert len(stmt.values) == 3
    assert isinstance(stmt.results[0], ast.Identifier)
    assert isinstance(stmt.results[1], ast.Identifier)
    assert isinstance(stmt.results[2], ast.Identifier)
    assert isinstance(stmt.values[0], ast.Placeholder)
    assert isinstance(stmt.values[1], ast.Placeholder)
    assert isinstance(stmt.values[2], ast.Placeholder)
    assert stmt.table.name == 'foo.bar'
    assert stmt.results[0].name == 'a'
    assert stmt.results[1].name == 'b'
    assert stmt.results[2].name == 'c'


def test_insert_error0():
    with pytest.raises(MqlSyntaxError):
        parse('INSERT INTO foo (a) VALUES (a)')


def test_insert_error1():
    with pytest.raises(MqlSyntaxError):
        parse('INSERT INTO foo () VALUES ()')


def test_insert_error2():
    with pytest.raises(MqlSyntaxError):
        parse('INSERT INTO foo (a) VALUES ()')


def test_insert_error3():
    with pytest.raises(MqlSyntaxError):
        parse('INSERT INTO foo () VALUES (?)')


def test_insert_error4():
    with pytest.raises(MqlSyntaxError):
        parse('INSERT INTO foo (a)')


def test_insert_error5():
    with pytest.raises(MqlSyntaxError):
        parse('INSERT INTO foo (a) VALUES')


def test_insert_error_paren1():
    with pytest.raises(MqlSyntaxError):
        parse('INSERT INTO foo a) VALUES (?)')


def test_insert_error_paren2():
    with pytest.raises(MqlSyntaxError):
        parse('INSERT INTO foo (a VALUES (?)')


def test_insert_error_paren3():
    with pytest.raises(MqlSyntaxError):
        parse('INSERT INTO foo (a) VALUES ?)')


def test_insert_error_paren1():
    with pytest.raises(MqlSyntaxError):
        parse('INSERT INTO foo (a) VALUES (?')


def test_insert_error_coma1():
    with pytest.raises(MqlSyntaxError):
        parse('INSERT INTO foo (a,) VALUES (?)')


def test_insert_error_size1():
    with pytest.raises(MqlSyntaxError):
        parse('INSERT INTO foo (a, b) VALUES (?)')


def test_insert_error_size2():
    with pytest.raises(MqlSyntaxError):
        parse('INSERT INTO foo (a) VALUES (?, ?)')


def test_update_simple():
    stmt = parse('UPDATE foo.bar SET a=1 WHERE id=2')
    assert isinstance(stmt, ast.UpdateStatement)
    assert isinstance(stmt.table, ast.Table)
    assert isinstance(stmt.where, ast.BinaryExpression)
    assert len(stmt.columns) == 1
    assert stmt.table.name == 'foo.bar'

def test_update():
    stmt = parse('UPDATE foo.bar SET a=1, b="test", c=? WHERE id=?')
    assert isinstance(stmt, ast.UpdateStatement)
    assert isinstance(stmt.table, ast.Table)
    assert isinstance(stmt.where, ast.BinaryExpression)
    assert len(stmt.columns) == 3
    assert stmt.table.name == 'foo.bar'
    assert isinstance(stmt.columns[0], ast.UpdateColumn)
    assert isinstance(stmt.columns[1], ast.UpdateColumn)
    assert isinstance(stmt.columns[2], ast.UpdateColumn)
    assert isinstance(stmt.columns[0].value, ast.IntNumber)
    assert isinstance(stmt.columns[1].value, ast.String)
    assert isinstance(stmt.columns[2].value, ast.Placeholder)
    assert stmt.columns[0].name == 'a'
    assert stmt.columns[1].name == 'b'
    assert stmt.columns[2].name == 'c'
    assert stmt.columns[0].value.value == 1
    assert stmt.columns[1].value.value == 'test'


def test_delete():
    stmt = parse('DELETE FROM foo.bar WHERE id=1')
    assert isinstance(stmt, ast.DeleteStatement)
    assert isinstance(stmt.table, ast.Table)
    assert isinstance(stmt.where, ast.BinaryExpression)
    assert stmt.table.name == 'foo.bar'


def test_show_sources():
    stmt = parse('SHOW SOURCES')
    assert isinstance(stmt, ast.ShowSourcesStatement)


def test_show_tables():
    stmt = parse('SHOW SOURCE foo')
    assert isinstance(stmt, ast.ShowSourceStatement)
    assert isinstance(stmt.source, ast.Source)
    assert stmt.source.name == 'foo'

    stmt = parse('SHOW SOURCE foo.bar')
    assert isinstance(stmt, ast.ShowSourceStatement)
    assert isinstance(stmt.source, ast.Source)
    assert stmt.source.name == 'foo.bar'
