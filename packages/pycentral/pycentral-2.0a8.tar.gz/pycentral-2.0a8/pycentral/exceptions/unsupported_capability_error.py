# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from pycentral.exceptions.pycentral_error import PycentralError


class UnsupportedCapabilityError(PycentralError):
    """
    Exception class for an PYCENTRAL Unsupported Capability Error.
    """

    base_msg = "UNSUPPORTED CAPABILITY"
