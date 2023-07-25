# Standard Library
import logging
from collections.abc import MutableMapping, MutableSequence
from functools import singledispatch

# Django
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import Http404

# Third Parties
from rest_framework import exceptions as rest_exceptions
from rest_framework.exceptions import APIException
from rest_framework.fields import get_error_detail
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger("main_logger")


def _extract_exception_details(raised_exception) -> str | list | dict | None:
    """Extracts error details from expected to be raised non-DRF exception
    classes since they store error messages in different attributes.

    Expected exceptions:
    - django.core.exceptions.ValidationError
    - django.core.exceptions.Exception
    """

    if isinstance(raised_exception, ValidationError):
        # ValidationError has a different structure from all other exception classes
        # and DRF has already a util function to parse it `get_error_detail`
        return get_error_detail(raised_exception)
    else:
        # all other exceptions that we expect has only the `args` tuple
        return getattr(raised_exception, "args", None)


@singledispatch
def _format_exception_details(exception_details) -> dict:
    """Formats extracted exception details into a single unified response
    format. Where `message` has the exception message, and `extra` might hold
    the field name or any other info related.

    Error Structure:
    - `{"error": {"message": str, "extra": str}}`
    """

    message, extra = exception_details, None
    parsed_error = {"error": {"message": message, "extra": extra}}
    return parsed_error


@_format_exception_details.register
def _(exception_details: MutableMapping) -> dict:
    """Formats nested dicts or dicts with different keys into the same
    format."""
    message = exception_details.get("message") or exception_details.get("detail")
    extra = exception_details.get("extra")

    # get latest depth level in case of nested dicts
    if not message and not extra:
        extra, message = exception_details.popitem()
        while isinstance(message, dict):
            extra, message = message.popitem()

    message = message[0] if isinstance(message, list) else message

    parsed_error = {"error": {"message": message, "extra": extra}}
    return parsed_error


@_format_exception_details.register(tuple)
@_format_exception_details.register(MutableSequence)
def _(exception_details: tuple | MutableSequence) -> dict:
    """Gets the first item only because we return one exception at a time.

    Sometimes the raised error list have empty dict items, so we get the
    first non empty one.
    """
    exception_details = next(detail for detail in exception_details if detail)
    return _format_exception_details(exception_details)


def _transform_into_drf_exception(exc):
    """Transforms expected raised exceptions from APIs into DRF ones.

    Any exception class raised from the APIs should be added below.
    Otherwise, a general 500 server will be returned.
    """
    exception_details = _extract_exception_details(exc)
    if isinstance(exc, ValidationError):
        return rest_exceptions.ValidationError(exception_details)
    elif isinstance(exc, ObjectDoesNotExist | Http404):
        return rest_exceptions.NotFound(exception_details)
    elif exc.__class__ == Exception:
        return rest_exceptions.APIException(exception_details)
    return None


def _log_exception(exc, context):
    request_method_path = f"{context['request'].method} {context['request'].path}"
    view_class = context["view"].__class__
    exception_info = repr(exc)
    logger.warning(f"{exception_info} (view: {view_class}, request: {request_method_path})", exc_info=True)


def custom_exception_handler(exc, context):
    """Transforms some expected Django exceptions into DRF ones.

    If the exception could be handled, it formats its content into a
    unified structure. Otherwise, it returns None which will cause a 500
    error to be raised.
    """
    _log_exception(exc, context)
    if not isinstance(exc, APIException):
        exc = _transform_into_drf_exception(exc)
    response = drf_exception_handler(exc, context)
    if response is None:
        return response
    response.data = _format_exception_details(response.data)
    return response
