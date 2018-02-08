from mql.common.traverse import NodeWalker


class BaseRule(NodeWalker):
    def __init__(self, context):
        self.context = context
