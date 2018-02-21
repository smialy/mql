from mql.common.traverse import walk, NodeWalkers
from .rules import default_rules


def validate(exe_context, rules=None):
    rules = rules or default_rules
    context = ValidatorContext(sources, ast)
    walkers = [rule(context) for rule in rules]
    walk(ast, NodeWalkers(walkers))
    return context.get_errors()


class ValidatorContext(object):
    def __init__(self, sources, ast):
        self.sources = sources
        self.ast = ast
        self._errors = []

    def add_error(self, error):
        self._errors.append(error)

    def get_errors(self):
        return self._errors[:]
