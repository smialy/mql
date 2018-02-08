from . import ast


__all__ = ['NodeVisitor', 'NodeTransformer', 'NodeWalker', 'NodeWalkers', 'walk']


def iter_fields(node):
    for field_name in node.__slots__:
        yield field_name, getattr(node, field_name)


class NodeVisitor:
    def visit(self, node):
        if node:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            return visitor(node)

    def generic_visit(self, node):
        for field_name, value in iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.Node):
                        self.visit(item)
            elif isinstance(value, ast.Node):
                self.visit(value)


class NodeTransformer(NodeVisitor):
    def generic_visit(self, node):
        for field_name, old_value in iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, ast.Node):
                        value = self.visit(value)
                        if value is None:
                            continue
                        elif not isinstance(value, ast.Node):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, ast.Node):
                new_node = self.visit(old_value)
                setattr(node, field_name, new_node)
        return node


def walk(root, walker):
    visit = walker.visit

    def _walk(node, parent, path):
        visit(node, parent, path)
        for name, child in iter_fields(node):
            if isinstance(child, list):
                for item in child:
                    if isinstance(item, ast.Node):
                        _walk(item, node, path + [node])
            else:
                if isinstance(child, ast.Node):
                    _walk(child, node, path + [node])
    _walk(root, None, [])


class NodeWalker:
    def visit(self, node, parent, path):
        method = 'visit_' + node.__class__.__name__
        if hasattr(self, method):
            visitor = getattr(self, method)
            return visitor(node, parent, path)


class NodeWalkers:
    def __init__(self, walkers):
        self._walkers = walkers

    def visit(self, node, parent, path):
        for walker in self._walkers:
            result = walker.visit(node, parent, path)
            if result:
                return result
