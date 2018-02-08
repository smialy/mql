from .select_unique_results import SelectUniqueResultsRule
from .select_from import SelectFromRule
default_rules = [
    SelectFromRule,
    SelectUniqueResultsRule
]

__all__ = [
    'SelectFromRule',
    'SelectUniqueResultsRule'
]
