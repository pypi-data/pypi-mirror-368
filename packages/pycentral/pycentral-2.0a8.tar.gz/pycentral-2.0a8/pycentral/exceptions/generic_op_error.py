# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from pycentral.exceptions.pycentral_error import PycentralError


class GenericOperationError(PycentralError):
    """
    PYCENTRAL Generic Operation Error Exception.
    """

    base_msg = "GENERIC OPERATION ERROR"

    def __init__(self, *args):
        self.message = None
        self.response_code = None
        self.extra_info = None
        if args:
            self.message = args[0]
            if len(args) >= 2:
                self.response_code = args[1]
            if len(args) > 2:
                self.extra_info = ", ".join(str(a) for a in args[2:])

    def __str__(self):
        msg_parts = [self.base_msg]
        if self.message:
            msg_parts.append(str(self.message))
        if self.response_code:
            msg_parts.append("Code")
            msg_parts.append(str(self.response_code))
        if self.extra_info:
            msg_parts.append("on Module")
            msg_parts.append(str(self.extra_info))
        msg = ": ".join(msg_parts)
        return repr(msg)
