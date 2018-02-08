from mql.common import traverse
from mql.common import ast
from .base import create_ast_tree, VisitMixin


def test_visitor():
    visited = []

    class TestVisitor(traverse.NodeVisitor, VisitMixin):
        def visit_SelectStatement(self, node):
            super().visit_SelectStatement(node);
            for id in node.results:
                self.visit(id)
            self.visit(node.table)
            self.visit(node.where)
            self.visit(node.order)
            self.visit(node.limit)
            self.visit(node.offset)

        def visit_SelectWhere(self, node):
            super().visit_SelectWhere(node)
            self.visit(node.condition)

        def visit_BinaryExpression(self, node):
            super().visit_BinaryExpression(node)
            self.visit(node.left)
            self.visit(node.right)

        def visit_BinaryExpression(self, node):
            super().visit_BinaryExpression(node)
            self.visit(node.left)
            self.visit(node.right)

        def visit_SelectOrder(self, node):
            super().visit_SelectOrder(node)
            for item in node.items:
                self.visit(item)

    visitor = TestVisitor()
    ast_tree = create_ast_tree()
    visitor.visit(ast_tree)
    assert visitor.visited == VisitMixin.RESULTS


def test_walker():
    visited = []
    class Walker(traverse.NodeWalker, VisitMixin):
        pass

    ast_tree = create_ast_tree()
    walker = Walker()
    traverse.walk(ast_tree, walker)
    assert walker.visited == VisitMixin.RESULTS
