from mql.common.traverse import walk, NodeWalkers
from .rules import default_rules


def validate(sources, ast_document, params, rules=None):
    rules = rules or default_rules
    context = ValidatorContext(sources, ast_document, params)
    walkers = [rule(context) for rule in rules]
    walk(ast_document, NodeWalkers(walkers))
    return context.get_errors()


class ValidatorContext(object):
    def __init__(self, sources, ast_document, params):
        self.sources = sources
        self.ast_document = ast_document
        self.params = params
        self._errors = []

    def add_error(self, error):
        self._errors.append(error)

    def get_errors(self):
        return self._errors[:]
