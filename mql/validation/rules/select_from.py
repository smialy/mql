from .base import BaseRule


class SelectFromRule(BaseRule):
    def visit_SelectStatement(self, node, *args):
        if not node.table:
            self.context.add_error('Missing keyword: FROM')
