class MidasException(Exception):
    """Exception to indicate a general API error."""


class MidasCommunicationException(MidasException):
    """Exception to indicate a communication error."""


class MidasAuthenticationException(MidasException):
    """Exception to indicate an authentication error."""


class MidasRegistrationException(MidasException):
    """Exception to indicate a registration error."""


class MidasDecodingException(MidasException):
    """Exception to indicate a failure to decode data retreived from the server. Please raise an issue!"""
