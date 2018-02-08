from mql.common import ast


def create_ast_tree():
    '''
    SELECT id, num as number, name
    FROM a.b
    WHERE (id = 1 OR id = 2 ) AND (num > 1 OR num < 10)
    ORDER BY id, num DESC
    LIMIT 10
    OFFSET 5
    '''
    return ast.SelectStatement(
        results=[
            ast.SelectIdentifier('id'),
            ast.SelectIdentifier('num', 'number'),
            ast.SelectIdentifier('name')
        ],
        table=ast.SelectTable('a.b'),
        where=ast.SelectWhere(ast.BinaryExpression(
            operator='AND',
            left=ast.BinaryExpression(
                operator='OR',
                left=ast.BinaryExpression(
                    operator='=',
                    left=ast.Identifier('id'),
                    right=ast.IntNumber(1),
                ),
                right=ast.BinaryExpression(
                    operator='=',
                    left=ast.Identifier('id'),
                    right=ast.IntNumber(2),
                )
            ),
            right=ast.BinaryExpression(
                operator='OR',
                left=ast.BinaryExpression(
                    operator='>',
                    left=ast.Identifier('num'),
                    right=ast.IntNumber(1),
                ),
                right=ast.BinaryExpression(
                    operator='<',
                    left=ast.Identifier('num'),
                    right=ast.IntNumber(10),
                )
            )
        )),
        order=ast.SelectOrder(items=[
            ast.SelectOrderItem('id'),
            ast.SelectOrderItem('num', 'DESC'),
        ]),
        limit=ast.SelectLimit(10),
        offset=ast.SelectOffset(5)
    )


class VisitMixin:
    RESULTS = [
        ('SelectStatement',),
        ('SelectIdentifier', 'id', ''),
        ('SelectIdentifier', 'num', 'number'),
        ('SelectIdentifier', 'name', ''),
        ('SelectTable', 'a.b'),
        ('SelectWhere', ),
        ('BinaryExpression', 'AND'),
        ('BinaryExpression', 'OR'),
        ('BinaryExpression', '='),
        ('Identifier', 'id'),
        ('IntNumber', 1),
        ('BinaryExpression', '='),
        ('Identifier', 'id'),
        ('IntNumber', 2),
        ('BinaryExpression', 'OR'),
        ('BinaryExpression', '>'),
        ('Identifier', 'num'),
        ('IntNumber', 1),
        ('BinaryExpression', '<'),
        ('Identifier', 'num'),
        ('IntNumber', 10),
        ('SelectOrder',),
        ('SelectOrderItem', 'id', 'ASC'),
        ('SelectOrderItem', 'num', 'DESC'),
        ('SelectLimit', 10),
        ('SelectOffset', 5)
    ]

    def __init__(self):
        self.visited = []

    def visit_SelectStatement(self, node, *args):
        self.visited.append(('SelectStatement',))

    def visit_SelectIdentifier(self, node, *args):
        self.visited.append(('SelectIdentifier', node.name, node.alias))

    def visit_SelectTable(self, node, *args):
        self.visited.append(('SelectTable', node.name))

    def visit_SelectWhere(self, node, *args):
        self.visited.append(('SelectWhere',))

    def visit_BinaryExpression(self, node, *args):
        self.visited.append(('BinaryExpression', node.operator))

    def visit_BinaryExpression(self, node, *args):
        self.visited.append(('BinaryExpression', node.operator))

    def visit_Identifier(self, node, *args):
        self.visited.append(('Identifier', node.name))

    def visit_IntNumber(self, node, *args):
        self.visited.append(('IntNumber', node.value))

    def visit_SelectOrder(self, node, *args):
        self.visited.append(('SelectOrder',))

    def visit_SelectOrderItem(self, node, *args):
        self.visited.append(('SelectOrderItem', node.name, node.direction))

    def visit_SelectLimit(self, node, *args):
        self.visited.append(('SelectLimit', node.value))

    def visit_SelectOffset(self, node, *args):
        self.visited.append(('SelectOffset', node.value))
