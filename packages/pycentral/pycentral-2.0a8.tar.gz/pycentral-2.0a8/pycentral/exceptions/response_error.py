# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from pycentral.exceptions.pycentral_error import PycentralError


class ResponseError(PycentralError):
    """
    Exception class for a PYCENTRAL Response Error.
    """

    base_msg = "RESPONSE ERROR"

    def __init__(self, *args):
        self.message = None
        self.response = None
        if args:
            self.response = args[0]
            if len(args) > 1:
                self.message = ", ".join(str(a) for a in args[1:])
        else:
            self.message = None

    def __str__(self):
        msg_parts = [self.base_msg]
        if self.message:
            msg_parts.append(str(self.message))
        if self.response:
            msg_parts.append("Response")
            msg_parts.append(str(self.response))
        msg = ": ".join(msg_parts)
        return repr(msg)
