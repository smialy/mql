from mql.validation import validate
from mql.parser.parser import parse


def test_uniqe_fields():
    ast = parse('SELECT id, id FROM foo')
    errors = validate(None, ast)
    assert len(errors) == 1
