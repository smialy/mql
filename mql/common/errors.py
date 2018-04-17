class MqlError(Exception):
    pass


class NotFoundSourceError(MqlError):
    pass


class MqlEngineError(MqlError):
    __slots__ = ('message', 'secure')

    def __init__(self, message, secure=False):
        super().__init__(message)
        self.secure = secure


class MqlSyntaxError(MqlError):
    __slots__ = ('message', 'source', 'position')

    def __init__(self, message, source=None, position=None):
        super().__init__(message)
        self.source = source
        self.position = position


def format_error(error, short=True):
    if isinstance(error, MqlSyntaxError):
        if short:
            return 'Syntax error'
    return str(error)
