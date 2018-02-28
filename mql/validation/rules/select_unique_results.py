from .base import BaseRule


class SelectUniqueResultsRule(BaseRule):
    def __init__(self, context):
        super().__init__(context)
        self._names = []

    def visit_SelectIdentifier(self, node, *args):
        name = node.alias if node.alias else node.name
        if name in self._names:
            self._error(name)
        else:
            self._names.append(name)


    def _error(self, name):
        self.context.add_error(
            'There can be only one the same name: {}'.format(name)
        )
