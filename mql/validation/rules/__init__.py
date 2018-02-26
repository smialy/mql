from .select_unique_results import SelectUniqueResultsRule


default_rules = [
    SelectUniqueResultsRule
]

__all__ = [
    'SelectFromRule',
    'SelectUniqueResultsRule'
]
