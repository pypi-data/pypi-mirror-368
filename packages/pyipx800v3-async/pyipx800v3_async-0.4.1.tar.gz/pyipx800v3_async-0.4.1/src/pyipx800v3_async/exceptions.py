"""Exceptions for IPX800."""


class Ipx800v3CannotConnectError(Exception):
    """Exception to indicate an error in connection."""


class Ipx800v3InvalidAuthError(Exception):
    """Exception to indicate an error in authentication."""


class Ipx800v3RequestError(Exception):
    """Exception to indicate an error with an API request."""