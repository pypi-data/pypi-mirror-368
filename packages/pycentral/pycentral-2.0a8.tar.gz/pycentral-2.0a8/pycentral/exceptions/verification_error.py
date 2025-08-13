# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from pycentral.exceptions.pycentral_error import PycentralError


class VerificationError(PycentralError):
    """
    PYCENTRAL Verification Error Exception.
    """

    base_msg = "VERIFICATION ERROR"

    def __init__(self, *args):
        self.message = None
        self.module = None
        if args:
            self.module = args[0]
            if len(args) > 1:
                self.message = ", ".join(str(a) for a in args[1:])

    def __str__(self):
        msg_parts = [self.base_msg]
        if self.module:
            if self.message:
                msg_parts.append("{0} DETAIL".format(self.module))
                msg_parts.append(self.message)
            else:
                msg_parts.append(self.module)
        msg = ": ".join(msg_parts)
        return repr(msg)
