import logging
from http import HTTPStatus
from logging import Logger

import tornado
import tornado.escape as escape


logger: Logger = logging.getLogger(__name__)  # noqa: F821
logger.setLevel(logging.DEBUG)


def get_request_attr_value(handler, arg):
    try:
        param = handler.get_argument(arg)
        if not param:
            logger.error(f"Invalid argument '{arg}', cannot be blank.")
            raise tornado.web.HTTPError(
                status_code=HTTPStatus.BAD_REQUEST,
                reason=f"Invalid argument '{arg}', cannot be blank.",
            )
        return param
    except tornado.web.MissingArgumentError as e:
        logger.error(f"Missing argument '{arg}'.", exc_info=e)
        raise tornado.web.HTTPError(
            status_code=HTTPStatus.BAD_REQUEST, reason=f"Missing argument '{arg}'."
        ) from e


def get_body_value(handler):
    try:
        if not handler.request.body:
            raise ValueError()
        return escape.json_decode(handler.request.body)
    except ValueError as e:
        logger.error("Invalid body.", exc_info=e)
        raise tornado.web.HTTPError(
            status_code=HTTPStatus.BAD_REQUEST, reason=f"Invalid POST body: {e}"
        ) from e