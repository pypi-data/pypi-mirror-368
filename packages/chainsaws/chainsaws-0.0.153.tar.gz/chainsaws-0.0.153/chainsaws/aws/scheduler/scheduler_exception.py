class SchedulerException(Exception):
    """Base exception for scheduler operations."""


class ScheduleNotFoundException(SchedulerException):
    """Schedule not found."""


class InvalidScheduleExpressionError(SchedulerException):
    """Invalid schedule expression."""


class ScheduleConflictError(SchedulerException):
    """Schedule conflict detected."""


class ScheduleValidationError(SchedulerException):
    """Schedule validation failed."""


class ScheduleGroupNotFoundException(SchedulerException):
    """Schedule group not found."""
