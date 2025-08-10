class LambdaException(Exception):
    """Lambda exception."""
    pass


class LambdaMemorySizeException(LambdaException):
    """Lambda memory size exception."""
    pass


class LambdaCreateFunctionException(LambdaException, ValueError):
    """Lambda code exception."""
    pass
