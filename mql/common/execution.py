import logging
from traceback import format_exception


logger = logging.getLogger(__name__)


class ExecuteResult:

    __slots__ = ('data', 'errors', 'encoded')

    def __init__(self, data=None, errors=None, encoded=False):
        self.data = data
        self.errors = errors
        self.encoded = encoded

    def has_errors(self):
        return bool(self.errors)


class ExecutionContext:

    __slots__ = ('errors', 'sources', 'ast_document', 'params', 'query')

    def __init__(self, sources, ast_document, params, query):
        self.errors = []
        self.sources = sources
        self.ast_document = ast_document
        self.params = params
        self.query = query

    def report_error(self, error):
        exception = format_exception(
            type(error), error, getattr(error, 'stack', None)
        )
        logger.error(''.join(exception))
        self.errors.append(error)
